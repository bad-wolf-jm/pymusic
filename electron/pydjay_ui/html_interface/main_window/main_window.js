Sortable              = require("../lib/Sortable.js")
WaveSurfer            = require("wavesurfer.js")
var WaveSurferRegions = require('wavesurfer.js/dist/plugin/wavesurfer.regions.min.js');
var path              = require('path');


DB           = new DataProvider()
T_controller = new TrackListController()
Q_controller = new QueueController()
S_controller = new SessionController()
mpc          = new PlaybackController(S_controller, Q_controller)
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



mpc.init_audio()
M = new MainPlayerView()
M.set_controller(mpc)
M.init()

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
                    id: queue[i].id,
                    name: queue[i].name,
                    data: queue[i],
                    date: moment(queue[i].date).format("MM-DD-YYYY"),
                }
                queue_rows.push(element)
            }
            jui.ready([ "grid.table" ], function(table) {
                    table("#session-list-elements", {
                        data:queue_rows,
                        scroll: false,
                        resize: false
                    });
                }
            )
        }
    )    
}

function display_playlists() {
    DB.get_group_list(
        (queue) => { 
            queue_rows = []
            for (let i=0; i<queue.length; i++) {
                element = {
                    id:   queue[i].id,
                    name: queue[i].name,
                }
                queue_rows.push(element)
            }
            jui.ready([ "grid.table" ], function(table) {
                    table("#playlist-list-elements", {
                        data:queue_rows,
                        scroll: false,
                        resize: false
                    });
                }
            )
        }
    )    
}

display_sessions()
display_playlists()