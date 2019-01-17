Sortable              = require("../../../lib/Sortable.js")
WaveSurfer            = require("wavesurfer.js")
var WaveSurferRegions = require('wavesurfer.js/dist/plugin/wavesurfer.regions.min.js');
var path              = require('path');
// const { EventDispatcher } = require("event_dispatcher")
const { MusicDatabase } = require("musicdb/model.js")
// const { PlaylistModel, PlaylistViewModel } = require("musicdb/playlist.js")
const { TrackSetModel } = require("musicdb/track_set.js")
// const { SessionModel } = require("musicdb/session.js")
const { Question } = require("ui/dialog/question.js")
// const {PydjayAudioFilePlayer} = require('audio/audio_player_file.js')
// const {PydjayAudioBufferPlayer} = require('audio/audio_player_buffer.js')


SV = new AccordionView("sidebar")

SV.on("refresh-sessions", () => {
    SE_controller.refresh(() => {})
})


SV.on("refresh-playlists", () => {
    PL_controller.refresh(() => {})
})

SV.on("add-playlist", () => {
    PL.begin_add()

})


MDB = new MusicDatabase("pymusic")
// MDB.queue.init()
// MDB.current_session.init()

DB = undefined //new DataProvider()

view = new TrackEditorView()
view.init()

T_controller  = new TrackListController()
PE_controller = new PlaylistController() //un_model)
Q_controller = new QueueController()
S_controller = undefined //new SessionController()
PL_controller = new PlaylistsController()
PL_controller.setModel(MDB.playlists)
SE_controller = new SessionsController()
SE_controller.setModel(MDB.sessions)

mpc = new PlaybackController(S_controller, Q_controller)
pc  = new PrecueController(S_controller, Q_controller)
vc  = new VolumeController(mpc, pc)

Q_controller.set_model(MDB.queue)


PE = new PlaylistEditView({
    list:       'playlist-edit-elements-body',
    num_tracks: "playlist-edit-number-of-tracks",
    duration:   "playlist-edit-duration"
})
PE.set_controller(PE_controller)

QL = new QueueView({
    list:       'queue-elements-body',
    num_tracks: "queue-number-of-tracks",
    duration:   "queue-duration"
})
QL.set_controller(Q_controller)


Q = new QueueAreaView(QL, PE)
Q.hide_playlist_editor()


T = new TrackListView({
    name:       "main-track-list-name",
    num_tracks: "main-track-list-number-of-tracks",
    duration:   "main-track-list-duration",
    filter:      "filter-track-list"
}, Q_controller, MDB.shortlisted_tracks, MDB.unavailable_tracks)
T.set_controller(T_controller)
MDB.queue.on("content-changed", async () => {
    T.setDimmedRows(await MDB.unavailable.getTrackIds())
})
MDB.current_session.on("content-changed", async () => {
    T.setDimmedRows(await MDB.unavailable.getTrackIds())    
})
MDB.unavailable_tracks.on("content-changed", async () => {
    T.setDimmedRows(await MDB.unavailable.getTrackIds())    
})


PL = new PlaylistsView({
    list: 'queue-elements-body'
})
PL.set_controller(PL_controller)

SE = new SessionsView({
    list: 'queue-elements-body'
})
SE.set_controller(SE_controller)

pc.connectOutputs({headphones:{left:0, right:1}})

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

mpc.on("track-started",
    (log_data) => {
        MDB.state.d.update({_id:"settings"}, {
            "current_track._id": log_data.track_object._id
        })
    }
)

mpc.on("track-finished",
    (log_data) => {
        MDB.current_session.append(log_data.track_object, {
            status: "FINISHED",
            time_start: log_data.start_time, 
            time_end: log_data.end_time
        })
        MDB.tracks.setTrackMetadata(log_data.track_object, {
            "stats.last_played": log_data.start_time,
            "stats.play_count": log_data.track_object.stats.play_count + 1
        })
    }
)

mpc.on("track-stopped",
    (log_data) => {
        MDB.current_session.append(log_data.track_object, {
            status: "STOPPED",
            time_start: log_data.start_time, 
            time_end: log_data.end_time
        })
        MDB.tracks.setTrackMetadata(log_data.track_object, {
            "stats.last_played": log_data.start_time,
            "stats.play_count": log_data.track_object.stats.play_count + 1
        })
    }
)

mpc.on("track-skipped",
    (log_data) => {
        MDB.current_session.append(log_data.track_object, {
            status: "SKIPPED",
            time_start: log_data.start_time, 
            time_end: log_data.end_time
        })
        MDB.tracks.setTrackMetadata(log_data.track_object, {
            "stats.last_played": log_data.start_time,
            "stats.play_count": log_data.track_object.stats.play_count + 1
        })
    }
)

ipcRenderer.on("master-end-of-stream", () => {
    mpc.dispatch("end-of-stream")
})


ipcRenderer.on("master-playback-stopped", () => {
    mpc.dispatch("playback-stopped")
})

ipcRenderer.on("master-playback-paused", () => {
    mpc.dispatch("playback-paused")
})

