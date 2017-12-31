zmq = require('zeromq');
path = require('path');

command_socket = zmq.socket('req');
command_socket.connect('tcp://127.0.0.1:9898');
command_socket.on("message", function( status, type, payload ) {
    //console.log("Received reply", payload);
});

function send_command(name, args, kwargs) {
    command_socket.send(JSON.stringify({'name': name, 'args': args, 'kwargs': kwargs}));
}

function preview_play(file_name, start_time, end_time){
    mute_monitor()
    send_command('preview_play', [file_name, start_time, end_time], {});
}

function preview_pause(file_name){
    send_command('preview_pause', [], {});
}

function preview_stop(file_name){
    send_command('preview_stop', [], {});
    restore_monitor();
}

function preview_seek_relative(time_delta){
    send_command('preview_seek', [time_delta], {});
}

function main_play(file_name, start_time, end_time){
    send_command('main_play', [file_name, start_time, end_time], {});
}

function main_stop(file_name, start_time, end_time){
    send_command('main_stop', [], {});
}

function set_main_player_volume(value){
    send_command('set_main_player_volume', [value], {});
}

function set_monitor_volume(value){
    send_command('set_monitor_volume', [value], {});
}

function set_precue_player_volume(value){
    send_command('set_precue_player_volume', [value], {});
}

function increase_main_player_volume(){
    send_command('increase_main_player_volume', [], {});
}

function increase_monitor_volume(){
    send_command('increase_monitor_volume', [], {});
}

function increase_precue_player_volume(){
    send_command('increase_precue_player_volume', [], {});
}

function decrease_main_player_volume(){
    send_command('decrease_main_player_volume', [], {});
}

function decrease_monitor_volume(){
    send_command('decrease_monitor_volume', [], {});
}

function decrease_precue_player_volume(){
    send_command('decrease_precue_player_volume', [], {});
}



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
var monitor_muted_volume = 0.01;
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


volume_control_socket = zmq.socket('pull');
volume_control_socket.connect('tcp://127.0.0.1:5555');
volume_control_socket.on("message", function( payload ) {
   data = JSON.parse(payload.toString());
   value = Math.round(data.kwargs.value*100);
   if (data.event == 'volume_set_notice') {
       switch (data.kwargs.channels[0]) {
            case 1:
                $$('main-player-volume').define('label', `${value}%`);
                $$('main-player-volume').refresh();
                break;
            case 3:
                monitor_volume = data.kwargs.value;
                $$('monitor-volume').define('label', `${value}%`)
                $$('monitor-volume').refresh();
                break;
            case 5:
                $$('precue-player-volume').define('label', `${value}%`)
                $$('precue-player-volume').refresh();
                break;
       }
   }
});


var preview_track_position = 0
preview_time_socket = zmq.socket('pull');
preview_time_socket.connect('tcp://127.0.0.1:5556');
preview_time_socket.on("message", function( payload ) {
   data = JSON.parse(payload.toString());
   if (data.event == 'track_position_notice') {
       $$('preview_time').define('label', format_nanoseconds(data.args[0]))
       $$('preview_time').refresh();
       if (track_data_edit_window.isVisible()) {
           track_edit_waveform.xAxis[0].removePlotLine('position-marker');
           track_edit_waveform.xAxis[0].addPlotLine({
               color:'#FF0000',
               width: 2,
               zIndex:10,
               value: data.args[0],
               id: 'position-marker'});
       }
       preview_track_position = data.args[0];
       preview_seek.animate(data.args[0] / preview_track_duration);
   } else if (data.event == 'track_duration_notice') {
       $$('preview_length').define('label', format_nanoseconds(data.args[0]))
       $$('preview_length').refresh();
       preview_track_duration = data.args[0];
   } else if (data.event == 'end_of_stream') {
       preview_track_duration = 1;
       preview_track_position = 0
       restore_monitor();
   }
});



