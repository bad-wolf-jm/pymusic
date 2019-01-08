const {AudioTrackPlayer} = require('track_playback/track_player.js')


mpl_channel_config = {master:{left:4, right:5}, headphones:{left:0, right:1}}
mpl_channel_config2 = {master:{left:0, right:1}}


class PlaybackController extends AudioTrackPlayer {
    constructor() {
        super()
        this.playing            = false

        this.monitor_set_volume = 1;
        this.monitor_volume = 1;
        this.monitor_muted_volume = 0;


        this.on('end-of-stream', () => {
            ipcRenderer.send("master-end-of-stream", {})
        })

        this.on('playback-stopped',  () => {
            ipcRenderer.send("master-playback-stopped", {})
        })
    
        this.on('playback-paused', () => {
            ipcRenderer.send("master-playback-paused", {})
        })
        
        this.on('playback-started', () => {
            ipcRenderer.send("master-playback-started", {})
        })

        this.on('stream-position', (pos) => {
            ipcRenderer.send("master-stream-position", {position: pos, duration:this.source.duration})
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
            this.play(url, time, end_time)
        }
    }
    
    init_audio() {
        if (this.audio_context.audio_ctx.destination.maxChannelCount >= 6) {
            this.connectOutputs(mpl_channel_config)
        } else {
            this.connectOutputs(mpl_channel_config2)
        }
    }

    mute_monitor() {
        var a_monitor_volume = {volume: this.monitor_volume};
        $(a_monitor_volume).animate(
            {volume: this.monitor_muted_volume},
            {
                duration:100,
                step: (now, tween) => {
                    this.set_monitor_volume(now);
                },
            }
        )
    }

    set_monitor_volume(value) {
        this.setVolume('headphones', 'left', value)
        this.setVolume('headphones', 'right', value)
    }

        
    restore_monitor() {
        var a_monitor_volume = {volume: this.monitor_volume};
        $(a_monitor_volume).animate(
            {volume: this.monitor_set_volume},
            {
                duration:100,
                step: (now, tween) => {
                    this.set_monitor_volume(now);
                },
            }
        )
    }
}
