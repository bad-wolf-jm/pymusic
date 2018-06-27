class PydjayAudioBufferPlayer extends PydjayAudioBasePlayer {
    constructor() {
        super()
    }

    play(buffer, start_time, end_time) {
        super.play(start_time, end_time)
        this.buffer = buffer
        this.source = this.audio_context.audio_ctx.createBufferSource()
        this.source.buffer = buffer
        this.source.channelInterpretation = "discrete"
        this.source.connect(this.audio_context.splitter)
        this.source.start(0, this.stream_start / 1000)
    }

    seek(timestamp) {
        super.seek(timestamp)
        if (this.source != null) {
            this.stream_start = timestamp * 1000 
            this.play(this.url, this.stream_start * 1000)
        }
    }

    skip(delta) {
        super.skip(delta)
        if (this.source != null) {
            let pos = this.stream_position + delta*1000
            this.stop()
            this.playBuffer(this.url, pos)
        }
    }

    pause() {
        if (this.state == "PLAYING"){
            if (this.source != null) {
                this.source.stop()
            }
        }
        super.pause()
    }

    resume() {
        if (this.state == "PAUSED") {
            this.play(this.buffer, this.stream_position)
            this.dispatch("playback-started")
        }
        super.resume()
    }

    stop() {
        if (this.source != null) {
            this.source.stop()
        }
        super.stop()
    }
}
