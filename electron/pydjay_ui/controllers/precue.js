const {AudioTrackPlayer} = require("track_playback/track_player.js")

class PrecueController extends AudioTrackPlayer {
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
