class PydjayAudioPlayer {
    constructor() {
        this.state = "STOPPED"
        this.url = null
        this.source = null
        this.stream_start = null
        this.stream_end = null
        this.stream_position = null
        this.stream_start_timestamp = null
        this.output_channel_layout = null
        this.audio_context = new PydjayAudioContext()
        this.audio_context.setTimeMonitor(x => this.updateStreamPosition(x))
    }

    play(url, start_time, end_time) {
        this.stop()
        this.source = new Audio()
        this.source.src = url
        this.source.onended = () => {this.onStreamEnded()}
        this.stream_start_timestamp = this.audio_context.audio_ctx.currentTime * 1000
        let x = this.audio_context.audio_ctx.createMediaElementSource(this.source)
        x.channelInterpretation = "discrete"
        x.connect(this.audio_context.splitter)
        this.stream_start = (start_time != undefined) ? start_time : 0
        //this.source.fastSeek(this.stream_start / 1000)
        this.source.currentTime = this.stream_start / 1000
        this.source.play()
        this.state = "PLAYING"
        this.stream_end = end_time
    }

    pause() {
        if (this.state == "PLAYING"){
            this.state = "PAUSED"
            if (this.source != null) {
                this.source.pause()
            }
        }
    }

    resume() {
        if (this.state == "PAUSED") {
            this.source.play()
            this.state = "PLAYING"
        }
    }

    togglePause() {
        if (this.state == "PLAYING") {
            this.pause()
        } else {
            this.resume()
        }
    }

    stop() {
        (this.source != null) && this.source.pause()
        this.source = null
        this.stream_position = null
        this.stream_start = null
        this.stream_end = null
        this.stream_start_timestamp = null
        this.state = "STOPPED"
    }

    onStreamEnded() {
        console.log("stream end")
        this.stop()
    }

    setVolume(channel_name, ch, gain_value) {
        if (this.output_channel_layout != null) {
            let channel = this.output_channel_layout[channel_name]
            if (channel != undefined) {
                let l = channel[ch]
                this.audio_context.gain_controls[l].gain.value = gain_value
            }
        }
    }

    getVolume(channel_name, ch) {
        if (this.output_channel_layout != null) {
            let channel = this.output_channel_layout[channel_name]
            if (channel != undefined) {
                let l = channel[ch]
                return this.audio_context.gain_controls[l].gain.value = gain_value
            }
        }
    }

    updateStreamPosition(playback_time) {
        if (this.stream_start_timestamp != null) {
            this.stream_position = playback_time * 1000 - this.stream_start_timestamp + this.stream_start
            if ((this.stream_end != undefined) && (this.stream_position > this.stream_end)) {
                this.stop()
                this.onStreamEnded()
            }
            //console.log((this.source.duration * 1000 -  this.stream_position).toFixed(1))
        } else {
            this.stream_position = undefined
        }
    }

    connectOutputs(channel_config) {
        this.pause()
        this.output_channel_layout = channel_config
        this.audio_context.connectOutputs(channel_config)
        this.resume()
    }
}
