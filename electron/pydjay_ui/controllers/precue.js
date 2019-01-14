class PrecueController extends PydjayAudioFilePlayer {
    constructor() {
        super()
        this.views              = []
        this.on('end-of-stream', () => {
                this.dispatch("track-finished")
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
            super.play(url, time, end_time)
        }
    }
    
    init_audio() {
        if (this.audio_context.audio_ctx.destination.maxChannelCount == 6) {
            this.connectOutputs({headphones:{left:0, right:1}})
        } else {
            this.connectOutputs({headphones:{left:0, right:1}})
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

    play_last_10_seconds(track) {
        if (track != undefined) {
            this.play(track, -10000000000)
        } else if (this.track != undefined) {
            this.play(this.track, -10000000000)
        } else {

        }
    }

    play_last_30_seconds(track) {
        if (track != undefined) {
            this.play(track, -30000000000)
        } else if (this.track != undefined) {
            this.play(this.track, -30000000000)
        }
    }

}
