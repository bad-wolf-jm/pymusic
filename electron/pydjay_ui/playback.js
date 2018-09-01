pl_channel_config = {headphones:{left:4, right:5}}
mpl_channel_config = {master:{left:0, right:1}, headphones:{left:4, right:5}}

pl_channel_config2 = {headphones:{left:0, right:1}}
mpl_channel_config2 = {master:{left:0, right:1}}

var pl = new PrecuePlayer() 
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

var mpl = new MainPlayer()
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
                                    current_queue_position = position;
                                    update_queue_labels();
                                    mpl.play(track[0])
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
    DB.get_track_by_id(id, (result) => {
        pl.play(result[0], stream_start, stream_end)
    })
}
