class MainPlayerView extends PydjayAudioFilePlayer {
    constructor () {
        super()
        this.controller = undefined
    }

    set_track(track) {
        let file_name = path.join(track.music_root, track.file_name);
        let stream_length = (track.stream_end-track.stream_start);
        document.getElementById("main-player-track-title").innerHTML    = track.title
        document.getElementById("main-player-track-album").innerHTML    = track.album
        document.getElementById("main-player-track-artist").innerHTML   = track.artist
        document.getElementById("main-player-track-bpm").innerHTML      = track.bpm
        document.getElementById("main-player-track-genre").innerHTML    = track.genre
        document.getElementById("main-player-track-year").innerHTML     = track.year
        // document.getElementById("main-player-track-last-played").innerHTML = moment(track.last_played).fromNow()
        document.getElementById("main-player-track-start").innerHTML    = `${format_nanoseconds(track.stream_start)}`
        document.getElementById("main-player-track-end").innerHTML      = `${format_nanoseconds(track.stream_end)}`
        document.getElementById("main-player-track-duration").innerHTML = `${format_nanoseconds(stream_length)}`

        var slider = document.querySelector('#slider');
        slider.oninput =  () => {
            var zoomLevel = Number(slider.value);
            this._waveform.zoom(zoomLevel);
          };
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
            height:        150,
            barHeight:     1.25,
            plugins: [
                WaveSurferRegions.create({
                    container: `#${this.main_waveform_id}`,
                    deferInit: false,
                })
            ]
        });       
        this._waveform.on(
            "ready", () => {
                this._waveform.zoom(0)
                //this.controller._do_start_playback(this._track)
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