ipcRenderer.on("master-playback-started", () => {
    mpc.dispatch("playback-started")
})


ipcRenderer.on("master-stream-position", (event, pos) => {
    mpc.dispatch("stream-position", pos)
})


pc.on('playback-started', () => {
    SV.open_panel(3)
})

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
    T.fitHeaderColumns()
})


window.addEventListener("resize", (event) => {
    let h = document.getElementById("track-list-elements-header")
    let ta = document.getElementById("main-track-list-scroller")
    let tl = document.getElementById("main-track-list")
    list_height = (tl.clientHeight - h.clientHeight) - 5
    ta.style.maxHeight = list_height + "px";
    T.fitHeaderColumns()
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

document.getElementById("main-menu-reset-audio").addEventListener('click', () => {
    ipcRenderer.send("reset-audio-system", {})
    pc.reset_audio_context({headphones:{left:0, right:1}})
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

document.getElementById("main-menu-save-session").addEventListener('click', () => {
    document.getElementById("save-session-dialog").showModal();
    document.getElementById("main-menu-dropdown").classList.toggle("show");
})

document.getElementById("session-save").addEventListener('click', async () => {
    let name = document.getElementById("session-name").value
    let location = document.getElementById("session-location").value
    let address = document.getElementById("session-address").value

    if (name != "") {
        await MDB.saveCurrentSession(name, location, address)
    }
    document.getElementById("save-session-dialog").close();
})

document.getElementById("session-save-cancel").addEventListener('click', () => {
    document.getElementById("save-session-dialog").close();
})





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

document.getElementById("main-menu-settings").addEventListener('click', () => {
    document.getElementById("main-menu-dropdown").classList.toggle("show");
})


document.getElementById("main-menu-quit").addEventListener('click', () => {
    document.getElementById("main-menu-dropdown").classList.toggle("show");
    ipcRenderer.send("quit-pymusic")
})

document.getElementById("filter-track-list").addEventListener("keyup", (e) => {
    if ((e.key == "Escape") || (e.key == "Enter")) {
        document.getElementById("filter-track-list").blur()
    }
});

///////////////////////////////////////////////

function refresh_sessions(x) {
    console.log("refresh_sessions", x)
}

async function display_all_songs() {
    T.ignore_unavailable = false
    T.model_order = false
    T.setDimmedRows(await MDB.unavailable.getTrackIds())
    T_controller.set_model("All Songs", MDB.tracks)
}

async function display_current_session() {
    T.ignore_unavailable = true
    T.model_order = true
    T.setDimmedRows(await MDB.unavailable.getTrackIds())
    T_controller.set_model("Current Session", MDB.current_session)
}

async function display_suggestions() {
    T.ignore_unavailable = false
    T.model_order = false
    T.setDimmedRows(await MDB.unavailable.getTrackIds())
    T_controller.set_model("Suggested tracks", MDB.suggested)
}

async function display_short_list() {
    T.ignore_unavailable = false
    T.model_order = false
    T.setDimmedRows(await MDB.unavailable.getTrackIds())
    T_controller.set_model("Short list", MDB.shortlisted_tracks)
}

async function display_unavailable() {
    T.ignore_unavailable = true
    T.model_order = false
    T.setDimmedRows(await MDB.unavailable.getTrackIds())
    T_controller.set_model("Unavailable tracks", MDB.unavailable_tracks)
}

async function display_played_tracks() {
    T.ignore_unavailable = false
    T.model_order = false
    T.setDimmedRows(await MDB.unavailable.getTrackIds())
    T_controller.set_model("Played songs", MDB.played_tracks)
}

async function display_never_played_tracks() {
    T.ignore_unavailable = false
    T.model_order = false
    T.setDimmedRows(await MDB.unavailable.getTrackIds())
    T_controller.set_model("Never Played songs", MDB.never_played_tracks)
}

async function display_session(id) {
    let pl = await MDB.sessions.getObjectById(id)
    let model = new TrackSetModel(MDB, MDB.sessions, id)
    T.ignore_unavailable = false
    T.model_order = true
    T.setDimmedRows(await MDB.unavailable.getTrackIds())
    T_controller.set_model(pl.event, model)
}

async function display_playlist(id) {
    let pl = await MDB.playlists.getObjectById(id)
    let model = new TrackSetModel(MDB, MDB.playlists, id)
    T.ignore_unavailable = false
    T.model_order = false
    T.setDimmedRows(await MDB.unavailable.getTrackIds())
    T_controller.set_model(pl.name, model)
}

ipcRenderer.on('playback-started', (event, arg) => {
    vc.mute_monitor()});


ipcRenderer.on('playback-stopped', (event, arg) => {
    vc.restore_monitor()});


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
    // $$('calendar').define('label', `<span style="color:rgb(200,200,200)">${Y}-${M}-${d}</span> | <b>${h}:${m}</b>`)
    // $$('calendar').refresh()
    t = setTimeout(function () {
        startTime()
    }, 30000);
}
startTime();


display_all_songs()
