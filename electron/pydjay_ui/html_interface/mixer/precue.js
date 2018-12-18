// pl_channel_config = {headphones:{left:4, right:5}}
// mpl_channel_config = {master:{left:2, right:3}, headphones:{left:4, right:5}}

// pl_channel_config2 = {headphones:{left:0, right:1}}
// mpl_channel_config2 = {master:{left:0, right:1}}


class PrecueController extends PydjayAudioFilePlayer {
    constructor() {
        super()
        this.views = []
        this.on('end-of-stream', () => {
            ipcRenderer.send("headphone-end-of-stream", {})
        })

        this.on('playback-stopped',  () => {
            ipcRenderer.send("headphone-playback-stopped", {})
        })
    
        this.on('playback-paused', () => {
            ipcRenderer.send("headphone-playback-paused", {})
        })
        
        this.on('playback-started', () => {
            ipcRenderer.send("headphone-playback-started", {})
        })

        this.on('stream-position', (pos) => {
            ipcRenderer.send("headphone-stream-position", {position: pos, duration:this.source.duration})
        })
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
        console.log(this.audio_context.audio_ctx.destination.maxChannelCount)

        if (this.audio_context.audio_ctx.destination.maxChannelCount >= 6) {
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