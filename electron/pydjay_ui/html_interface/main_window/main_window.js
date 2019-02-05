Sortable              = require("../../../lib/Sortable.js")
WaveSurfer            = require("wavesurfer.js")
var WaveSurferRegions = require('wavesurfer.js/dist/plugin/wavesurfer.regions.min.js');
var path              = require('path');

const { Question } = require("ui/dialog/question.js")
const { AudioOutputSettings } = require("iface/dialogs/audio_setup")
const { MusicDatabase } = require("musicdb/model.js")
const { SessionSaveDialog } = require('iface/dialogs/session_save_dialog')
const { AudioOutputDetector } = require('webaudio/detect')
const { TrackListAreaController } = require('app/views/track_list_area')
const { QueueAreaController } = require('app/views/queue_list_area')
const { SessionsListView } = require('app/views/sidebar_sessions_list')
const { PlaylistListView } = require('app/views/sidebar_playlist_list')
// const { TrackSetModel } = require("musicdb/track_set.js")
// const { ClusteredListView } = require('ui/listview/cluster')
// const { EventDispatcher } = require("event_dispatcher")
// const { PlaylistModel, PlaylistViewModel } = require("musicdb/playlist.js")
// const { SessionModel } = require("musicdb/session.js")
// const { Question } = require("ui/dialog/question.js")
// const {PydjayAudioFilePlayer} = require('audio/audio_player_file.js')
// const {PydjayAudioBufferPlayer} = require('audio/audio_player_buffer.js')


SV = new AccordionView("sidebar")

SV.on("refresh-sessions", () => {
    // SE_controller.refresh(() => {})
})


SV.on("refresh-playlists", () => {
    // PL_controller.refresh(() => {})
})

SV.on("add-playlist", () => {
    PL.begin_add()
})


MDB = new MusicDatabase("pymusic")

// MDB.queue.init()
// MDB.current_session.init()
// DB = undefined //new DataProvider()

view = new TrackEditorView()
view.init()

// T_controller  = new TrackListController()
// PE_controller = new PlaylistController() //un_model)
// Q_controller = new QueueController()
// S_controller = undefined //new SessionController()
// PL_controller = new PlaylistsController()
// PL_controller.setModel(MDB.playlists)
// SE_controller = new SessionsController()
// SE_controller.setModel(MDB.sessions)

// tracks_model              = new TrackListModel()
// unavailable_model         = new UnavailableModel(tracks_model)
// shortlist_model           = new ShortlistModel(tracks_model)
// suggested_model           = new SuggestedModel(tracks_model)
// played_tracks_model       = new PlayedTracksModel(tracks_model)
// never_played_tracks_model = new NeverPlayedTracksModel(tracks_model)
// current_session_model     = new CurrentSessionModel(tracks_model)
// queue_model               = new QueueModel(tracks_model, current_session_model)


// un_model = new UnionModel()
// un_model.addModel("queue", queue_model)
// un_model.addModel("current_session", current_session_model)
// un_model.addModel("unavailable", unavailable_model)

// T_controller              = new TrackListController() //un_model)
// PE_controller             = new PlaylistController() //un_model)
// Q_controller              = new QueueController()
// S_controller              = new SessionController()
// PL_controller             = new PlaylistsController()
// SE_controller             = new SessionsController()

// mpc                       = new PlaybackController( ) //S_controller, Q_controller)
// pc                        = new PrecueController( S_controller, Q_controller)

// Q_controller.set_model(MDB.queue) //queue_model)
// S_controller.set_model(current_session_model)

