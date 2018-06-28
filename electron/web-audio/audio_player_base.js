class PydjayAudioBasePlayer extends EventDispatcher {
    constructor() {
        super()
        this.state = "STOPPED"
        this.url = null
        this.source = null
        this.stream_start = null
        this.stream_end = null
        this.stream_position = null
        this.stream_start_timestamp = null
        this.stream_pause_time = 0
        this.stream_elapsed_time = 0
        this.total_pause_time = 0
        this.output_channel_layout = null
        this.audio_context = new PydjayAudioContext()
        this.audio_context.on("timestamp", x => this.updateStreamPosition(x))
        this.input_type = null
    }

    reset_audio_context() {
        this.audio_context.audio_ctx.close()
        this.audio_context.un("timestamp") 
        this.audio_context = new PydjayAudioContext()
        this.audio_context.on("timestamp", x => this.updateStreamPosition(x))
    }

    play(start_time, end_time) {
        this.stop()
        this.stream_start_timestamp = this.audio_context.audio_ctx.currentTime * 1000
        this.stream_pause_time = 0
        this.total_pause_time = 0
        this.stream_elapsed_time = 0
        this.stream_start = (start_time != undefined) ? start_time : 0
        this.stream_end = end_time
        this.state = "PLAYING"
        this.dispatch("playback-started")
    }

    seek(timestamp) {
        this.stream_start = timestamp * 1000    
    }

    skip(delta) {
        this.stream_start += (delta*1000)    
    }

    pause() {
        if (this.state == "PLAYING"){
            this.dispatch("playback-paused")
            this.state = "PAUSED"
            this.pause_time = this.stream_elapsed
        }
    }

    resume() {
        if (this.state == "PAUSED") {
            this.total_pause_time += (this.audio_context.audio_ctx.currentTime*1000 - this.stream_start_timestamp -this.pause_time)
            this.stream_pause_time = 0
            this.state = "PLAYING"
            this.dispatch("playback-started")
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
        this.source = null
        this.stream_position = null
        this.stream_start = null
        this.stream_end = null
        this.stream_start_timestamp = null
        this.total_pause_time = 0
        this.state = "STOPPED"
        this.dispatch("playback-stopped")
    }

    onStreamEnded() {
        this.stop()
        this.dispatch("end-of-stream")
    }

    setVolume(channel_name, ch, gain_value) {
        if (this.output_channel_layout != null) {
            let channel = this.output_channel_layout[channel_name]
            if (channel != undefined) {
                let l = channel[ch]
                this.audio_context.gain_controls[l].gain.value = gain_value
                this.dispatch('volume-set', channel_name, ch, gain_value)
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
        if ((this.stream_start_timestamp != null)) {
            let stream_elapsed = (playback_time * 1000) - this.stream_start_timestamp
            let stream_position = stream_elapsed + this.stream_start
            this.stream_elapsed = Math.round(stream_elapsed)
            stream_position = Math.round(stream_position)
            if ((stream_position != this.stream_position) && (this.state == "PLAYING")) {
                this.stream_position = stream_position - this.total_pause_time
                this.dispatch("stream-position", this.stream_position)
                if ((this.stream_end != undefined) && (this.stream_position > this.stream_end)) {
                    this.stop()
                    this.onStreamEnded()
                }    
            }
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
