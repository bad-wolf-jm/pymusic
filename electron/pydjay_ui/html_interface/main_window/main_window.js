Sortable              = require("../../../lib/Sortable.js")
WaveSurfer            = require("wavesurfer.js")
var WaveSurferRegions = require('wavesurfer.js/dist/plugin/wavesurfer.regions.min.js');
var path              = require('path');

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


DB = new DataProvider()

tracks_model              = new TrackListModel()
unavailable_model         = new UnavailableModel(tracks_model)
shortlist_model           = new ShortlistModel(tracks_model)
suggested_model           = new SuggestedModel(tracks_model)
played_tracks_model       = new PlayedTracksModel(tracks_model)
never_played_tracks_model = new NeverPlayedTracksModel(tracks_model)
current_session_model     = new CurrentSessionModel(tracks_model)
queue_model               = new QueueModel(tracks_model, current_session_model)


un_model = new UnionModel()
un_model.addModel("queue", queue_model)
un_model.addModel("current_session", current_session_model)
un_model.addModel("unavailable", unavailable_model)

T_controller              = new TrackListController(un_model)
Q_controller              = new QueueController()
S_controller              = new SessionController()
PL_controller             = new PlaylistsController()
SE_controller             = new SessionsController()

mpc                       = new PlaybackController(S_controller, Q_controller)
pc                        = new PrecueController(S_controller, Q_controller)
vc                        = new VolumeController(mpc, pc)

Q_controller.set_model(queue_model)
S_controller.set_model(current_session_model)

ipcRenderer.on("track-modified", (e, id) => {
    //console.log(e, id)
    tracks_model.update(id)
})


Q = new QueueView({
    list:       'queue-elements-body',
    num_tracks: "queue-number-of-tracks",
    duration:   "queue-duration"
})
Q.set_controller(Q_controller)

T = new TrackListView({
    name:       "main-track-list-name",
    num_tracks: "main-track-list-number-of-tracks",
    duration:   "main-track-list-duration",
    filter:      "filter-track-list"
}, Q_controller, shortlist_model, unavailable_model)
T.set_controller(T_controller)

PL = new PlaylistsView({
    list: 'queue-elements-body'
})
PL.set_controller(PL_controller)

SE = new SessionsView({
    list: 'queue-elements-body'
})
SE.set_controller(SE_controller)

mpc.init_audio()
pc.init_audio()
M = new MainPlayerView()
M.set_controller(mpc)
M.init()

P = new PrecuePlayerView()
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
    () => {
    }
)

mpc.on("track-finished",
    () => {
    }
)


ipcRenderer.on("headphone-playback-stopped", () => {
    pc.dispatch("playback-stopped")
})


ipcRenderer.on("headphone-playback-paused", () => {
    pc.dispatch("playback-paused")
})

ipcRenderer.on("headphone-playback-started", () => {
    pc.dispatch("playback-started")
})


ipcRenderer.on("headphone-stream-position", (event, pos) => {
    pc.dispatch("stream-position", pos)
})


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




// pc.on('playback-stopped',  () => {
//         vc.restore_monitor()
//     }
// )

// pc.on('playback-paused', () => {
//         vc.restore_monitor()
//     }
// )

pc.on('playback-started', () => {
        //vc.mute_monitor()
        SV.open_panel(3)
    }
)



mpc.on("queue-stop-requested",
    () => {
        B = document.getElementById("queue-start-button")
        B.innerHTML = "<i class=\"fa fa-close\"></i>"
        B.style.backgroundColor = "#667700"
    }
)

mpc.on("queue-stop-request-cancelled",
    () => {
        let M = document.getElementById("queue-stop-message")
        M.style.display="none"
        B = document.getElementById("queue-start-button")
        B.innerHTML = "<i class=\"fa fa-stop\"></i>"
        B.style.backgroundColor = "#AA0000"
    }
)

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

window.addEventListener("resize", (event) => {
    let h = document.getElementById("track-list-elements-header")
    let ta = document.getElementById("main-track-list-scroller")
    let tl = document.getElementById("main-track-list")
    list_height = (tl.clientHeight - h.clientHeight) - 5
    ta.style.maxHeight = list_height + "px";
})

document.getElementById("settings-button").addEventListener('click', () => {
    document.getElementById("main-menu-dropdown").classList.toggle("show");
})

document.getElementById("main-menu-add-track").addEventListener('click', () => {
    document.getElementById("main-menu-dropdown").classList.toggle("show");
})

document.getElementById("main-menu-reset-audio").addEventListener('click', () => {
    ipcRenderer.send("reset-audio-system", {})
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

document.getElementById("session-save").addEventListener('click', () => {
    let name = document.getElementById("session-name").value
    let location = document.getElementById("session-location").value
    let address = document.getElementById("session-address").value

    if (name != "") {
        //save
        current_session_model.store_session(name, location, address, () => {
            SE_controller.refresh(() => {})
        })
    }
    document.getElementById("save-session-dialog").close();
})


document.getElementById("session-save-cancel").addEventListener('click', () => {
    document.getElementById("save-session-dialog").close();
})



document.getElementById("main-menu-settings").addEventListener('click', () => {
    document.getElementById("main-menu-dropdown").classList.toggle("show");
})


document.getElementById("main-menu-mixer").addEventListener('click', () => {
    ipcRenderer.send("show-mixer-window")
    document.getElementById("main-menu-dropdown").classList.toggle("show");
})



document.getElementById("main-menu-quit").addEventListener('click', () => {
    document.getElementById("main-menu-dropdown").classList.toggle("show");
    ipcRenderer.send("quit-pymusic")
})

///////////////////////////////////////////////

function refresh_sessions(x) {
    console.log("refresh_sessions", x)
}

function display_all_songs() {
    T_controller.set_model("All Songs", tracks_model)
}

function display_current_session() {
    T_controller.set_model("Current Session", current_session_model)
}

function display_suggestions() {
    T_controller.set_model("Suggested tracks", suggested_model)
}

function display_short_list() {
    T_controller.set_model("All Songs", shortlist_model)
}

function display_unavailable() {
    T_controller.set_model("Unavailable tracks", unavailable_model)
}

function display_played_tracks() {
    T_controller.set_model("Played songs", played_tracks_model)
}

function display_never_played_tracks() {
    T_controller.set_model("Never Played songs", never_played_tracks_model)
}

function display_session(id) {
    DB.get_session_info(id,
        (info) => {
            let L = new SessionModel(info, tracks_model)
            T_controller.set_model(info.name, L)
        }
    )
}

function display_playlist(id) {
    DB.get_group_info(id,
        (info) => {
            let L = new PlaylistModel(info, tracks_model)
            T_controller.set_model(info.name, L)
        }
    )
}

ipcRenderer.on('playback-started', (event, arg) => {
    vc.mute_monitor()});

ipcRenderer.on('playback-stopped', (event, arg) => {
    vc.restore_monitor()});

display_all_songs()
