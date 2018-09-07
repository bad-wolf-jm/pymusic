
DB = new DataProvider()

var table_13;

DB.get_queue_elements(
    (queue) => { 
        queue_rows = []
        // queue_rows = [
        //     {
        //         "title": "title_1",
        //         "artist": "artist_1",
        //         "bpm": "bpm_1",
        //         "duration": "0:01",
        //     },
        //     {
        //         "title": "title_1",
        //         "artist": "artist_1",
        //         "bpm": "bpm_1",
        //         "duration": "0:01",
        //     },
        //     {
        //         "title": "title_1",
        //         "artist": "artist_1",
        //         "bpm": "bpm_1",
        //         "duration": "0:01",
        //     },
        //     {
        //         "title": "title_1",
        //         "artist": "artist_1",
        //         "bpm": "bpm_1",
        //         "duration": "0:01",
        //     }
        // ]
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

// DB.get_queue_elements(
//     (queue) => { 
//         queue_rows = []
// queue_rows = [
//     {
//         "title": "title_1",
//         "artist": "artist_1",
//         "bpm": "bpm_1",
//         "cover":"../../../resources/images/default_album_cover.png",
//         "duration": "0:01",
//     },
//     {
//         "title": "title_2",
//         "artist": "artist_2",
//         "bpm": "bpm_2",
//         "cover":"../../../resources/images/default_album_cover.png",
//         "duration": "0:02",
//     },
//     {
//         "title": "title_3",
//         "artist": "artist_3",
//         "bpm": "bpm_3",
//         "cover":"../../../resources/images/default_album_cover.png",
//         "duration": "0:03",
//     },
//     {
//         "title": "title_4",
//         "artist": "artist_4",
//         "bpm": "bpm_4",
//         "cover":"../../../resources/images/default_album_cover.png",
//         "duration": "0:04",
//     },
//     {
//         "title": "title_5",
//         "artist": "artist_5",
//         "bpm": "bpm_5",
//         "cover":"../../../resources/images/default_album_cover.png",
//         "duration": "0:05",
//     },
//     {
//         "title": "title_6",
//         "artist": "artist_6",
//         "bpm": "bpm_6",
//         "cover":"../../../resources/images/default_album_cover.png",
//         "duration": "0:06",
//     }
// ]
// for (let i=0; i<queue.length; i++) {
//     element = {
//         title:    queue[i].title,
//         artist:   queue[i].artist,
//         bpm:      queue[i].bpm,
//         duration: format_nanoseconds(queue[i].stream_length),
//     }
//     if (queue[i].cover == null) {
//         element.cover = "../../../resources/images/default_album_cover.png"
//     } else {
//         element.cover = `file://${queue[i].image_root}/${queue[i].cover}`
//     }
//     queue_rows.push(element)
    
// }
// jui.ready([ "grid.table" ], function(table) {
//         table("#queue-list-elements", {
//             data:queue_rows,
//             scroll: false,
//             resize: false
//         });
//     }
// )
//     }
// )0
Sortable = require("../lib/Sortable.js")
var el = document.getElementById('queue-elements-body');
//console.log(Sortable)
var sortable = Sortable.create(el, {
    // group: {
    //     name:        'main',
    //     // put:         true,
    //     // revertClone: true,

    // },

    ghostClass: "ghost",
    animation: 150,
    // Element is chosen
	onChoose: function (/**Event*/evt) {
		console.log("chosen", evt.oldIndex);  // element index within parent
	},

	// Element dragging started
	onStart: function (/**Event*/evt) {
		console.log("start", evt.oldIndex);  // element index within parent
	},

	// Element dragging ended
	onEnd: function (/**Event*/evt) {
		var itemEl = evt.item;  // dragged HTMLElement
		console.log(evt.to,    // target list
		            evt.from,  // previous list
		            evt.oldIndex,  // element's old index within old parent
		            evt.newIndex)  // element's new index within new parent
	},

	// Element is dropped into the list from another list
	onAdd: function (/**Event*/evt) {
        // same properties as onEnd

        console.log("add", evt)
        return false
	},

	// Changed sorting within list
	onUpdate: function (/**Event*/evt) {
        console.log("update", evt)
		// same properties as onEnd
	},

	// Called by any change to the list (add / update / remove)
	onSort: function (/**Event*/evt) {
        // same properties as onEnd
        evt.item = undefined
        console.log("sort", evt)
        //return false
	},

	// Element is removed from the list into another list
	onRemove: function (/**Event*/evt) {
		// same properties as onEnd
	},

	// Attempt to drag a filtered element
	onFilter: function (/**Event*/evt) {
		var itemEl = evt.item;  // HTMLElement receiving the `mousedown|tapstart` event.
	},

	// // Event when you move an item in the list or between lists
	// onMove: function (/**Event*/evt, /**Event*/originalEvent) {
	// 	// // Example: http://jsbin.com/tuyafe/1/edit?js,output
	// 	// console.log(evt.dragged, // dragged HTMLElement
	// 	// evt.draggedRect, // TextRectangle {left, top, right и bottom}
	// 	// evt.related, // HTMLElement on which have guided
	// 	// evt.relatedRect, // TextRectangle
	// 	// originalEvent.clientY) // mouse position
    //     // // return false; — for cancel
    //     // return false
	// },

	// Called when creating a clone of element
	onClone: function (/**Event*/evt) {
		var origEl = evt.item;
        var cloneEl = evt.clone;
        //console.log()
	}
  });


  var mel = document.getElementById('main-elements-body');
  //console.log(Sortable)
  var sortable = Sortable.create(mel, {
    //   group: {
    //       name:'main',
    //     //   revertClone: true,
    //     //   pull:"clone"
    //     },
        sort:false,
      ghostClass:"ghost",
      animation: 200,
      // Element is chosen
      onChoose: function (/**Event*/evt) {
          console.log(evt.oldIndex);  // element index within parent
      },
  
      // Element dragging started
      onStart: function (/**Event*/evt) {
          console.log(evt.oldIndex);  // element index within parent
      },
  
      // Element dragging ended
      onEnd: function (/**Event*/evt) {
          var itemEl = evt.item;  // dragged HTMLElement
          console.log(evt.to,    // target list
                      evt.from,  // previous list
                      evt.oldIndex,  // element's old index within old parent
                      evt.newIndex)  // element's new index within new parent
      },
  
      // Element is dropped into the list from another list
      onAdd: function (/**Event*/evt) {
          // same properties as onEnd
      },
  
      // Changed sorting within list
      onUpdate: function (/**Event*/evt) {
          // same properties as onEnd
          console.log(evt)
      },
  
      // Called by any change to the list (add / update / remove)
      onSort: function (/**Event*/evt) {
          // same properties as onEnd
          console.log(evt)
      },
  
      // Element is removed from the list into another list
      onRemove: function (/**Event*/evt) {
          // same properties as onEnd
      },
  
      // Attempt to drag a filtered element
      onFilter: function (/**Event*/evt) {
          var itemEl = evt.item;  // HTMLElement receiving the `mousedown|tapstart` event.
      },
  
      // Event when you move an item in the list or between lists
      onMove: function (/**Event*/evt, /**Event*/originalEvent) {
          // Example: http://jsbin.com/tuyafe/1/edit?js,output
        //   console.log(evt.dragged, // dragged HTMLElement
        //   evt.draggedRect, // TextRectangle {left, top, right и bottom}
        //   evt.related, // HTMLElement on which have guided
        //   evt.relatedRect, // TextRectangle
        //   originalEvent.clientY) // mouse position
        //   // return false; — for cancel
          //return false
      },
  
      // Called when creating a clone of element
      onClone: function (/**Event*/evt) {
          var origEl = evt.item;
          var cloneEl = evt.clone;
      }
    });
  


// var main_table_drag = 


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

//Q = new QueueController()