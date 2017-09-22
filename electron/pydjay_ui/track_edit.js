path = require('path');
fs = require('fs');
//wavesUI = require('waves-ui')

var track_id_edit = undefined;
var stream_start_edit = undefined;
var stream_end_edit = undefined;
var track_edited = undefined;
var track_length_edit = undefined;

function edit_track_data(id) {
    db_connection.query(
        `SELECT tracks.id as id, title, artist, album, bpm, file_name, cover_medium, waveform,
                stream_start, stream_end, track_length, settings.db_music_cache as music_root,
                settings.db_waveform_cache as waveform_root,
                settings.db_image_cache as image_root
        FROM tracks LEFT JOIN settings on 1 WHERE tracks.id=${id} LIMIT 1`,
        function(error, result) {
            if (error) throw error;
            result = result[0];
            track_edited = result;
            file_name = path.join(result.music_root, result.file_name);
            cover_file_name = `${result.image_root}/${result.cover_small}`;
            stream_length = (result.stream_end-result.stream_start) / 1000000000;
            stream_start_edit = result.stream_start;
            stream_end_edit = result.stream_end;
            track_length_edit = result.track_length;
            track_id_edit = result.id;
            $$('main-title-edit').define('label', result.title)
            $$('main-title-edit').refresh()
            $$('main-artist-edit').define('label', `${result.artist}`)
            $$('main-artist-edit').refresh()
            $$('main-album-edit').define('label', `${result.album}`)
            $$('main-album-edit').refresh()
            $$('track-data').define('label', `${format_nanoseconds(result.track_length)} - ${result.bpm} BPM`)
            $$('track-data').refresh()

            if (result.cover_medium == null) {
                cover_source = "../resources/images/default_album_cover.png"
            } else {
                cover_source = `file://${result.image_root}/${result.cover_medium}`;
            }
            var cover_image = `<img style="margin:0px; padding:0px;" src="${cover_source}" height='128' width='128'></img>`
            $$('main-cover-image-edit').define('template', cover_image);
            $$('main-cover-image-edit').refresh();

            waveform_file = path.join(result.waveform_root, result.waveform);

            fs.readFile(waveform_file,
                function (err, data) {
                    if (err) throw err;
                    set_start_marker(stream_start_edit);
                    set_end_marker(stream_end_edit);
                    let data_start = data.indexOf(10)+1;
                    var buf = new ArrayBuffer(4);
                    var view = new DataView(buf);
                    amplitudes = []
                    for (var i = data_start; i+4<data.length; i=i+(8*5)) {
                        view.setUint8(3, data[i]);
                        view.setUint8(2, data[i+1]);
                        view.setUint8(1, data[i+2]);
                        view.setUint8(0, data[i+3]);
                        timestamp = view.getFloat32(0);
                        view.setUint8(3, data[i+4]);
                        view.setUint8(2, data[i+5]);
                        view.setUint8(1, data[i+6]);
                        view.setUint8(0, data[i+7]);
                        average_amplitude = view.getFloat32(0);
                        amplitudes.push([timestamp, average_amplitude]);
                    }
                    track_edit_waveform.series[0].setData(amplitudes, false, false, false);
                    track_edit_waveform.redraw(false);
                }
            );
            track_data_edit_window.show();
        }
    )
}

function set_start_marker_to_current_time() {
    set_start_marker(preview_track_position);
}

function set_end_marker_to_current_time() {
    set_end_marker(preview_track_position);
}

function cover_waveform(id, start, end) {
    track_edit_waveform.xAxis[0].removePlotBand(id);
    track_edit_waveform.xAxis[0].addPlotBand({
        color:'rgba(25,25,25,0.8)',
        width: 2,
        zIndex: 10,
        from:start,
        to: end,
        id: id});
}

function mark_position(id, position) {
    track_edit_waveform.xAxis[0].removePlotLine(id);
    track_edit_waveform.xAxis[0].addPlotLine({
        color:'#00FF00',
        width: 2,
        zIndex: 10,
        value: position,
        id: id});
}

function set_start_marker(timestamp) {
    stream_start_edit = Math.max(timestamp, 0);
    cover_waveform('stream-start-cover', 0, stream_start_edit);
    mark_position('stream-start-marker', stream_start_edit);
}

function set_end_marker(timestamp) {
    stream_end_edit = Math.min(timestamp, track_length_edit);
    cover_waveform('stream-end-cover', stream_end_edit, track_length_edit);
    mark_position('stream-end-marker', stream_end_edit);
}


function save_new_track_info() {
    $QUERY(
        `UPDATE tracks SET
         stream_start=${stream_start_edit},
         stream_end=${stream_end_edit},
         stream_length=${stream_end_edit-stream_start_edit} WHERE id=${track_id_edit}`,
         function (r) {
             console.log('track_edited')
         }

    )
}
