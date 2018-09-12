Sortable              = require("../lib/Sortable.js")
WaveSurfer            = require("wavesurfer.js")
var WaveSurferRegions = require('wavesurfer.js/dist/plugin/wavesurfer.regions.min.js');
var path              = require('path');


DB            = new DataProvider()
T_controller  = new TrackListController()
Q_controller  = new QueueController()
S_controller  = new SessionController()
PL_controller = new PlaylistsController()
SE_controller = new SessionsController()
mpc           = new PlaybackController(S_controller, Q_controller)
pc            = new PrecueController(S_controller, Q_controller)
Q = new QueueView({
    list:       'queue-elements-body',
    num_tracks: "queue-number-of-tracks",
    duration:   "queue-duration"
})
Q.set_controller(Q_controller)

T = new TrackListView({
    name:       "main-track-list-name",
    num_tracks: "main-track-list-number-of-tracks",
    duration:   "main-track-list-duration"
})
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
// M.init()



mpc.on("queue-started", 
    () => {
        B = document.getElementById("queue-start-button")
        B.innerHTML = "<i class=\"fa fa-stop\"></i>"
        B.style.backgroundColor = "#660000"
    }
)

mpc.on("queue-stopped", 
    () => {
        M = document.getElementById("queue-stop-message")
        M.style.visibility="hidden"
        B = document.getElementById("queue-start-button")
        B.innerHTML = "<i class=\"fa fa-play\"></i>"
        B.style.backgroundColor = "rgb(25,25,25)"
    }
)

mpc.on("queue-finished", 
    () => {
        M = document.getElementById("queue-stop-message")
        M.style.visibility="hidden"
        B = document.getElementById("queue-start-button")
        B.innerHTML = "<i class=\"fa fa-play\"></i>"
        B.style.backgroundColor = "rgb(25,25,25)"
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

mpc.on("queue-stop-requested", 
    () => {
        M = document.getElementById("queue-stop-message")
        M.style.visibility="visible"
        B = document.getElementById("queue-start-button")
        B.innerHTML = "<i class=\"fa fa-play-circle\"></i>"
        B.style.backgroundColor = "#667700"
    }
)

mpc.on("queue-stop-request-cancelled", 
    () => {
        let M = document.getElementById("queue-stop-message")
        M.style.visibility="hidden"
        B = document.getElementById("queue-start-button")
        B.innerHTML = "<i class=\"fa fa-stop\"></i>"
        B.style.backgroundColor = "#AA0000"
    }
)

mpc.on("next-track-countdown", (time) => {
    let M = document.getElementById("main-player-time-remaining")
    console.log(time)
    M.innerHTML = `${time}`
})


function refresh_sessions(x) {
    console.log("refresh_sessions", x)
}

function display_all_songs() {
    DB.get_all_tracks(
        (queue) => { 
            T_controller.set_list("All Songs", queue)
        }
    )
}

function display_suggestions() {
    DB.get_suggested_tracks(
        (queue) => { 
            T_controller.set_list("Suggested Songs", queue)
        }
    )    
}

function display_short_list() {
    DB.get_shortlisted_tracks(
        (queue) => { 
            T_controller.set_list("Short listed Songs", queue)
        }
    )    
}

function display_unavailable() {
    DB.get_unavailable_tracks(
        (queue) => { 
            T_controller.set_list("Unavailable Songs", queue)
        }
    )    
}

function display_played_tracks() {
    DB.get_played_tracks(
        (queue) => { 
            T_controller.set_list("Played Songs", queue)
        }
    )    
}

function display_never_played_tracks() {
    DB.get_never_played_tracks(
        (queue) => { 
            T_controller.set_list("never played Songs", queue)
        }
    )    
}

function display_session(id) {
    DB.get_session_info(id, 
        (info) => {
            DB.get_session_tracks(id, 
                (queue) => { 
                    T_controller.set_list(`${info.name} - ${moment(info.date).format("MM-DD-YYYY")}`, queue)
                }
            )            
        }
    )
}

function display_playlist(id) {
    DB.get_group_info(id, 
        (info) => {
            DB.get_playlist_tracks(id, 
                (queue) => { 
                    T_controller.set_list(`${info.name}`, queue)
                }
            )            
        }
    )
}

function display_sessions() {
    DB.get_sessions_list(
        (queue) => { 
            queue_rows = []
            for (let i=0; i<queue.length; i++) {
                element = {
                    id:   queue[i].id,
                    name: queue[i].name,
                    data: queue[i],
                    date: moment(queue[i].date).format("MM-DD-YYYY"),
                }
                queue_rows.push(element)
            }
            jui.ready([ "grid.table" ], function(table) {
                    table("#session-list-elements", {
                        data:   queue_rows,
                        scroll: false,
                        resize: false
                    });
                }
            )
        }
    )    
}
