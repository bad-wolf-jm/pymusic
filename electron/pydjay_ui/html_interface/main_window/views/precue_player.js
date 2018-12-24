
Huebee = require("huebee")

class PrecuePlayerView extends EventDispatcher {
    constructor (track_list_model) {
        super()
        this.track_list_model = track_list_model
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
        document.getElementById("precue-player-track-progress").addEventListener("click", (e) => {
            let x = e.target.getBoundingClientRect()
            let mouseX = (e.clientX - x.left)
            let ratio = mouseX / x.width
            if (this.controller.track != undefined) {
                this.controller.play(this.controller.track,
                                     this.controller.track.stream_start +
                                        (this.controller.track.stream_length * ratio))
            }
        })

        this.hueb = new Huebee(document.getElementById("track-color-value"), {
            notation: "hex",
            saturations: 1
        })

        this.hueb.on( 'change', ( color, hue, sat, lum ) => {
            this.track_list_model.set_metadata(this._track, {color: color})
            this.hueb.close()
        })

        document.getElementById("precue-player-color").addEventListener("click", () => {
            this.hueb.open()
        })

        this.track_list_model.on("metadata-changed", (track) => {
            if (track.id == this._track.id) {
                this.set_track(track)
            }
        })
    }

    show_options() {
        document.getElementById("precue-dropdown").classList.toggle("show");
    }

    set_controller(controller) {
        this.controller = controller
        this.controller.on("stream-position", (pos_data) => {
            let pos = pos_data.position
            let duration = pos_data.duration
            let remaining = Math.abs(duration*1000 - pos)
            let percent = (pos*100 / (duration*1000))
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
                if (this.controller.track != undefined) {
                    this.controller.play(this.controller.track)
                }
            }
        })
        document.getElementById("precue-player-loved").addEventListener("click", () => {
            if (this._track != undefined) {
                this.updateLoved(!this._track.favorite)
            }
        })
    }

    set_unset() {
        document.getElementById("precue-player-play-button").innerHTML = `<i class="fa fa-play"></i>`
    }

    set_track(track) {
        let file_name = path.join(track.music_root, track.file_name);
        let stream_length = (track.stream_end-track.stream_start);
        document.getElementById("precue-player-title").innerHTML       = track.title
        document.getElementById("precue-player-album").innerHTML       = track.album
        document.getElementById("precue-player-artist").innerHTML      = track.artist
        document.getElementById("precue-player-genre").innerHTML       = track.genre
        document.getElementById("precue-player-last-played").innerHTML = track.last_played
        document.getElementById("precue-player-play-count").innerHTML  = track.play_count
        document.getElementById("precue-player-bpm").innerHTML         = track.bpm
        document.getElementById("precue-player-duration").innerHTML    = `${format_nanoseconds(stream_length)}`
        if (track.color == null) {
            document.getElementById("precue-player-color").style.background = "#ffffff"
        } else {
            document.getElementById("precue-player-color").style.background = track.color
        }
        this.setRating(track.rating)
        this.setLoved(track.favorite)
        let cover_source = undefined
        if (track.cover == null) {
            cover_source = "../../resources/images/default_album_cover.png"
        } else {
            cover_source = `file://${track.image_root}/${track.cover}`;
        }
        document.getElementById("precue-player-cover").src = cover_source
        this._track = track
        document.getElementById("no-preview-track").style.display = "none"
        document.getElementById("precue-dropdown").classList.remove("show")
    }

    setRating (num) {
        let html = "";
        for (let i=1; i<6; i++) {
            html+=`<i id='precue-rating-star-${i}' class='fa ` + ( i <= num ? "fa-star" : "fa-star-o") +`' style='margin-left:3px'></i>`;
        }
        document.getElementById("precue-player-rating").innerHTML = html
        for (let i=1; i<6; i++) {
            document.getElementById(`precue-rating-star-${i}`).addEventListener('click', () => {
                if (i == 1 && this._track.rating == 1) {
                    this.updateRating(0)
                } else {
                    this.updateRating(i)
                }
            })
        }
    }

    setLoved (value){
        var html = "";
        this.loved = value
        html+="<i title='"+value+"' class='fa " + (value ? "fa-heart" : "fa-heart-o") +"'></i>";
        document.getElementById("precue-player-loved").innerHTML = html
    }

    updateRating(new_value) {
        if (this.track_list_model != undefined) {
            this.track_list_model.set_metadata(this._track, {rating:new_value})
            // this.hueb.close()    
        }

        // DB.update_track_data(this._track.id, {rating:new_value}, () => {
        //     this._track.rating = new_value
        //     this.setRating(new_value)
        // })
    }

    updateLoved(new_value) {
        if (this.track_list_model != undefined) {
            this.track_list_model.set_metadata(this._track, {favorite:new_value})
            // this.hueb.close()    
        }

        // DB.update_track_data(this._track.id, {favorite:new_value}, () => {
        //     console.log(new_value)
        //     this._track.favorite = new_value
        //     this.setLoved(new_value)
        // })
    }
}
