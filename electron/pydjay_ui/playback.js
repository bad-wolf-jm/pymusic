// zmq = require('zeromq');
// path = require('path');

// command_socket = zmq.socket('req');
// command_socket.connect('tcp://127.0.0.1:9898');
// command_socket.on("message", function( status, type, payload ) {

// });

// function send_command(name, args, kwargs) {
//     command_socket.send(JSON.stringify({'name': name, 'args': args, 'kwargs': kwargs}));
// }


pl_channel_config = {headphones:{left:4, right:5}}
mpl_channel_config = {master:{left:0, right:1}, headphones:{left:4, right:5}}

pl_channel_config2 = {headphones:{left:0, right:1}}
mpl_channel_config2 = {master:{left:0, right:1}}

// pl_channel_config = {headphones:{left:2, right:3}}
// mpl_channel_config = {master:{left:0, right:1}, headphones:{left:2, right:3}}


// pl_channel_config = {headphones:{left:4, right:5}}
// mpl_channel_config = {master:{left:0, right:1}, headphones:{left:4, right:5}}


var pl = new PydjayAudioFilePlayer()

//pl.connectOutputs(pl_channel_config)
pl.on('playback-stopped', restore_monitor)
pl.on('playback-paused', restore_monitor)
pl.on('playback-started', mute_monitor)

function preview_play(file_name, start_time, end_time){
    pl.play(file_name, start_time / 1000000, end_time / 1000000)
}

function preview_pause(file_name){
    pl.togglePause()
}

function preview_stop(file_name){
    pl.stop()
}

function preview_seek_relative(time_delta){
    pl.skip(time_delta)
}

pl.on("stream-position", function (pos) {
    $$('preview_time').define('label', `${format_nanoseconds(pos*1000000)}`)
    $$('preview_time').refresh()
    $$('preview_length').define('label', format_nanoseconds(pl.source.duration*1000000000))
    $$('preview_length').refresh();
    preview_seek.animate(pos / (1000*pl.source.duration));
    preview_track_position = pos;
})

var mpl = new MainPlayer()
//var mpl = new PydjayAudioFilePlayer()
//mpl.connectOutputs(mpl_channel_config)
// mpl.on("stream-position", function (pos) {
//     remaining = Math.abs(mpl.source.duration*1000 - pos)
//     $$('main_track_time').define('label', `-${format_nanoseconds(remaining*1000000)}`)
//     $$('main_track_time').refresh()
//     main_player_progress.animate(pos / (1000*mpl.source.duration));

// })
mpl.on('end-of-stream', function () {
    if (!stop_request){
        db_connection.query(
            'SELECT COUNT(id) as queue_count FROM session_queue WHERE status="pending"',
            function (error, result) {
                if (error) throw error;
                if (result[0].queue_count > 0) {
                    mark_as_played(current_queue_position, play_next_track_after_time);
                } else {
                    mark_as_played(current_queue_position, false);
                    queue_playing = false;
                    $$('start-stop-button').define('label', 'START');
                    $$('start-stop-button').define('icon', 'play');
                    $$('start-stop-button').refresh();
                    $$('queue_stop_message').hide()
                }
            }
        )
    } else {
        mark_as_played(current_queue_position, false);
        queue_playing = false;
        $$('start-stop-button').define('label', 'START');
        $$('start-stop-button').define('icon', 'play');
        $$('start-stop-button').refresh();
        $$('queue_stop_message').hide()
    }
})


function reset_audio() {
    let url = undefined
    if (mpl.source != undefined) {
        time = mpl.source.currentTime * 1000
        end_time = mpl.stream_end
        url = mpl.url
        mpl.stop()
    }
    mpl.reset_audio_context()
    pl.stop()
    pl.reset_audio_context()
    init_audio()
    // console.log(mpl.audio_context.audio_ctx.destination.maxChannelCount)
    // if (mpl.audio_context.audio_ctx.destination.maxChannelCount == 6) {
    //     mpl.connectOutputs(mpl_channel_config)
    //     pl.connectOutputs(pl_channel_config)    
    // } else {
    //     mpl.connectOutputs(mpl_channel_config2)
    //     pl.connectOutputs(pl_channel_config2)    
    // }


    if (url != undefined) {
        mpl.play(url, time, end_time)
    }
}

