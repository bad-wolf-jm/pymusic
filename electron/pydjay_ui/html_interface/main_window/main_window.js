
DB = new DataProvider()

var table_13;

DB.get_queue_elements(
    (queue) => { 
        queue_rows = []
        for (let i=0; i<queue.length; i++) {
            element = {
                title:    queue[i].title,
                artist:   queue[i].artist,
                bpm:      queue[i].bpm,
                duration: format_nanoseconds(queue[i].stream_length),
            }
            if (queue[i].cover == null) {
                element.cover = "../../../resources/images/default_album_cover.png"
            } else {
                element.cover = `file://${queue[i].image_root}/${queue[i].cover}`
            }
            queue_rows.push(element)
            
        }
        jui.ready([ "grid.table" ], function(table) {
                table("#queue-list-elements", {
                    data:queue_rows,
                    scroll: false,
                    resize: false
                });
            }
        )
    }
)

function format_main_list(track_list) {
    queue_rows = []
    for (let i=0; i<track_list.length; i++) {
        element = {
            title:       track_list[i].title,
            artist:      track_list[i].artist,
            genre:       track_list[i].genre,
            last_played: (track_list[i].last_played != null) ? moment(track_list[i].last_played).format('MM-DD-YYYY') : "",
            play_count:  track_list[i].play_count,
            rating:      track_list[i].rating,
            bpm:         track_list[i].bpm,
            duration: format_nanoseconds(track_list[i].stream_length),
        }
        queue_rows.push(element)
    }
    return queue_rows

}

function display_all_songs() {
    DB.get_all_tracks(
        (queue) => { 
            queue_rows = format_main_list(queue)
            jui.ready([ "grid.table" ], function(table) {
                    table("#track-list-elements", {
                        data:queue_rows,
                        scroll: false,
                        resize: false
                    });
                }
            )
        }
    )
}

function display_suggestions() {
    DB.get_suggested_tracks(
        (queue) => { 
            queue_rows = format_main_list(queue)
            jui.ready([ "grid.table" ], function(table) {
                    table("#track-list-elements", {
                        data:queue_rows,
                        scroll: false,
                        resize: false
                    });
                }
            )
        }
    )    
}

function display_short_list() {
    DB.get_shortlisted_tracks(
        (queue) => { 
            queue_rows = format_main_list(queue)
            jui.ready([ "grid.table" ], function(table) {
                    table("#track-list-elements", {
                        data:queue_rows,
                        scroll: false,
                        resize: false
                    });
                }
            )
        }
    )    
}

function display_unavailable() {
    DB.get_unavailable_tracks(
        (queue) => { 
            queue_rows = format_main_list(queue)
            jui.ready([ "grid.table" ], function(table) {
                    table("#track-list-elements", {
                        data:queue_rows,
                        scroll: false,
                        resize: false
                    });
                }
            )
        }
    )    
}

function display_played_tracks() {
    DB.get_played_tracks(
        (queue) => { 
            queue_rows = format_main_list(queue)
            jui.ready([ "grid.table" ], function(table) {
                    table("#track-list-elements", {
                        data:queue_rows,
                        scroll: false,
                        resize: false
                    });
                }
            )
        }
    )    
}

function display_never_played_tracks() {
    DB.get_never_played_tracks(
        (queue) => { 
            queue_rows = format_main_list(queue)
            jui.ready([ "grid.table" ], function(table) {
                    table("#track-list-elements", {
                        data:queue_rows,
                        scroll: false,
                        resize: false
                    });
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
                    name:      queue[i].name,
                    date:      moment(queue[i].date).format("MM-DD-YYYY"),
                }
                queue_rows.push(element)
            }
            // return queue_rows
        
        
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
                    name:      queue[i].name,
                    // date:      moment(queue[i].date).format("MM-DD-YYYY"),
                }
                queue_rows.push(element)
            }
            // return queue_rows
        
        
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


display_all_songs()
display_sessions()
display_playlists()