const electron = require('electron')
const { remote } = electron
const { ipcRenderer } = electron
const { DropdownMenu } = require("app/components/dropdownmenu")
const { AccordionView } = require("ui/dom/accordion")
const { Question } = require("ui/dialog/question.js")
const { AudioOutputSettings } = require("app/dialogs/audio_setup")
const { SessionSaveDialog } = require('app/dialogs/session_save_dialog')
const { TagEditDialog } = require('app/dialogs/tag_edit_dialog')
const { AudioOutputDetector } = require('webaudio/detect')
const { TrackListAreaController } = require('app/views/track_list_area')
const { QueueAreaController } = require('app/views/queue_list_area')
const { SessionsListView } = require('app/views/sidebar_sessions_list')
const { PlaylistListView } = require('app/views/sidebar_playlist_list')
const { PymusicAppController } = require('app/controller')
const { TrackAdder } = require("app/dialogs/track_add_dialog")
const { MainPlayerView } = require("app/views/main_player_view")
const { PrecuePlayerView } = require("app/views/sidebar_precue_player")

SV = new AccordionView("sidebar")

SV.on("refresh-sessions", () => {
    SE.displayModel(MDB.sessions)
})


SV.on("refresh-playlists", () => {
    PL.displayModel(MDB.playlists)
})

SV.on("add-playlist", () => {
    PL.beginAdd()
})


const AppController = new PymusicAppController()

MDB = AppController.library
// view = new TrackEditorView()
// view.init()

var available_outputs = {}

async function getAudioOutputDevices() {
    let output_dict = {}
    let audio_outputs = await (new AudioOutputDetector().detectAutioOutputs())
    audio_outputs.forEach((o) => {
        output_dict[o.deviceId] = o.label
    })
    return output_dict
}

function setupAudioOutputs(audio_setup, available_devices) {
    if (available_devices[audio_setup.main_master]) {
        AppController.setMasterOutputDeviceId(audio_setup.main_master)
    } else {
        AppController.setMasterOutputDeviceId("null")
    }

    if (available_devices[audio_setup.main_headset]) {
        AppController.setHeadsetOutputDeviceId(audio_setup.main_headset)
    } else {
        AppController.setHeadsetOutputDeviceId("null")
    }

    if (available_devices[audio_setup.prelisten]) {
        AppController.setPrelistenOutputDeviceId(audio_setup.prelisten)
        // view.setOutputDeviceId(audio_setup.prelisten)
    } else {
        AppController.setPrelistenOutputDeviceId("null")
        // view.setOutputDeviceId("null")
    }
}

MDB.getAudioDevices().then(async (devices) => {
    let audio_outputs = await getAudioOutputDevices()
    let audio_setup = await MDB.getAudioSetup()
    setupAudioOutputs(audio_setup, audio_outputs)
})

var T = setInterval(async () => {
    let audio_outputs = await getAudioOutputDevices()
    let saved_audio_devices = await MDB.getAudioDevices()
    let audio_setup = await MDB.getAudioSetup()
    let update = false
    Object.keys(audio_outputs).forEach((deviceId) => {
        if (!(saved_audio_devices[deviceId])) {
            saved_audio_devices[deviceId] = audio_outputs[deviceId]
            update = true
        }
    })
    update && (await MDB.state.d.update({_id: "settings"}, {$set: {
        "audio_devices": saved_audio_devices
    }}))
    setupAudioOutputs(audio_setup, audio_outputs)

}, 1000)

Q = new QueueAreaController(MDB)
Q.hide_playlist_editor()
Q.queue_view.displayModel("QUEUE", MDB.queue)


T = new TrackListAreaController(MDB)

PL = new PlaylistListView({
    list: 'queue-elements-body'
})
PL.displayModel(MDB.playlists)
PL.on("row-click", (playlistId) => {
    T.display_playlist(playlistId)
})

SE = new SessionsListView({
    list: 'queue-elements-body'
})
SE.displayModel(MDB.sessions)
SE.on("row-click", (sessionId) => {
    T.display_session(sessionId)
})

M = new MainPlayerView(MDB.tracks)
M.set_controller(AppController)
M.init()

P = new PrecuePlayerView(MDB.tracks)
P.set_controller(AppController)

AppController.on("main:queue-started",
    () => {
        B = document.getElementById("queue-start-button")
        B.innerHTML = "<i class=\"fa fa-stop\"></i>"
        B.style.backgroundColor = "#660000"
        document.getElementById("main-player-overlay").style.display="none"
    }
)

AppController.on("main:queue-stopped",
    () => {
        B = document.getElementById("queue-start-button")
        B.innerHTML = "<i class=\"fa fa-play\"></i>"
        B.style.backgroundColor = "rgb(25,25,25)"
        document.getElementById("main-player-overlay").style.display="block"
    }
)

AppController.on("main:queue-finished",
    () => {
        B = document.getElementById("queue-start-button")
        B.innerHTML = "<i class=\"fa fa-play\"></i>"
        B.style.backgroundColor = "rgb(25,25,25)"
        document.getElementById("main-player-overlay").style.display="block"
    }
)

AppController.on('prelisten:playback-started', () => {
    SV.open_panel(3)
})

AppController.on("main:next-track-countdown", (time) => {
    let M = document.getElementById("main-player-track-title")
    if (time > 1) {
        M.innerHTML = `Next track will start in ${time} seconds`
    } else if (time == 1) {
        M.innerHTML = `Next track will start in 1 second`
    } else {
        M.innerHTML = `Next track will start now`

    }
})