function init_audio() {
    console.log(mpl.audio_context.audio_ctx.destination.maxChannelCount)
    if (mpl.audio_context.audio_ctx.destination.maxChannelCount == 6) {
        mpl.connectOutputs(mpl_channel_config)
        pl.connectOutputs(pl_channel_config)    
    } else {
        mpl.connectOutputs(mpl_channel_config2)
        pl.connectOutputs(pl_channel_config2)    
    }
}



init_audio()

// epl = new PydjayAudioPlayer()
// epl.connectOutputs({master:{left:0, right:1}})
// epl.on('playback-stopped', restore_monitor)
// epl.on('playback-paused', restore_monitor)
// epl.on('playback-started', mute_monitor)
// //epl.on('playback-started', pl.)

// function edit_play(file_name, start_time, end_time){
//     epl.play(file_name, start_time / 1000000, end_time / 1000000)
// }

// function edit_pause(file_name){
//     epl.togglePause()
// }

// function edit_stop(file_name){
//     epl.stop()
// }

// function preview_seek_relative(time_delta){
//     pl.skip(time_delta)
// }

// pl.on("stream-position", function (pos) {
//     $$('preview_time').define('label', `${format_nanoseconds(pos*1000000)}`)
//     $$('preview_time').refresh()
//     $$('preview_length').define('label', format_nanoseconds(pl.source.duration*1000000000))
//     $$('preview_length').refresh();
//     preview_seek.animate(pos / (1000*pl.source.duration));
//     preview_track_position = pos;
// })





function main_play(file_name, start_time, end_time){
    mpl.play(file_name, start_time / 1000000, end_time / 1000000)
}

function main_stop(file_name, start_time, end_time){
    mpl.stop()
}

function set_main_player_volume(value){
    mpl.setVolume('master', 'left', value)
    mpl.setVolume('master', 'right', value)
}

function set_monitor_volume(value){
    mpl.setVolume('headphones', 'left', value)
    mpl.setVolume('headphones', 'right', value)
}

function set_precue_player_volume(value){
    pl.setVolume('master', 'left', value)
    pl.setVolume('master', 'right', value)
}

// function increase_main_player_volume(){
//     send_command('increase_main_player_volume', [], {});
// }

// function increase_monitor_volume(){
//     send_command('increase_monitor_volume', [], {});
// }

// function increase_precue_player_volume(){
//     send_command('increase_precue_player_volume', [], {});
// }

// function decrease_main_player_volume(){
//     send_command('decrease_main_player_volume', [], {});
// }

// function decrease_monitor_volume(){
//     send_command('decrease_monitor_volume', [], {});
// }

// function decrease_precue_player_volume(){
//     send_command('decrease_precue_player_volume', [], {});
// }


var preview_play_id = undefined
var preview_track_duration = 1;
var main_track_seconds_elapsed = 0;
var next_track_delay = 5;
var current_track_id = undefined;
var current_queue_position = undefined;
var queue_playing = false;
var stop_request = false;
var current_track_length = 1

var monitor_set_volume = 1;
var monitor_volume = 1;
var monitor_muted_volume = 0;
var monitor_muting = false;
var monitor_muting_time = 200;


function mute_monitor() {
    var a_monitor_volume = {volume: monitor_volume};
    $(a_monitor_volume).animate(
        {volume: monitor_muted_volume},
        {
            duration:100,
            step: function (now, tween){
                set_monitor_volume(now);
            },
        }
    )
}


function restore_monitor() {
    var a_monitor_volume = {volume: monitor_volume};
    $(a_monitor_volume).animate(
        {volume: monitor_set_volume},
        {
            duration:100,
            step: function (now, tween){
                set_monitor_volume(now);
            },
        }
    )
}


