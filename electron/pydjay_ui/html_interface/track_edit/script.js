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
    
    DB.get_settings((settings) => {
        let new_values = view.getValues()
        let image_root = `${settings.image_root}`
        //console.log(new_values)
        if (new_values.cover != null) {
            new_values.cover_original = `cover_original_${track_id}`
            new_values.cover_large    = `cover_large_${track_id}`
            new_values.cover_medium   = `cover_medium_${track_id}`
            new_values.cover_small    = `cover_small_${track_id}`
            new_values.cover.write(`${path.join(settings.image_root, new_values.cover_original)}`);
            new_values.cover.resize(320,320).write(`${path.join(settings.image_root, new_values.cover_large)}`)
            new_values.cover.resize(160,160).write(`${path.join(settings.image_root, new_values.cover_medium)}`)
            new_values.cover.resize(100,100).write(`${path.join(settings.image_root, new_values.cover_small)}`)      
        } else if (new_values.cover !== undefined) {
            new_values.cover_original = null;
            new_values.cover_large    = null;
            new_values.cover_medium   = null;
            new_values.cover_small    = null;
        }

        DB.update_track_data(track_id, new_values, () => {
            ipcRenderer.send("track-modified", track_id)
        })    
    })
}