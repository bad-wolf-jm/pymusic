class PrecuePlayerView extends EventDispatcher {
    constructor () {
        super()
        this.controller = undefined
        document.getElementById("precue-options").addEventListener('click', this.show_options.bind(this))

        document.getElementById("precue-play-full-track").addEventListener('click', () => {
            this.controller.play(this.controller.track)
        })
        document.getElementById("precue-play-last-30-seconds").addEventListener('click', () => {
            this.controller.play_last_30_seconds(this.controller.track)
        })
        document.getElementById("precue-play-last-10-seconds").addEventListener('click', () => {
            this.controller.play_last_10_seconds(this.controller.track)
        })
        document.getElementById("precue-play-stop").addEventListener('click', () => {
            this.controller.stop()
            document.getElementById("precue-dropdown").classList.remove("show")
        })
    }

    show_options() {
        document.getElementById("precue-dropdown").classList.toggle("show");
    }

    set_controller(controller) {
        this.controller = controller
        this.controller.on("stream-position", (pos) => {
            let remaining = Math.abs(this.controller.source.duration*1000 - pos)
            let percent = (pos*100 / (this.controller.source.duration*1000))
            if (isFinite(percent)) {
                document.getElementById("precue-player-track-progress").value = percent;
            }
        })
        this.controller.on("track-finished", this.set_unset.bind(this))
        this.controller.on("track-started", this.set_track.bind(this))
        this.controller.on("playback-paused", () => {
            document.getElementById("precue-player-play-button").innerHTML = `<i class="fa fa-play"></i>`
        })
        this.controller.on("playback-stopped", () => {
            document.getElementById("precue-player-play-button").innerHTML = `<i class="fa fa-play"></i>`
        })
        this.controller.on("playback-started", () => {
            document.getElementById("precue-player-play-button").innerHTML = `<i class="fa fa-pause"></i>`
        })
        document.getElementById("precue-player-play-button").addEventListener('click', () => {
            if ((this.controller.state == "PAUSED") || (this.controller.state == "PLAYING")) {
                this.controller.togglePause()
            } else {
                if (controller.track != undefined) {
                    this.controller.play(this.controller.track)
                }
            }
        })
    }

    set_unset() {
        document.getElementById("precue-player-play-button").innerHTML = `<i class="fa fa-play"></i>`
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
        document.getElementById("precue-player-bpm").innerHTML         = track.bpm
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
        document.getElementById("no-preview-track").style.display = "none"
        document.getElementById("precue-dropdown").classList.remove("show")
        //this._waveform.load(file_name)
    }

    setRating (num) {
        var html = "";
        for (let i=1; i<6; i++) {
            html+="<i class='fa " + ( i <= num ? "fa-star" : "fa-star-o") +"' style='margin-left:3px'></i>";
        }
        document.getElementById("precue-player-rating").innerHTML = html
    }
    
    setLoved (value){
        var html = "";
        this.loved = value
        html+="<i title='"+value+"' class='fa " + (value ? "fa-heart" : "fa-heart-o") +"'></i>";
        document.getElementById("precue-player-loved").innerHTML = html
    }
}