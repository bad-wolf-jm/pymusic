WaveSurfer            = require("wavesurfer.js")
var WaveSurferRegions = require('wavesurfer.js/dist/plugin/wavesurfer.regions.min.js');
var path              = require('path');
const { ipcRenderer } = require('electron');
const remote = require('electron').remote;

var track_id = null

DB = new DataProvider()

view = new MainPlayerView()
view.init()

function _get_rating(track_object) {
    let html = "";
    for (let j=1; j<6; j++) {
        html+="<i class='fa " + ( j <= track_object.rating ? "fa-star" : "fa-star-o") +"' style='font-size:8pt; margin-left:3px'></i>";
    }
    return html
}

function setTrack(id) {
    track_id = id
    DB.get_track_by_id(id, (track) => {
        view.set_track(track[0])
        DB.get_related_tracks(id, (queue) => {
            DB.get_playback_history(id, (history) => {
                let queue_rows = []  
                for(let i=0; i<queue.length; i++) {
                    let element = {
                        id:          queue[i].id,
                        available:   queue[i].available,
                        color:       queue[i].color,
                        loved:       "<i title='"+i+"' class='fa " + (queue[i].favorite ? "fa-heart" : "fa-heart-o") +"'></i>",
                        title:       queue[i].title,
                        artist:      queue[i].artist,
                        genre:       queue[i].genre,
                        last_played: (queue[i].last_played != null) ? moment(queue[i].last_played).format('MM-DD-YYYY') : "",
                        play_count:  queue[i].play_count,
                        rating:      _get_rating(queue[i]), 
                        bpm:         queue[i].bpm,
                        duration:    format_nanoseconds(queue[i].stream_length),
                    }
                    queue_rows.push(element)
                }
                jui.ready([ "grid.table" ], (table) => {
                    var queue_content = table("#related-elements", {
                        data:   queue_rows,
                        scroll: false,
                        resize: false
                    });
                    var history_content = table("#playback-history", {
                        data:   history,
                        scroll: false,
                        resize: false
                    })
                })
            })
        })
    })    
}

ipcRenderer.on('track-id', (event, arg) => {setTrack(arg.id)});

function closeme() {
    var window = remote.getCurrentWindow();
    view.audio_player.stop()
    window.close();
}

function saveme() {
    var window = remote.getCurrentWindow();
    view.audio_player.stop()
    

    DB.update_track_data(track_id, view.getValues(), () => {
        ipcRenderer.send("track-modified", track_id)
        window.close();
    })
}