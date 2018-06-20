class PydjayAudioContext extends EventDispatcher{
    constructor() {
        super()
        this.audio_ctx =  new AudioContext()
        this.audio_ctx.destination.channelCount = this.audio_ctx.destination.maxChannelCount
        this.audio_ctx.destination.channelInterpretation = "discrete"
        this.createSplitter()
        this.createMerger()
        this.createGainControls()
        this.time_callback = null
        this.time_monitor = this.audio_ctx.createScriptProcessor(256, 1, 1)
        this.time_monitor.onaudioprocess = () => {
            this.dispatch("timestamp", this.audio_ctx.currentTime)
            // (this.time_callback != null) && this.time_callback(this.audio_ctx.currentTime)
        }
        this.merger.connect(this.time_monitor).connect(this.audio_ctx.destination)
        this.merger.connect(this.audio_ctx.destination)
        this.source = null;
    }

    createSplitter() {
        this.splitter = this.audio_ctx.createChannelSplitter(this.audio_ctx.destination.maxChannelCount)
        this.splitter.channelInterpretation = "discrete"
    }

    createMerger() {
        this.merger = this.audio_ctx.createChannelMerger(this.audio_ctx.destination.maxChannelCount)
        this.merger.channelInterpretation = "discrete"
    }

    createGainControls() {
        this.gain_controls = []
        let i=0
        for (i=0; i < this.audio_ctx.destination.maxChannelCount; i++) {
            let g = this.audio_ctx.createGain()
            g.connect(this.merger, 0, i)
            this.gain_controls.push(g)
        }
    }

    connectOutputs(channel_layout) {
        let channel_names = Object.keys(channel_layout)
        this.splitter.disconnect()
        for (let i=0; i<channel_names.length; i++) {
            let channel_data = channel_layout[channel_names[i]]
            this.splitter.connect(this.gain_controls[channel_data.left], 0, 0)
            this.splitter.connect(this.gain_controls[channel_data.right], 1, 0)
        }
    }

    // setTimeMonitor(callback) {
    //     this.time_callback = callback
    // }
}