window.addEventListener("load", (event) => {
    let h = document.getElementById("track-list-elements-header")
    let ta = document.getElementById("main-track-list-scroller")
    let tl = document.getElementById("main-track-list")
    list_height = (tl.clientHeight - h.clientHeight) - 5
    ta.style.maxHeight = list_height + "px";
    T._listview.fitHeaderColumns()
})

window.addEventListener("resize", (event) => {
    let h = document.getElementById("track-list-elements-header")
    let ta = document.getElementById("main-track-list-scroller")
    let tl = document.getElementById("main-track-list")
    list_height = (tl.clientHeight - h.clientHeight) - 5
    ta.style.maxHeight = list_height + "px";
    T._listview.fitHeaderColumns()
})

var settingsMenuDOM = document.getElementById("settings-menu")
var settingsMenu = new DropdownMenu()
settingsMenuDOM.appendChild(settingsMenu.domElement)

settingsMenu.addItem(`<i class="fa fa-plus"></i>&nbsp;&nbsp;Add tracks`, () => {
    remote.dialog.showOpenDialog({ properties: ['openFile', 'multiSelections'] }, (files) => {
        if (files != undefined) {
            let x = new TrackAdder(files, MDB)
        }
    })
})
settingsMenu.addSeparator()
settingsMenu.addItem(`<i class="fa fa-refresh"></i>&nbsp;&nbsp;Audio setup`, () => {
    let d = new AudioOutputSettings({
        library: MDB,
        appController: AppController,
        masterOutputChange: (deviceId) => {
            AppController.setMasterOutputDeviceId(deviceId)
            MDB.state.d.update({_id: "settings"}, {
                $set: {'audio_setup.main_master': deviceId}
            })
        },
        masterHeadphoneChange: (deviceId) => {
            AppController.setHeadsetOutputDeviceId(deviceId)
            MDB.state.d.update({_id: "settings"}, {
                $set: {'audio_setup.main_headset': deviceId}
            })
        },
        prelistenOutputChange: (deviceId) => {
            AppController.setPrelistenOutputDeviceId(deviceId)
            MDB.state.d.update({_id: "settings"}, {
                $set: {'audio_setup.prelisten': deviceId}
            })

        }
    })
    d.open()
})
settingsMenu.addSeparator()
settingsMenu.addItem(`<i class="fa fa-tags"></i>&nbsp;&nbsp;Edit tags`, async () => {
    let d = new TagEditDialog(MDB)
    d.open()
    await d.init()
})
settingsMenu.addSeparator()
settingsMenu.addItem(`<i class="fa fa-stop"></i>&nbsp;&nbsp;Stop queue now`, () => {
    AppController.stopQueue()
})
settingsMenu.addItem(`<i class="fa fa-ellipsis-h"></i>&nbsp;&nbsp;Skip current track`, () => {
    AppController.skipToNextTrack()
})
settingsMenu.addSeparator()
settingsMenu.addItem(`<i class="fa fa-save"></i>&nbsp;&nbsp;Save current session`, () => {
    let dialog = new SessionSaveDialog({
        confirmAction: async () => {
            let name = dialog.name_input.domElement.value
        
            if (name != "") {
                await MDB.saveCurrentSession(name)
            }
            dialog.close()
        },
        dismissAction: () => {
            dialog.close()
        }
    })
    dialog.open()
})
settingsMenu.addItem(`<i class="fa fa-minus"></i>&nbsp;&nbsp;Discard current session`, () => {
    let q = new Question({
        title: "Discard current session",
        question: "Discard the current session? this operation cannot be undone",
        confirmText: "yes",
        dismissText: 'no',
        confirmAction: () => {
            MDB.discardCurrentSession()
            q.close()
        },
        dismissAction: () => {
            q.close()
        },
    })
    q.open()
})
settingsMenu.addSeparator()
settingsMenu.addItem(`<i class="fa fa-desktop"></i>&nbsp;&nbsp;Toggle fullscreen`, () => {
    let window = electron.remote.getCurrentWindow();
    window.setFullScreen(!(window.isFullScreen()));
})
settingsMenu.addItem(`<i class="fa fa-bug"></i>&nbsp;&nbsp;Open developper tools`, () => {
    let window = electron.remote.getCurrentWindow();
    window.openDevTools();
})
settingsMenu.addSeparator()
settingsMenu.addItem(`<i class="fa fa-power-off"></i>&nbsp;&nbsp;Quit`, () => {
    ipcRenderer.send("quit-pymusic")
})

function refresh_sessions(x) {
    console.log("refresh_sessions", x)
}

function checkTime(i) {
    return (i < 10) ? "0" + i : i;
}

function startTime() {
    let today = new Date()
    h = checkTime(today.getHours())
    m = checkTime(today.getMinutes())
    s = checkTime(today.getSeconds())
    d = checkTime(today.getDate())
    M = checkTime(today.getMonth()+1)
    Y = today.getFullYear()
    document.getElementById("footer-date").innerHTML = `${Y}-${M}-${d}`
    document.getElementById("footer-time").innerHTML = `${h}:${m}`
    t = setTimeout(function () {
        startTime()
    }, 30000);
}
startTime();

T.display_all_songs()
