class PydjayAudioFilePlayer extends PydjayAudioBasePlayer {
    constructor() {
        super()
    }

    play(url, start_time, end_time) {
        super.play(start_time, end_time)
        this.url = url
        this.source = new Audio()
        this.source.src = url
        this.source.onended = () => {this.onStreamEnded()}
        let x = this.audio_context.audio_ctx.createMediaElementSource(this.source)
        x.channelInterpretation = "discrete"
        x.connect(this.audio_context.splitter)
        this.source.currentTime = this.stream_start / 1000
        this.source.play()
    }

    seek(timestamp) {
        super.seek(timestamp)
        if (this.source != null) {
            this.source.currentTime = timestamp
            this.stream_start = timestamp * 1000    
        }
    }

    skip(delta) {
        super.skip(delta)
        if (this.source != null) {
            this.source.currentTime += delta
        }
    }

    pause() {
        if (this.state == "PLAYING"){
            if (this.source != null) {
                this.source.pause()
            }
        }
        super.pause()
    }

    resume() {
        if (this.state == "PAUSED") {
            this.source.play()
        }
        super.resume()
    }

    stop() {
        if (this.source != null) {
            this.source.pause()
        }
        super.stop()
    }
}
