pl_channel_config = {headphones:{left:4, right:5}}
mpl_channel_config = {master:{left:0, right:1}, headphones:{left:4, right:5}}

pl_channel_config2 = {headphones:{left:0, right:1}}
mpl_channel_config2 = {master:{left:0, right:1}}


class PlaybackController extends PydjayAudioFilePlayer {
    constructor(session_controller, queue_controller) {
        super()
        this.views              = []
        this.session_controller = session_controller
        this.queue_controller   = queue_controller
        this.stop_request       = false
        this.playing            = false
        this.on('end-of-stream', () => {
                this.session_controller.add(this._current_track)
                if (this.stop_request) {
                    this.queue_playing = false
                    this.stop_request = false
                    this.dispatch("queue-stopped")
                } else {
                    this.dispatch("track-finished")
                }
            }
        )        
    }

    reset_audio() {
        let url = undefined
        if (mpl.source != undefined) {
            time     = this.source.currentTime * 1000
            end_time = this.stream_end
            url      = this.url
            this.stop()
        }
        this.reset_audio_context()
        this.init_audio()
        if (url != undefined) {
            this.play(url, time, end_time)
        }
    }
    
    init_audio() {
        if (this.audio_context.audio_ctx.destination.maxChannelCount == 6) {
            this.connectOutputs(mpl_channel_config)
        } else {
            this.connectOutputs(mpl_channel_config2)
        }
    }

    _do_start_playback(track) {
        console.log(track)
        let file_name = path.join(track.music_root, track.file_name);
        this.play(file_name,  track.stream_start / 1000000, track.stream_end / 1000000)    
    }

    _do_play_next_track() {
        let track = this.queue_controller.pop()
        if (track != undefined) {
            this.dispatch("track-started", track)
        } else {
            this.dispatch("queue-finished")
        }
    }

    play_next_track(delay) {
        var id = setInterval(
             () => {
                if (delay <= 0) {
                    clearInterval(id);
                    this._do_play_next_track();
                } else {
                    this.dispatch('next-track-countdown', delay)
                    delay--;
                }
            }, 
            1000
        )    
    }

    start_queue() {
        if (!this.queue_playing) {
            this._do_play_next_track()
            this.dispatch("queue-started")
        } else {
            if (!this.stop_request){
                this.stop_request = true;
                this.dispatch("queue-stop-requested")
            } else {
                this.stop_request = false;
                this.dispatch("queue-stop-request-cancelled")
            }
        }
    }

    stop_queue_now() {
        this.queue_playing = false;
        this.stop_request = false;
        this.dispatch("queue-stopped")
    }

    skip_to_next_track() {
        if (this.queue_playing && !(this.stop_request)){
            this.stop()
            this.play_next_track(0)
        }
    }
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
    DB.mark_as_played(queue_position,
        function (error, result) {
            DB.get_waiting_time(
                (t) => {
                    continuation(t)
                }
            )
        }
    )
}
