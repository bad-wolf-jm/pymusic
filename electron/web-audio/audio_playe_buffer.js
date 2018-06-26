class PydjayAudioBufferPlayer extends PydjayAudioBasePlayer {
    constructor() {
        super()
        // this.state = "STOPPED"
        // this.url = null
        // this.source = null
        // this.stream_start = null
        // this.stream_end = null
        // this.stream_position = null
        // this.stream_start_timestamp = null
        // this.stream_pause_time = 0
        // this.stream_elapsed_time = 0
        // this.total_pause_time = 0
        // this.output_channel_layout = null
        // this.audio_context = new PydjayAudioContext()
        // this.audio_context.on("timestamp", x => this.updateStreamPosition(x))
        // this.input_type = null
    }

    // play(url, start_time, end_time) {
    //     this.stop()
    //     this.source = new Audio()
    //     this.source.src = url
    //     this.source.onended = () => {this.onStreamEnded()}
    //     this.stream_start_timestamp = this.audio_context.audio_ctx.currentTime * 1000
    //     this.stream_pause_time = 0
    //     this.total_pause_time = 0
    //     this.stream_elapsed_time = 0
    //     let x = this.audio_context.audio_ctx.createMediaElementSource(this.source)
    //     x.channelInterpretation = "discrete"
    //     x.connect(this.audio_context.splitter)
    //     this.stream_start = (start_time != undefined) ? start_time : 0
    //     this.source.currentTime = this.stream_start / 1000
    //     this.source.play()
    //     this.state = "PLAYING"
    //     this.stream_end = end_time
    //     this.input_type = "FILE"
    //     this.url = url
    //     this.dispatch("playback-started")
    // }

    play(buffer, start_time, end_time) {
        super.play(start_time, end_time)
        // this.stop()
        this.buffer = buffer
        this.source = this.audio_context.audio_ctx.createBufferSource()
        // this.stream_start_timestamp = this.audio_context.audio_ctx.currentTime * 1000
        // this.stream_pause_time = 0
        // this.total_pause_time = 0
        // this.stream_elapsed_time = 0

        this.source.buffer = buffer
        this.source.channelInterpretation = "discrete"
        this.source.connect(this.audio_context.splitter)
        // this.stream_start = (start_time != undefined) ? start_time : 0
        // this.stream_end = end_time
        // //this.source.currentTime = this.stream_start / 1000
        this.source.start(0, this.stream_start / 1000)
        // this.state = "PLAYING"
        // this.input_type = "BUFFER"
        // this.dispatch("playback-started")
    }

    seek(timestamp) {
        super.seek(timestamp)
        if (this.source != null) {
            // if (this.input_type == "FILE") {
            //     this.source.currentTime = timestamp
            //     this.stream_start = timestamp * 1000    
            // } else {
            this.stream_start = timestamp * 1000 
            this.playBuffer(this.url, this.stream_start * 1000)
            // }
        }
    }

    skip(delta) {
        super.skip(delta)
        if (this.source != null) {
            // if (this.input_type == 'FILE') {
            //     this.source.currentTime += delta
            //     this.stream_start += (delta*1000)    
            // } else {
                //this.stream_start += (delta*1000)
                //console.log(this.stream_start)
            let pos = this.stream_position + delta*1000
            this.stop()
            this.playBuffer(this.url, pos)
            // }
        }
    }

    pause() {
        if (this.state == "PLAYING"){
            // this.dispatch("playback-paused")
            // this.state = "PAUSED"
            // this.pause_time = this.stream_elapsed
            super.pause()
            if (this.source != null) {
                // if (this.source.pause){
                //     this.source.pause()
                // } else {
                this.source.stop()
                // }
            }
        }
    }

    resume() {
        super.resume()
        if (this.state == "PAUSED") {
            // this.total_pause_time += (this.audio_context.audio_ctx.currentTime*1000 - this.stream_start_timestamp -this.pause_time)
            // this.stream_pause_time = 0
            // this.state = "PLAYING"
            // if (this.source.play) {
            //     this.source.play()
            // } else {
            this.play(this.buffer, this.stream_position)
            // }
            this.dispatch("playback-started")
        }
    }

    // togglePause() {
    //     if (this.state == "PLAYING") {
    //         this.pause()
    //     } else {
    //         this.resume()
    //     }
    // }

    stop() {
        if (this.source != null) {
            // if (this.source.pause){
            //     this.source.pause()
            // } else {
            this.source.stop()
            // }
        }
        super.stop()
        // this.source = null
        // this.stream_position = null
        // this.stream_start = null
        // this.stream_end = null
        // this.stream_start_timestamp = null
        // this.total_pause_time = 0
        // this.state = "STOPPED"
        // this.dispatch("playback-stopped")
    }

    // onStreamEnded() {
    //     this.stop()
    //     this.dispatch("end-of-stream")
    // }

    // setVolume(channel_name, ch, gain_value) {
    //     if (this.output_channel_layout != null) {
    //         let channel = this.output_channel_layout[channel_name]
    //         if (channel != undefined) {
    //             let l = channel[ch]
    //             this.audio_context.gain_controls[l].gain.value = gain_value
    //             this.dispatch('volume-set', channel_name, ch, gain_value)
    //         }
    //     }
    // }

    // getVolume(channel_name, ch) {
    //     if (this.output_channel_layout != null) {
    //         let channel = this.output_channel_layout[channel_name]
    //         if (channel != undefined) {
    //             let l = channel[ch]
    //             return this.audio_context.gain_controls[l].gain.value = gain_value
    //         }
    //     }
    // }

    // updateStreamPosition(playback_time) {
    //     if ((this.stream_start_timestamp != null)) {
    //         let stream_elapsed = (playback_time * 1000) - this.stream_start_timestamp
    //         let stream_position = stream_elapsed + this.stream_start
    //         this.stream_elapsed = Math.round(stream_elapsed)
    //         stream_position = Math.round(stream_position)
    //         //console.log(stream_position, this.state)
    //         if ((stream_position != this.stream_position) && (this.state == "PLAYING")) {
    //             this.stream_position = stream_position - this.total_pause_time
    //             //console.log(this.stream_position)
    //             this.dispatch("stream-position", this.stream_position)
    //             if ((this.stream_end != undefined) && (this.stream_position > this.stream_end)) {
    //                 this.stop()
    //                 this.onStreamEnded()
    //             }    
    //         }
    //     } else {
    //         this.stream_position = undefined
    //     }
    // }

    // connectOutputs(channel_config) {
    //     this.pause()
    //     this.output_channel_layout = channel_config
    //     this.audio_context.connectOutputs(channel_config)
    //     this.resume()
    // }
}
