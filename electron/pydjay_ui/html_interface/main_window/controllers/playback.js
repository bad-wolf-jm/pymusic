// pl_channel_config = {headphones:{left:4, right:5}}
// mpl_channel_config = {master:{left:0, right:1}, headphones:{left:4, right:5}}

// pl_channel_config2 = {headphones:{left:0, right:1}}
// mpl_channel_config2 = {master:{left:0, right:1}}
const { RemoteTrackPlayer } = require("track_playback/remote_player/remote_player.js")


pl_channel_config = {headphones:{left:0, right:1}}
mpl_channel_config = {master:{left:4, right:5}, headphones:{left:0, right:1}}

pl_channel_config2 = {headphones:{left:0, right:1}}
mpl_channel_config2 = {master:{left:0, right:1}}

class PlaybackController extends RemoteTrackPlayer {
    constructor(session_controller, queue_controller) {
        super()
        this.views              = []
        //this.session_controller = session_controller
        this.queue_controller   = queue_controller
        this.stop_request       = false
        this.playing            = false
        this.on('track-finished', async (track) => {
                if (this.stop_request) {
                    this.queue_playing = false
                    this.stop_request = false
                    this.dispatch("queue-stopped")
                } else {
                    let time = await MDB.state.d.find({_id: "settings"})
                    this.play_next_track(time.track_gap || 2000)
                }
            })        
    }

    _do_start_playback(track) {
        this.play(track,  track.stream_start, track.stream_end)    
    }

    async _do_play_next_track() {
        let track = await this.queue_controller.pop()
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
                    this.dispatch('next-track-countdown', delay)
                    delay = delay - 1000;
                }
            }, 
            1000
        )    
    }

    async start_queue() {
        if (!this.queue_playing) {
            if (!(await this.queue_controller.is_empty())) {
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
        this.dispatch("queue-stopped")
    }

    skip_to_next_track() {
        if (this.queue_playing && !(this.stop_request)){
            if (this._current_track != undefined) {
                this._current_track.end_time = new Date()
                this._current_track.status = "skipped"
                this.dispatch("track-skipped", this._current_track)
                this.stop()
                this._current_track = undefined    
            }
            this.play_next_track(0)
        }
    }
}