// volume_control_socket = zmq.socket('pull');
// volume_control_socket.connect('tcp://127.0.0.1:5555');
// volume_control_socket.on("message", function( payload ) {
//    data = JSON.parse(payload.toString());
//    value = Math.round(data.kwargs.value*100);
//    if (data.event == 'volume_set_notice') {
//        switch (data.kwargs.channels[0]) {
//             case 1:
//                 $$('main-player-volume').define('label', `${value}%`);
//                 $$('main-player-volume').refresh();
//                 break;
//             case 3:
//                 monitor_volume = data.kwargs.value;
//                 $$('monitor-volume').define('label', `${value}%`)
//                 $$('monitor-volume').refresh();
//                 break;
//             case 5:
//                 $$('precue-player-volume').define('label', `${value}%`)
//                 $$('precue-player-volume').refresh();
//                 break;
//        }
//    }
// });


// var preview_track_position = 0
// preview_time_socket = zmq.socket('pull');
// preview_time_socket.connect('tcp://127.0.0.1:5556');
// preview_time_socket.on("message", function( payload ) {
//    data = JSON.parse(payload.toString());
//    if (data.event == 'track_position_notice') {
//        $$('preview_time').define('label', format_nanoseconds(data.args[0]))
//        $$('preview_time').refresh();
//        if (track_data_edit_window.isVisible()) {
//            track_edit_waveform.xAxis[0].removePlotLine('position-marker');
//            track_edit_waveform.xAxis[0].addPlotLine({
//                color:'#FF0000',
//                width: 2,
//                zIndex:10,
//                value: data.args[0],
//                id: 'position-marker'});
//        }
//        preview_track_position = data.args[0];
//        preview_seek.animate(data.args[0] / preview_track_duration);
//    } else if (data.event == 'track_duration_notice') {
//        $$('preview_length').define('label', format_nanoseconds(data.args[0]))
//        $$('preview_length').refresh();
//        preview_track_duration = data.args[0];
//    } else if (data.event == 'end_of_stream') {
//        preview_track_duration = 1;
//        preview_track_position = 0
//        restore_monitor();
//    }
// });



// main_time_socket = zmq.socket('pull');
// main_time_socket.connect('tcp://127.0.0.1:5557');
// main_time_socket.on("message", function( payload ) {
//     data = JSON.parse(payload.toString());
//     if (data.event == 'track_position_notice') {
//         if (current_track_length != undefined) {
//             remaining = Math.abs(current_track_length - data.args[0])
//             $$('main_track_time').define('label', `-${format_nanoseconds(remaining)}`)
//             $$('main_track_time').refresh()
//         }
//         main_player_progress.animate(data.args[0] / current_track_length);
//     } else if (data.event == 'track_duration_notice') {
//         $$('main_track_time').define('label', `-${format_nanoseconds(data.args[0])}`)
//         $$('main_track_time').refresh();
//         current_track_length = data.args[0];
//     } else if (data.event == 'end_of_stream') {
//         if (!stop_request){
//             db_connection.query(
//                 'SELECT COUNT(id) as queue_count FROM session_queue WHERE status="pending"',
//                 function (error, result) {
//                     if (error) throw error;
//                     if (result[0].queue_count > 0) {
//                         mark_as_played(current_queue_position, play_next_track_after_time);
//                     } else {
//                         mark_as_played(current_queue_position, false);
//                         queue_playing = false;
//                         $$('start-stop-button').define('label', 'START');
//                         $$('start-stop-button').define('icon', 'play');
//                         $$('start-stop-button').refresh();
//                         $$('queue_stop_message').hide()
//                     }
//                 }
//             )
//         } else {
//             mark_as_played(current_queue_position, false);
//             queue_playing = false;
//             $$('start-stop-button').define('label', 'START');
//             $$('start-stop-button').define('icon', 'play');
//             $$('start-stop-button').refresh();
//             $$('queue_stop_message').hide()
//         }
//     }
// });