main_time_socket = zmq.socket('pull');
main_time_socket.connect('tcp://127.0.0.1:5557');
main_time_socket.on("message", function( payload ) {
    data = JSON.parse(payload.toString());
    if (data.event == 'track_position_notice') {
        if (current_track_length != undefined) {
            remaining = Math.abs(current_track_length - data.args[0])
            $$('main_track_time').define('label', `-${format_nanoseconds(remaining)}`)
            $$('main_track_time').refresh()
        }
        main_player_progress.animate(data.args[0] / current_track_length);
    } else if (data.event == 'track_duration_notice') {
        $$('main_track_time').define('label', `-${format_nanoseconds(data.args[0])}`)
        $$('main_track_time').refresh();
        current_track_length = data.args[0];
    } else if (data.event == 'end_of_stream') {
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
    }
});


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
                $$('main-artist').define('label', `Next track will start now...`)
                play_next_track();
            } else {
                if (delay > 1) {
                    $$('main-artist').define('label', `Next track will start in ${delay} seconds`)
                } else {
                    $$('main-artist').define('label', `Next track will start in 1 second`)
                }
                $$('main-artist').refresh()
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
                            db_connection.query(
                                `SELECT title, artist, album, bpm, file_name, cover_small, stream_start, stream_end, settings.db_music_cache as music_root,
                                 settings.db_image_cache as image_root FROM tracks left join settings on 1 WHERE tracks.id=${track_id} LIMIT 1`,
                                function (error, result) {
                                    if (error) throw error;
                                    result = result[0];
                                    file_name = path.join(result.music_root, result.file_name);
                                    stream_length = (result.stream_end-result.stream_start) / 1000000000;
                                    $$('main-title').define('label', result.title)
                                    $$('main-title').refresh()
                                    $$('main-artist').define('label', `${result.artist} - ${result.album}`)
                                    $$('main-artist').refresh()
                                    if (result.cover_small == null) {
                                        cover_source = "../resources/images/default_album_cover.png"
                                    } else {
                                        cover_source = `file://${result.image_root}/${result.cover_small}`;
                                    }
                                    var cover_image = `<img style="margin:0px; padding:0px;" src="${cover_source}" height='58' width='58'></img>`
                                    $$('main-cover-image').define('template', cover_image);
                                    $$('main-cover-image').refresh();
                                    current_queue_position = position;
                                    $$('queue_list').remove($$('queue_list').getFirstId())
                                    update_queue_labels();
                                    main_play(file_name, result.stream_start, result.stream_end)

                                }
                            )
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
        `SELECT title, artist, album, bpm, file_name, cover_small, stream_start, stream_end, settings.db_music_cache as music_root,
         settings.db_image_cache as image_root FROM tracks left join settings on 1 WHERE tracks.id=${id} LIMIT 1`,
        function(error, result) {
            if (error) throw error;
            result = result[0];
            file_name = path.join(result.music_root, result.file_name);
            cover_file_name = `${result.image_root}/${result.cover_small}`;
            stream_length = (result.stream_end-result.stream_start) / 1000000000;
            $$('preview_title').define('label', result.title)
            $$('preview_title').refresh()
            $$('preview_artist').define('label', `${result.artist} - ${result.album}`)
            $$('preview_artist').refresh()
            if (result.cover_small == null) {
                cover_source = "../resources/images/default_album_cover.png"
            } else {
                cover_source = `file://${result.image_root}/${result.cover_small}`;
            }
            var cover_image = `<img style="margin:0px; padding:0px;" src="${cover_source}" height='75' width='75'></img>`
            $$('preview-cover-image').define('template', cover_image);
            $$('preview-cover-image').refresh();
            stream_start = (stream_start == undefined) ? result.stream_start : stream_start;
            stream_end = (stream_end == undefined) ? result.stream_end : stream_end;
            if (stream_start < 0) {
                stream_start = stream_end + stream_start;
            }
            preview_play(file_name, stream_start, stream_end)
        }
    )
}
