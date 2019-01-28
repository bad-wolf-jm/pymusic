
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
            let t = this.controller._current_track.track_object
            if (t != undefined) {
                this.controller.play(t, t.track.stream_start + ((t.track.stream_end - t.track.stream_start) * ratio))
            }
        })

        this.track_list_model.on("object-updated", (track) => {
            if (this._track != undefined) {
                if (track._id == this._track._id) {
                    this.update_track(track)
                }    
            }
        })
    }

    show_options() {
        document.getElementById("precue-dropdown").classList.toggle("show");
    }

    set_controller(controller) {
        this.controller = controller
        this.controller.on("stream-position", (pos) => {
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
                if (this.controller.track != undefined) {
                    this.controller.play(this.controller.track)
                }
            }
        })
        document.getElementById("precue-player-loved").addEventListener("click", () => {
            if (this._track != undefined) {
                this.updateLoved(!this._track.stats.loved)
            }
        })
    }

    set_unset() {
        document.getElementById("precue-player-play-button").innerHTML = `<i class="fa fa-play"></i>`
    }

    update_track(track) {
        let stream_length = (track.track.stream_end - track.track.stream_start);
        this._track = track
        document.getElementById("precue-player-title").innerHTML       = track.metadata.title
        document.getElementById("precue-player-album").innerHTML       = track.metadata.album
        document.getElementById("precue-player-artist").innerHTML      = track.metadata.artist
        document.getElementById("precue-player-genre").innerHTML       = track.metadata.genre
        document.getElementById("precue-player-last-played").innerHTML = track.stats.last_played
        document.getElementById("precue-player-play-count").innerHTML  = track.stats.play_count
        document.getElementById("precue-player-bpm").innerHTML         = track.track.bpm
        document.getElementById("precue-player-duration").innerHTML    = `${format_nanoseconds(stream_length)}`
        this.setRating(track.stats.rating)
        this.setLoved(track.stats.loved)
        let cover_source = undefined
        if (track.metadata.cover == null) {
            cover_source = "../../resources/images/default_album_cover.png"
        } else {
            cover_source = `file://${track.metadata.cover.small}`;
        }
        document.getElementById("precue-player-cover").src = cover_source
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
                if (i == 1 && this._track.stats.rating == 1) {
                    this.updateRating(0)
                } else {
                    this.updateRating(i)
                }
            })
        }
    }


    set_track(tr) {
        // console.log(tr)
        this.update_track(tr.track_object)
    }

    setLoved (value){
        var html = "";
        this.loved = value
        html+="<i title='"+value+"' class='fa " + (value ? "fa-heart" : "fa-heart-o") +"'></i>";
        document.getElementById("precue-player-loved").innerHTML = html
    }

    updateRating(new_value) {
        if (this.track_list_model != undefined) {
            this.track_list_model.setTrackMetadata(this._track, {'stats.rating':new_value})
        }
    }

    updateLoved(new_value) {
        if (this.track_list_model != undefined) {
            this.track_list_model.setTrackMetadata(this._track, {'stats.loved':new_value})
        }
    }
}