function mark_as_played(queue_position, continuation) {
    current_time = webix.Date.dateToStr('%Y-%m-%d %H:%i:%s')(new Date());
    db_connection.query(
        `UPDATE session_queue SET status='played', end_time='${current_time}' WHERE position=${queue_position}`,
        function (error, result) {
            db_connection.query(
                `SELECT wait_time FROM settings`,
                function (error, result) {
                    if (error) {
                        next_track_delay = 5;
                    } else {
                        next_track_delay = result[0].wait_time;
                    }
                    if (continuation) {
                        continuation(next_track_delay);
                    }
                }
            )
        }
    )
}

function play_next_track_after_time(time_in_seconds) {
    var delay = time_in_seconds;
    var id = setInterval(
        function () {
            if (delay <= 0) {
                clearInterval(id);
                $$(mpl.title_id).define('label', ``)
                play_next_track();
            } else {
                if (delay > 1) {
                    $$(mpl.title_id).define('label', `Next track will start in ${delay} seconds`)
                } else {
                    $$(mpl.title_id).define('label', `Next track will start in 1 second`)
                }
                $$(mpl.title_id).refresh()
                delay--;
            }
        }, 1000)
}

function play_next_track() {
    db_connection.query(
        `SELECT min(position) as next_position FROM session_queue WHERE status='pending' GROUP BY status`,
        function (error, result) {
            if (error) throw error;
            position = result[0].next_position;
            current_time = webix.Date.dateToStr('%Y-%m-%d %H:%i:%s')(new Date());
            db_connection.query(
                `UPDATE session_queue SET status='playing', start_time='${current_time}' WHERE position=${position}`,
                function (error, result) {
                    if (error) throw error;
                    db_connection.query(
                        `SELECT track_id FROM session_queue WHERE position=${position}`,
                        function (error, result) {
                            if (error) throw error;
                            track_id = result[0].track_id;
                            DB.get_track_by_id(track_id, 
                                function (track) {
                                    $$('queue_list').remove($$('queue_list').getFirstId())
                                    update_queue_labels();
                                    mpl.play(track[0])
                                }
                            )



                            // db_connection.query(
                            //     `SELECT title, artist, album, bpm, file_name, cover_small, stream_start, stream_end, settings.db_music_cache as music_root,
                            //      settings.db_image_cache as image_root FROM tracks left join settings on 1 WHERE tracks.id=${track_id} LIMIT 1`,
                            //     function (error, result) {
                            //         if (error) throw error;
                            //         result = result[0];
                            //         file_name = path.join(result.music_root, result.file_name);
                            //         stream_length = (result.stream_end-result.stream_start) / 1000000000;
                            //         $$('main-title').define('label', result.title)
                            //         $$('main-title').refresh()
                            //         $$('main-artist').define('label', `${result.artist} - ${result.album}`)
                            //         $$('main-artist').refresh()
                            //         if (result.cover_small == null) {
                            //             cover_source = "../resources/images/default_album_cover.png"
                            //         } else {
                            //             cover_source = `file://${result.image_root}/${result.cover_small}`;
                            //         }
                            //         var cover_image = `<img style="margin:0px; padding:0px;" src="${cover_source}" height='58' width='58'></img>`
                            //         $$('main-cover-image').define('template', cover_image);
                            //         $$('main-cover-image').refresh();
                            //         current_queue_position = position;
                            //         $$('queue_list').remove($$('queue_list').getFirstId())
                            //         update_queue_labels();
                            //         main_play(file_name, result.stream_start, result.stream_end)

                            //     }
                            // )
                        }
                    )
                }
            )
        }
    )
}

