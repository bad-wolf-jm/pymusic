class MainPlayerView extends EventDispatcher {
    constructor (track_list_model) {
        super()
        this.controller = undefined
        this.track_list_model = track_list_model

        if (this.track_list_model != undefined) {
            this.track_list_model.on("metadata-changed", (track) => {
                if (this._track != undefined) {
                    if (track.id == this._track.id) {
                        this.set_track_metadata(track)
                    }
                }
            })
        }

        document.getElementById("main-player-loved").addEventListener("click", () => {
            if (this._track != undefined) {
                this.updateLoved(!this._track.favorite)
            }
        })
    }

    set_controller(controller) {
        this.controller = controller
        this.controller.on("stream-position", (pos) => {
            let remaining = Math.abs(pos.duration*1000 - pos.position)
            document.getElementById("main-player-time-remaining").innerHTML = `-${format_nanoseconds(remaining*1000000)}`
        })
        this.controller.on("queue-stopped",                this.set_queue.bind(this))
        this.controller.on("track-finished",                this.set_queue.bind(this))
        this.controller.on("track-started",                this.set_track.bind(this))
        this.controller.on("queue-finished",                this.set_queue.bind(this))
        this.controller.on("queue-stopped",                this.set_queue.bind(this))
        this.controller.on("queue-stop-requested",         this.set_queue.bind(this))
        this.controller.on("queue-stop-request-cancelled", this.set_queue.bind(this))
        this.controller.on("next-track-countdown",         this.set_queue.bind(this))
    }

    set_queue() {

    }

    set_track_metadata(track) {
        if (this._track != undefined && track.id == this._track.id) {
            let stream_length = (track.bounds.end-track.bounds.start);
            document.getElementById("main-player-track-title").innerHTML    = track.title
            document.getElementById("main-player-track-album").innerHTML    = track.album
            document.getElementById("main-player-track-artist").innerHTML   = track.artist
            document.getElementById("main-player-track-bpm").innerHTML      = track.bpm
            document.getElementById("main-player-track-duration").innerHTML = `${format_nanoseconds(stream_length)}`
            this.setRating(track.rating)
            this.setLoved(track.favorite)
            let cover_source = undefined
            if (track.cover == null) {
                cover_source = "../../resources/images/default_album_cover.png"
            } else {
                cover_source = `file://${track.cover.medium}`;
            }
            document.getElementById("main-player-track-cover").src = cover_source    
        }
    }

    set_track(track) {
        let file_name = track.path //path.join(track.music_root, track.file_name);
        this._track = track
        this.set_track_metadata(track)
        this._waveform.load(file_name)
    }

    init() {
        this._waveform = WaveSurfer.create({
            container:     `#main-player-waveform`,
            waveColor:     'violet',
            progressColor: 'purple',
            height:        40,
            barHeight:     1,
            plugins: [
                WaveSurferRegions.create({
                    container: `#${this.main_waveform_id}`,
                    deferInit: false,
                })
            ]
        });
        this._position_tracker = this.controller.on("stream-position",
            (pos) => {
                let p = pos.position*1000000 / this._track.duration
                p = Math.max(p,0.0)
                p = Math.min(p,1.0)
                this._waveform.seekAndCenter(p)
            }
        )
        this._waveform.on(
            "ready", () => {
                this._waveform.zoom(0)
                this.controller._do_start_playback(this._track)
            }
        )
    }

    setRating (num) {
        var html = "";
        for (var i=1; i<6; i++) {
            html+=`<i id='main-rating-star-${i}' class='fa ` + ( i <= num ? "fa-star" : "fa-star-o") +`' style='margin-left:3px'></i>`;
        }
        document.getElementById("main-player-rating").innerHTML = html
        for (let i=1; i<6; i++) {
            document.getElementById(`main-rating-star-${i}`).addEventListener('click', () => {
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
        document.getElementById("main-player-loved").innerHTML = html
    }

    updateRating(new_value) {
        if (this.track_list_model != undefined) {
            this.track_list_model.set_metadata(this._track, {rating:new_value})
        }
    }

    updateLoved(new_value) {
        if (this.track_list_model != undefined) {
            this.track_list_model.set_metadata(this._track, {favorite:new_value})
        }
    }

}
