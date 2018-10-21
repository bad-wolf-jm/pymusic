class MainPlayerView extends PydjayAudioFilePlayer {
    constructor () {
        super()
        this.controller = undefined
    }

    set_controller(controller) {
        this.controller = controller
        this.controller.on("stream-position", (pos) => {
            let remaining = Math.abs(this.controller.source.duration*1000 - pos)
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

    set_track(track) {
        let file_name = path.join(track.music_root, track.file_name);
        let stream_length = (track.stream_end-track.stream_start);
        document.getElementById("main-player-track-title").innerHTML    = track.title
        document.getElementById("main-player-track-album").innerHTML    = track.album
        document.getElementById("main-player-track-artist").innerHTML   = track.artist
        document.getElementById("main-player-track-bpm").innerHTML      = track.bpm
        document.getElementById("main-player-track-duration").innerHTML = `${format_nanoseconds(stream_length)}`
        this.setRating(track.rating)
        this.setLoved(track.favorite)
        let cover_source = undefined
        if (track.cover == null) {
            cover_source = "../../../resources/images/default_album_cover.png"
        } else {
            cover_source = `file://${track.image_root}/${track.cover}`;
        }
        document.getElementById("main-player-track-cover").src = cover_source
        this._track = track
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
                let p = pos*1000000 / this._track.track_length
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
            html+="<i class='fa " + ( i <= num ? "fa-star" : "fa-star-o") +"' style='margin-left:3px'></i>";
        }
        document.getElementById("main-player-rating").innerHTML = html
    }
    
    setLoved (value){
        var html = "";
        this.loved = value
        html+="<i title='"+value+"' class='fa " + (value ? "fa-heart" : "fa-heart-o") +"'></i>";
        document.getElementById("main-player-loved").innerHTML = html
    }
}