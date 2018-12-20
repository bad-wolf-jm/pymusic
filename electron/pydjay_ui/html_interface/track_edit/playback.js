// pl_channel_config = {headphones:{left:4, right:5}}
// mpl_channel_config = {master:{left:0, right:1}, headphones:{left:4, right:5}}

// pl_channel_config2 = {headphones:{left:0, right:1}}
// mpl_channel_config2 = {master:{left:0, right:1}}

// pl_channel_config = {headphones:{left:0, right:1}}
// mpl_channel_config = {master:{left:4, right:5}, headphones:{left:0, right:1}}

// pl_channel_config2 = {headphones:{left:0, right:1}}
// mpl_channel_config2 = {master:{left:0, right:1}}


class PrecueController extends EventDispatcher {
    constructor() {
        super()
        this.track = 
        this.views = []
        // ipsRenderer.on()
        this.on('end-of-stream', () => {
                this.dispatch("end-of-stream")
            }
        )

        ipcRenderer.on("headphone-playback-stopped", () => {
            this.dispatch("playback-stopped")
        })
        
        
        ipcRenderer.on("headphone-playback-paused", () => {
            this.dispatch("playback-paused")
        })
        
        ipcRenderer.on("headphone-playback-started", () => {
            this.dispatch("playback-started")
        })
        
        ipcRenderer.on("headphone-stream-position", (event, pos) => {
            this.dispatch("stream-position", pos)
        })
        
    }

    reset_audio() {
        // let url = undefined, time=undefined, end_time=undefined
        // if (this.source != undefined) {
        //     time     = this.source.currentTime * 1000
        //     end_time = this.stream_end
        //     url      = this.url
        //     this.stop()
        // }
        // this.reset_audio_context()
        // this.init_audio()
        // if (url != undefined) {
        //     super.play(url, time, end_time)
        // }
    }

    init_audio() {
        // if (this.audio_context.audio_ctx.destination.maxChannelCount == 6) {
        //     this.connectOutputs(pl_channel_config)
        // } else {
        //     this.connectOutputs(pl_channel_config2)
        // }
    }

    togglePause() {
        if (this.state == 'PLAYING') {
            ipcRenderer.send("mixer-pause", {channel: "headphones"})
            this.state = 'PAUSED'
        } else if (this.state == 'PAUSED') {
            ipcRenderer.send("mixer-resume", {channel: "headphones"})
            this.state = 'PLAYING'
        } else {

        }
    }

    stop() {
        ipcRenderer.send("mixer-stop", {channel: "headphones"})
        this.state = 'STOPPED'
    }

    play(track, stream_start, stream_end) {
        this.track = track
        ipcRenderer.send("mixer-play", {
            track: this.track,
            stream_start: stream_start,
            stream_end: stream_end,
            channel: "headphones"
        })
        this.state = "PLAYING"
        this.dispatch("track-started", track)
        // let file_name = path.join(this.track.music_root, this.track.file_name);
        // if (stream_start == undefined) {
        //     stream_start = this.track.stream_start
        //     stream_end = this.track.stream_end
        // } else if (stream_end == undefined) {
        //     stream_end = this.track.stream_end
        //     if (stream_start < 0) {
        //         stream_start = stream_end + stream_start;
        //     }
        // }
        // super.play(file_name, stream_start / 1000000, stream_end / 1000000)
    }

    // play_last_10_seconds(track) {
    //     if (track != undefined) {
    //         this.play(track, -10000000000)
    //     } else if (this.track != undefined) {
    //         this.play(this.track, -10000000000)
    //     } else {

    //     }
    // }

    // play_last_30_seconds(track) {
    //     if (track != undefined) {
    //         this.play(track, -30000000000)
    //     } else if (this.track != undefined) {
    //         this.play(this.track, -30000000000)
    //     }
    // }

}
