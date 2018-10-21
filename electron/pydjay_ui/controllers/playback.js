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
        this._current_track     = undefined
        this.on('end-of-stream', () => {
                this._current_track.end_time = new Date()
                this._current_track.status = "ended"
                this.session_controller.add(this._current_track)
                this._current_track = undefined
                this.dispatch("track-finished")
                if (this.stop_request) {
                    this.queue_playing = false
                    this.stop_request = false
                    this.dispatch("queue-stopped")
                } else {
                    DB.get_waiting_time(
                        (wait_time) => {
                            mpc.play_next_track(wait_time)
                        }
                    )
                }
            }
        )        
    }

    reset_audio() {
        let url = undefined, time=undefined, end_time=undefined
        if (this.source != undefined) {
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
        console.log(this.audio_context.audio_ctx.destination.maxChannelCount)
        if (this.audio_context.audio_ctx.destination.maxChannelCount == 6) {
            this.connectOutputs(mpl_channel_config)
        } else {
            this.connectOutputs(mpl_channel_config2)
        }
    }

    _do_start_playback(track) {
        let file_name = path.join(track.music_root, track.file_name);
        this._current_track = {
            start_time: new Date(),
            end_time: undefined,
            status: undefined,
            track_id: track.id
        }
        this.play(file_name,  track.stream_start / 1000000, track.stream_end / 1000000)    
    }

    _do_play_next_track() {
        let track = this.queue_controller.pop()
        if (track != undefined) {
            this.queue_playing = true
            this.dispatch("track-started", track)
        } else {
            this.queue_playing = false
            this.dispatch("queue-finished")
        }
    }

    play_next_track(delay) {
        var id = setInterval(
             () => {
                if (delay <= 0) {
                    clearInterval(id);
                    this.dispatch('next-track-countdown', 0)
                    this._do_play_next_track();
                } else {
                    // console.log(delay)
                    this.dispatch('next-track-countdown', delay)
                    delay--;
                }
            }, 
            1000
        )    
    }

    start_queue() {
        if (!this.queue_playing) {
            if (!(this.queue_controller.is_empty())) {
                this._do_play_next_track()
                this.dispatch("queue-started")    
            }
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
        this.stop()
        if (this._current_track != undefined) {
            this._current_track.end_time = new Date()
            this._current_track.status = "stopped"
            this.session_controller.add(this._current_track)
            this._current_track = undefined    
        }
        this.dispatch("queue-stopped")
    }

    skip_to_next_track() {
        if (this.queue_playing && !(this.stop_request)){
            this.stop()
            if (this._current_track != undefined) {
                this._current_track.end_time = new Date()
                this._current_track.status = "skipped"
                this.session_controller.add(this._current_track)
                this._current_track = undefined    
            }
            this.play_next_track(0)
        }
    }
}
