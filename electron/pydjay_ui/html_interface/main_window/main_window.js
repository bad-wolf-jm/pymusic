const electron = require('electron')
const { remote } = electron
const { ipcRenderer } = electron
const { DropdownMenu } = require("ui/dom/dropdownmenu")
const { Question } = require("ui/dialog/question.js")
const { AudioOutputSettings } = require("app/dialogs/audio_setup")
const { SessionSaveDialog } = require('app/dialogs/session_save_dialog')
const { TagEditDialog } = require('app/dialogs/tag_edit_dialog')
const { AudioOutputDetector } = require('webaudio/detect')
const { TrackListAreaController } = require('app/views/track_list_area')
const { QueueAreaController } = require('app/views/queue_list_area')
const { LinksList } = require('app/views/sidebar_library_links')
const { SessionsListView } = require('app/views/sidebar_sessions_list')
const { PlaylistListView } = require('app/views/sidebar_playlist_list')
const { PymusicAppController } = require('app/controller')
const { TrackAdder } = require("app/dialogs/track_add_dialog")
const { Sidebar } = require("app/views/sidebar")
const { MainPlayerView } = require("app/views/header_main_player")
const { PrecuePlayerView } = require("app/views/sidebar_precue_player")

const AppController = new PymusicAppController()

MDB = AppController.library

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
    } else {
        AppController.setPrelistenOutputDeviceId("null")
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

M = new MainPlayerView(MDB.tracks)
M.set_controller(AppController)
M.init()

sidebar = new Sidebar(MDB)
document.getElementById("sidebar").appendChild(sidebar.domElement)

window.addEventListener("load", (event) => {
    T._listview.fitHeaderColumns()
    sidebar.adjustHeights()
})

window.addEventListener("resize", (event) => {
    T._listview.fitHeaderColumns()
    sidebar.adjustHeights()
})


function refresh_sessions(x) {

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
