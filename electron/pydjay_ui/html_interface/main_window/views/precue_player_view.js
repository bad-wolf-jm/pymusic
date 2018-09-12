class PrecuePlayerView extends EventDispatcher {
    constructor () {
        super()
        this.controller = undefined
    }

    set_controller(controller) {
        this.controller = controller
        this.controller.on("stream-position", (pos) => {
            let remaining = Math.abs(this.controller.source.duration*1000 - pos)
        })
        this.controller.on("track-finished", this.set_queue.bind(this))
        this.controller.on("track-started", this.set_track.bind(this))
    }

    set_track(track) {
        let file_name = path.join(track.music_root, track.file_name);
        let stream_length = (track.stream_end-track.stream_start);
        // document.getElementById("main-player-track-title").innerHTML    = track.title
        document.getElementById("precue-player-title").innerHTML       = track.title
        document.getElementById("precue-player-album").innerHTML       = track.album
        document.getElementById("precue-player-artist").innerHTML      = track.artist
        document.getElementById("precue-player-genre").innerHTML       = track.genre
        document.getElementById("precue-player-last-played").innerHTML = track.last_played
        document.getElementById("precue-player-play-count").innerHTML  = track.play_count
        document.getElementById("precue-player-bpm").innerHTML  = track.bpm
        document.getElementById("precue-player-duration").innerHTML    = `${format_nanoseconds(stream_length)}`
        this.setRating(track.rating)
        this.setLoved(track.favorite)
        let cover_source = undefined
        if (track.cover == null) {
            cover_source = "../../../resources/images/default_album_cover.png"
        } else {
            cover_source = `file://${track.image_root}/${track.cover}`;
        }
        document.getElementById("precue-player-cover").src = cover_source
        this._track = track
        //this._waveform.load(file_name)
    }

    setRating (num) {
        var html = "";
        for (var i=1; i<6; i++) {
            html+="<i class='fa " + ( i <= num ? "fa-star" : "fa-star-o") +"' style='margin-left:3px'></i>";
        }
        document.getElementById("main-player-rating").innerHTML = html
    }
    
    setLoved (value){
        var html = "";
        this.loved = value
        html+="<i title='"+i+"' class='fa " + (value ? "fa-heart" : "fa-heart-o") +"'></i>";
        document.getElementById("main-player-loved").innerHTML = html
    }
}