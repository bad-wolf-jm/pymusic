const {AudioTrackPlayer} = require("track_playback/track_player.js")

class PrecueController extends AudioTrackPlayer {

    constructor() {
        super()
        this.addOutput("main")
        super.setOutputDeviceId('main', 'null')
    }

    setOutputDeviceId(deviceId) {
        // console.log(deviceId)
        (deviceId != this.getOutputDeviceId()) && super.setOutputDeviceId("main", deviceId)
    }

    getOutputDeviceId() {
        return super.getOutputDeviceIds()["main"] //, deviceId)
    }

    play_last_10_seconds(track) {
        console.log(track)
        this.track = track
        if (track != undefined) {
            this.play(track, -10000)
        } else if (this.track != undefined) {
            this.play(this.track, -10000)
        } else {

        }
    }

    play_last_30_seconds(track) {
        console.log(track)
        if (track != undefined) {
            this.play(track, -30000)
        } else if (this.track != undefined) {
            this.play(this.track, -30000)
        }
    }

}