// ipcRenderer.on("track-modified", (e, id) => {
//     tracks_model.update(id)
// })
mpc = new PlaybackController(undefined, MDB.queue)
pc  = new PrecueController() //S_controller, Q_controller)
// vc  = new VolumeController(mpc, pc)

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
        mpc.setMasterOutputDeviceId(audio_setup.main_master)
    } else {
        mpc.setMasterOutputDeviceId("null")
    }

    if (available_devices[audio_setup.main_headset]) {
        mpc.setHeadsetOutputDeviceId(audio_setup.main_headset)
    } else {
        mpc.setHeadsetOutputDeviceId("null")
    }

    if (available_devices[audio_setup.prelisten]) {
        pc.setOutputDeviceId(audio_setup.prelisten)
        view.setOutputDeviceId(audio_setup.prelisten)
    } else {
        pc.setOutputDeviceId("null")
        view.setOutputDeviceId("null")
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

// Q_controller.set_model(MDB.queue)


// PE = new PlaylistEditView({
//     list:       'playlist-edit-elements-body',
//     num_tracks: "playlist-edit-number-of-tracks",
//     duration:   "playlist-edit-duration"
// })
// PE.set_controller(PE_controller)

// QL = new QueueView({
//     list:       'queue-elements-body',
//     num_tracks: "queue-number-of-tracks",
//     duration:   "queue-duration"
// })
// QL.set_controller(Q_controller)


// Q = new QueueAreaView(QL, PE)


Q = new QueueAreaController(MDB)
Q.hide_playlist_editor()
Q.queue_view.displayModel("QUEUE", MDB.queue)


T = new TrackListAreaController(MDB)

// T = new TrackListView({
//     name:       "main-track-list-name",
//     num_tracks: "main-track-list-number-of-tracks",
//     duration:   "main-track-list-duration",
//     filter:      "filter-track-list"
// }, Q_controller, MDB.shortlisted_tracks, MDB.unavailable_tracks)
// T.set_controller(T_controller)
// MDB.queue.on("content-changed", async () => {
//     T.setDimmedRows(await MDB.unavailable.getTrackIds())
// })
// MDB.current_session.on("content-changed", async () => {
//     T.setDimmedRows(await MDB.unavailable.getTrackIds())    
// })
// MDB.unavailable_tracks.on("content-changed", async () => {
//     T.setDimmedRows(await MDB.unavailable.getTrackIds())    
// })


PL = new PlaylistListView({
    list: 'queue-elements-body'
})
// PL.set_controller(PL_controller)
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
// SE.set_controller(SE_controller)

// pc.connectOutputs({headphones:{left:0, right:1}})

M = new MainPlayerView(MDB.tracks)
M.set_controller(mpc)
M.init()

P = new PrecuePlayerView(MDB.tracks)
P.set_controller(pc)

mpc.on("queue-started",
    () => {
        B = document.getElementById("queue-start-button")
        B.innerHTML = "<i class=\"fa fa-stop\"></i>"
        B.style.backgroundColor = "#660000"
        document.getElementById("main-player-overlay").style.display="none"
    }
)

mpc.on("queue-stopped",
    () => {
        B = document.getElementById("queue-start-button")
        B.innerHTML = "<i class=\"fa fa-play\"></i>"
        B.style.backgroundColor = "rgb(25,25,25)"
        document.getElementById("main-player-overlay").style.display="block"
    }
)

mpc.on("queue-finished",
    () => {
        B = document.getElementById("queue-start-button")
        B.innerHTML = "<i class=\"fa fa-play\"></i>"
        B.style.backgroundColor = "rgb(25,25,25)"
        document.getElementById("main-player-overlay").style.display="block"
    }
)

mpc.on("track-started", async (log_data) => {
    await MDB.state.d.update({_id:"settings"}, {
        $set: {"current_track._id": log_data._id}
    })
})

mpc.on("track-finished", async (log_data) => {
    await MDB.current_session.append(log_data.track_object, {
        status: "FINISHED",
        time_start: log_data.start_time, 
        time_end: log_data.end_time
    })
    await MDB.tracks.setTrackMetadata(log_data.track_object, {
        "stats.last_played": log_data.start_time,
        "stats.play_count": log_data.track_object.stats.play_count + 1
    })
})

mpc.on("track-stopped", async (log_data) => {
    await MDB.current_session.append(log_data.track_object, {
        status: "STOPPED",
        time_start: log_data.start_time, 
        time_end: log_data.end_time
    })
    await MDB.tracks.setTrackMetadata(log_data.track_object, {
        "stats.last_played": log_data.start_time,
        "stats.play_count": log_data.track_object.stats.play_count + 1
    })
})

pc.on('playback-started', () => {
        mpc.muteHeadset()
        SV.open_panel(3)
    }
)

mpc.on("track-skipped", async (log_data) => {
    await MDB.current_session.append(log_data.track_object, {
        status: "SKIPPED",
        time_start: log_data.start_time, 
        time_end: log_data.end_time
    })
    await MDB.tracks.setTrackMetadata(log_data.track_object, {
        "stats.last_played": log_data.start_time,
        "stats.play_count": log_data.track_object.stats.play_count + 1
    })
})

// ipcRenderer.on("master-end-of-stream", () => {
//     mpc.dispatch("end-of-stream")
// })


// ipcRenderer.on("master-playback-stopped", () => {
//     mpc.dispatch("playback-stopped")
// })


// pc.on('playback-stopped', () => {
//     mpc.unmuteHeadset()
// }
// )

pc.on('playback-paused', () => {
    mpc.unmuteHeadset()
})



// mpc.on("queue-stop-requested",
//     () => {
//         B = document.getElementById("queue-start-button")
//         B.innerHTML = "<i class=\"fa fa-close\"></i>"
//         B.style.backgroundColor = "#667700"
//     }
// )

// mpc.on("queue-stop-request-cancelled",
//     () => {
//         let M = document.getElementById("queue-stop-message")
//         M.style.display="none"
//         B = document.getElementById("queue-start-button")
//         B.innerHTML = "<i class=\"fa fa-stop\"></i>"
//         B.style.backgroundColor = "#AA0000"
//     }
//)

mpc.on("next-track-countdown", (time) => {
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

document.getElementById("settings-button").addEventListener('click', () => {
    document.getElementById("main-menu-dropdown").classList.toggle("show");
})

document.getElementById("main-menu-add-track").addEventListener('click', () => {
    remote.dialog.showOpenDialog({ properties: ['openFile', 'multiSelections'] }, (files) => {
        if (files != undefined) {
            let x = new TrackAdder(files, MDB)
        }
    })
    document.getElementById("main-menu-dropdown").classList.toggle("show");
})

document.getElementById("main-menu-audio-setup").addEventListener('click', async () => {
    let d = new AudioOutputSettings({
        library: MDB,
        mainPlayer: mpc,
        prelistenPlayer: pc,
        masterOutputChange: (deviceId) => {
            mpc.setMasterOutputDeviceId(deviceId)
            MDB.state.d.update({_id: "settings"}, {
                $set: {'audio_setup.main_master': deviceId}
            })
        },
        masterHeadphoneChange: (deviceId) => {
            mpc.setHeadsetOutputDeviceId(deviceId)
            MDB.state.d.update({_id: "settings"}, {
                $set: {'audio_setup.main_headset': deviceId}
            })
        },
        prelistenOutputChange: (deviceId) => {
            pc.setOutputDeviceId(deviceId)
            view.setOutputDeviceId(deviceId)
            MDB.state.d.update({_id: "settings"}, {
                $set: {'audio_setup.prelisten': deviceId}
            })

        }
    })
    d.open()
    document.getElementById("main-menu-dropdown").classList.toggle("show");
})



document.getElementById("main-menu-stop-queue-now").addEventListener('click', () => {
    mpc.stop_queue_now()
    document.getElementById("main-menu-dropdown").classList.toggle("show");
})

document.getElementById("main-menu-skip-current-track").addEventListener('click', () => {
    mpc.skip_to_next_track()
    document.getElementById("main-menu-dropdown").classList.toggle("show");
})

document.getElementById("main-menu-save-session").addEventListener('click', async () => {
    let dialog = new SessionSaveDialog({
        confirmAction: async () => {
            let name = dialog.name_input.domElement.value
            //let location = dialog.location_input.domElement.value
            //let address = dialog.address_input.domElement.value
        
            if (name != "") {
                await MDB.saveCurrentSession(name) //, location, address)
            }
    
            dialog.close()
        },
        dismissAction: () => {
            dialog.close()
        }
    })
    dialog.open()
    document.getElementById("main-menu-dropdown").classList.toggle("show");
})

// document.getElementById("session-save").addEventListener('click', async () => {
//     let name = document.getElementById("session-name").value
//     let location = document.getElementById("session-location").value
//     let address = document.getElementById("session-address").value

//     if (name != "") {
//         await MDB.saveCurrentSession(name, location, address)
//     }
//     document.getElementById("save-session-dialog").close();
// })

// document.getElementById("session-save-cancel").addEventListener('click', () => {
//     document.getElementById("save-session-dialog").close();
// })

document.getElementById("main-menu-discard-session").addEventListener('click', () => {
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
    document.getElementById("main-menu-dropdown").classList.toggle("show");
})


document.getElementById("main-menu-quit").addEventListener('click', () => {
    document.getElementById("main-menu-dropdown").classList.toggle("show");
    ipcRenderer.send("quit-pymusic")
})

// document.getElementById("filter-track-list").addEventListener("keyup", (e) => {
//     if ((e.key == "Escape") || (e.key == "Enter")) {
//         document.getElementById("filter-track-list").blur()
//     }
// });

///////////////////////////////////////////////

function refresh_sessions(x) {
    console.log("refresh_sessions", x)
}

// async function display_all_songs() {
//     T.ignore_unavailable = false
//     T.model_order = false
//     T_controller.set_model("All Songs", MDB.tracks)
//     T._listview.setDimmedRows(await MDB.unavailable.getTrackIds())
// }

// async function display_current_session() {
//     T.ignore_unavailable = true
//     T.model_order = true
//     T_controller.set_model("Current Session", MDB.current_session)
//     T._listview.setDimmedRows(await MDB.unavailable.getTrackIds())
// }

// async function display_suggestions() {
//     T.ignore_unavailable = false
//     T.model_order = false
//     T_controller.set_model("Suggested tracks", MDB.suggested)
//     T._listview.setDimmedRows(await MDB.unavailable.getTrackIds())
// }

// async function display_short_list() {
//     T.ignore_unavailable = false
//     T.model_order = false
//     T_controller.set_model("Short list", MDB.shortlisted_tracks)
//     T._listview.setDimmedRows(await MDB.unavailable.getTrackIds())
// }

// async function display_unavailable() {
//     T.ignore_unavailable = true
//     T.model_order = false
//     T_controller.set_model("Unavailable tracks", MDB.unavailable_tracks)
//     T._listview.setDimmedRows(await MDB.unavailable.getTrackIds())
// }

// async function display_played_tracks() {
//     T.ignore_unavailable = false
//     T.model_order = false
//     T_controller.set_model("Played songs", MDB.played_tracks)
//     T._listview.setDimmedRows(await MDB.unavailable.getTrackIds())
// }

// async function display_never_played_tracks() {
//     T.ignore_unavailable = false
//     T.model_order = false
//     T_controller.set_model("Never Played songs", MDB.never_played_tracks)
//     T._listview.setDimmedRows(await MDB.unavailable.getTrackIds())
// }

// async function display_session(id) {
//     let pl = await MDB.sessions.getObjectById(id)
//     let model = new TrackSetModel(MDB, MDB.sessions, id)
//     T.ignore_unavailable = false
//     T.model_order = true
//     T_controller.set_model(pl.event, model)
//     T._listview.setDimmedRows(await MDB.unavailable.getTrackIds())
// }

// async function display_playlist(id) {
//     let pl = await MDB.playlists.getObjectById(id)
//     let model = new TrackSetModel(MDB, MDB.playlists, id)
//     T.ignore_unavailable = false
//     T.model_order = false
//     T_controller.set_model(pl.name, model)
//     T._listview.setDimmedRows(await MDB.unavailable.getTrackIds())
// }

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
