pl_channel_config = {headphones:{left:4, right:5}}
mpl_channel_config = {master:{left:0, right:1}, headphones:{left:4, right:5}}

pl_channel_config2 = {headphones:{left:0, right:1}}
mpl_channel_config2 = {master:{left:0, right:1}}


class PrecueController extends PydjayAudioFilePlayer {
    constructor() {
        super()
        this.views              = []
        // this.session_controller = session_controller
        // this.queue_controller   = queue_controller
        // this.stop_request       = false
        // this.playing            = false
        this.on('end-of-stream', () => {
                this.dispatch("track-finished")
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
            this.connectOutputs(pl_channel_config)
        } else {
            this.connectOutputs(pl_channel_config2)
        }
    }

    play(track, stream_start, stream_end) {
        this.track = track
        let file_name = path.join(this.track.music_root, this.track.file_name);
        if (stream_start == undefined) {
            stream_start = this.track.stream_start
            stream_end = this.track.stream_end
        } else if (stream_end == undefined) {  
            stream_end = this.track.stream_end
            if (stream_start < 0) {
                stream_start = stream_end + stream_start;
            }
        }
        this.dispatch("track-started", track)
        super.play(file_name, stream_start / 1000000, stream_end / 1000000)
    }
}