function start_queue() {
    if (!queue_playing) {
        db_connection.query(
            `SELECT count(id) as queue_count FROM session_queue WHERE status='pending'`,
            function (error, result) {
                if (error) throw error;
                if (result[0].queue_count > 0) {
                    play_next_track()
                    queue_playing = true;
                    stop_request = false;
                    $$('queue_stop_message').hide()
                    $$('start-stop-button').define('label', 'STOP');
                    $$('start-stop-button').define('icon', 'stop');
                    $$('start-stop-button').refresh();
                }
            }
        )
    } else {
        if (!stop_request){
            stop_request = true;
            $$('queue_stop_message').show()
            $$('start-stop-button').define('label', 'CANCEL');
            $$('start-stop-button').define('icon', 'close');
            $$('start-stop-button').refresh();
        } else {
            stop_request = false;
            $$('queue_stop_message').hide()
            $$('start-stop-button').define('label', 'STOP');
            $$('start-stop-button').define('icon', 'stop');
            $$('start-stop-button').refresh();
        }
    }
}


function stop_queue_now() {
    mark_as_played(current_queue_position, (t) => {main_stop()});
    queue_playing = false;
    stop_request = false;
    $$('start-stop-button').define('label', 'START');
    $$('start-stop-button').define('icon', 'play');
    $$('start-stop-button').refresh();
    $$('queue_stop_message').hide();
    $$('skip_stop_dialog').hide();
}

function skip_to_next_track() {
    if (queue_playing && !stop_request){
        main_stop()
        db_connection.query(
            `SELECT count(id) as queue_count FROM session_queue WHERE status='pending'`,
            function (error, result) {
                if (error) throw error;
                if (result[0].queue_count > 0) {
                    mark_as_played(current_queue_position, (t) => {play_next_track()});
                } else {
                    $$('start-stop-button').define('label', 'START');
                    $$('start-stop-button').define('icon', 'play');
                    $$('start-stop-button').refresh();
                    $$('queue_stop_message').hide();
                    queue_playing = false;
                    stop_request = false;
                }
            }
        )
    }
    $$('skip_stop_dialog').hide()
}

function preview_play_track_id(id, stream_start, stream_end) {
    db_connection.query(
        `SELECT title, artist, album, bpm, file_name, cover_small, track_length, genre, stream_start, year, stream_end, settings.db_music_cache as music_root,
         settings.db_image_cache as image_root FROM tracks left join settings on 1 WHERE tracks.id=${id} LIMIT 1`,
        function(error, result) {
            if (error) throw error;
            result = result[0];
            file_name = path.join(result.music_root, result.file_name);
            cover_file_name = `${result.image_root}/${result.cover_small}`;
            stream_length = (result.stream_end-result.stream_start) / 1000000000;
            preview_play_id = result.id
            $$('preview_title').define('label', `<b>${result.title}</b>`)
            $$('preview_title').refresh()
            $$('preview_artist').define('label', `${result.artist}`)
            $$('preview_artist').refresh()
            if (result.cover_small == null) {
                cover_source = "../resources/images/default_album_cover.png"
            } else {
                cover_source = `file://${result.image_root}/${result.cover_small}`;
            }
            var cover_image = `<img style="margin:0px; padding:0px;" src="${cover_source}" height='95' width='95'></img>`
            $$('preview-cover-image').define('template', cover_image);
            $$('preview-cover-image').refresh();

            if (stream_start == undefined) {
                stream_start = result.stream_start // Math.floor(Math.random() * Math.floor(result.stream_end - result.stream_start));
                stream_end = result.stream_end
            } else if (stream_end == undefined) {
                stream_end = end = result.stream_end
                if (stream_start < 0) {
                    stream_start = stream_end + stream_start;
                }
            }
            // $$("metadata").setValues(
            //     {
            //         title: result.title || "",
            //         artist: result.artist || "",
            //         album: result.album || "",
            //         year: result.year || "",
            //         genre: result.genre || "",
            //         color: result.color || "#FFFFFF",
            //         bpm: result.bpm || "",
            //         track_length:`${format_nanoseconds(result.track_length)}`,
            //         track_start:`${format_nanoseconds(result.stream_start)}`,
            //         track_end: `${format_nanoseconds(result.stream_end)}`,
            //         file: file_name
            //     }
            // )            
            preview_play(file_name, stream_start, stream_end)
        }
    )
}
