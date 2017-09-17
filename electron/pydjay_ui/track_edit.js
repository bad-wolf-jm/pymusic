path = require('path');
fs = require('fs');
//wavesUI = require('waves-ui')

var stream_start_edit = undefined;
var stream_end_edit = undefined;


function edit_track_data(id) {
    db_connection.query(
        `SELECT title, artist, album, bpm, file_name, cover_medium, waveform,
                stream_start, stream_end, track_length, settings.db_music_cache as music_root,
                settings.db_waveform_cache as waveform_root,
                settings.db_image_cache as image_root
        FROM tracks left join settings on 1 WHERE tracks.id=${id} LIMIT 1`,
        function(error, result) {
            if (error) throw error;
            result = result[0];
            file_name = path.join(result.music_root, result.file_name);
            //console.log(file_name);
            cover_file_name = `${result.image_root}/${result.cover_small}`;
            stream_length = (result.stream_end-result.stream_start) / 1000000000;
            $$('main-title-edit').define('label', result.title)
            $$('main-title-edit').refresh()
            $$('main-artist-edit').define('label', `${result.artist}`)
            $$('main-artist-edit').refresh()
            $$('main-album-edit').define('label', `${result.album}`)
            $$('main-album-edit').refresh()
            if (result.cover_medium == null) {
                cover_source = "../resources/images/default_album_cover.png"
            } else {
                cover_source = `file://${result.image_root}/${result.cover_medium}`;
            }
            var cover_image = `<img style="margin:0px; padding:0px;" src="${cover_source}" height='128' width='128'></img>`
            $$('main-cover-image-edit').define('template', cover_image);
            $$('main-cover-image-edit').refresh();

            waveform_file = path.join(result.waveform_root, result.waveform);
            console.log(waveform_file);
            fs.readFile(waveform_file,
                function (err, data) {
                    if (err) throw err;
                    let data_start = data.indexOf(10)+1;
                    var buf = new ArrayBuffer(4);
                    var view = new DataView(buf);
                    amplitudes = []
                    for (var i = data_start; i+4<data.length; i=i+(8*5)) {
                        view.setUint8(3, data[i]);
                        view.setUint8(2, data[i+1]);
                        view.setUint8(1, data[i+2]);
                        view.setUint8(0, data[i+3]);
                        timestamp = view.getFloat32(0); //view.getInt16(0);
                        //i += 4;
                        view.setUint8(3, data[i+4]);
                        view.setUint8(2, data[i+5]);
                        view.setUint8(1, data[i+6]);
                        view.setUint8(0, data[i+7]);
                        average_amplitude = view.getFloat32(0); //view.getInt16(0);
                        amplitudes.push(average_amplitude);

                    }
                    //console.log(amplitudes);
                    var audioCtx = new AudioContext();
                    var buffer = audioCtx.createBuffer(1, Math.round((amplitudes.length / 250) * 3000), 3000);
                    var nowBuffering = buffer.getChannelData(0);
                    amplitudes.forEach(
                        function (value, index) {
                            nowBuffering[Math.round((index / 250) * 3000)] = value
                        }
                    )
                    var $track = document.querySelector('#track-waveform');
                    var width = $track.getBoundingClientRect().width;
                    var height = $track.getBoundingClientRect().height;
                    //var width = 500;
                    //var height = 125;
                    var duration = result.track_length / 1000000000;
                    // define the numbr of pixels per seconds the timeline should display
                    var pixelsPerSecond = 6*(width / duration);
                    console.log(pixelsPerSecond, duration, width, height);
                    var timeline = new wavesUI.core.Timeline(pixelsPerSecond, width);
                    // create a new track into the `track-1` element and give it a id ('main')
                    timeline.createTrack($track, height, 'main');
                    var waveformLayer = new wavesUI.helpers.WaveformLayer(buffer, {
                            width:width,
                         height: height
                       });
                    timeline.addLayer(waveformLayer, 'main');
                    timeline.tracks.render();
                    //track_edit_waveform.series[0].setData(amplitudes, true, false, false)
                }
            );
            track_data_edit_window.show();
        }
    )
}
