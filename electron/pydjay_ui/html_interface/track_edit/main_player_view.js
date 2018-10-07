
pl_channel_config = {headphones:{left:4, right:5}}
mpl_channel_config = {master:{left:0, right:1}, headphones:{left:4, right:5}}

pl_channel_config2 = {headphones:{left:0, right:1}}
mpl_channel_config2 = {master:{left:0, right:1}}

class MainPlayerView extends PydjayAudioFilePlayer {
    constructor () {
        super()
        this.controller = undefined
        this.stream_start = 0
        this.stream_end = Infinity
        this.track_length = Infinity
        this.favorite = undefined
        this.rating = undefined
        this.current_stream_position = null
        this.audio_player = new PydjayAudioBufferPlayer()
        if (this.audio_player.audio_context.audio_ctx.destination.maxChannelCount == 6) {
            this.audio_player.connectOutputs(pl_channel_config)    
        } else {
            this.audio_player.connectOutputs(pl_channel_config2)    
        }

    }

    set_track(track) {
        let file_name = path.join(track.music_root, track.file_name);
        let stream_length = (track.stream_end-track.stream_start);
        document.getElementById("main-player-track-title").value  = track.title
        document.getElementById("main-player-track-album").value  = track.album
        document.getElementById("main-player-track-artist").value = track.artist
        document.getElementById("main-player-track-bpm").value    = track.bpm
        document.getElementById("main-player-track-genre").value  = track.genre
        document.getElementById("main-player-track-year").value   = track.year
        document.getElementById("main-player-track-start").innerHTML = `${format_nanoseconds(track.stream_start)}`
        document.getElementById("main-player-track-end").innerHTML   = `${format_nanoseconds(track.stream_end)}`
        document.getElementById("main-player-track-duration").innerHTML = `${format_nanoseconds(stream_length)}`

        document.getElementById("play-button").addEventListener("click", () => {
            if (this.audio_player.state == "PLAYING") {
                this.audio_player.stop()
                this.current_stream_position = null
                //$$(this.play_button_id).define("icon", "play")
                //$$(this.play_button_id).refresh()
            } else {
                let start;
                if (this.current_stream_position != null) {
                    start = this.current_stream_position * this._track.track_length  / 1000000               
                } else {
                    start = this.stream_start / 1000000
                }
                this.audio_player.play(this._waveform.backend.buffer, start, this.stream_end / 1000000)
                //$$(this.play_button_id).define("icon", "stop")
                //$$(this.play_button_id).refresh()
            }
            })

        document.getElementById("main-player-loved").addEventListener("click", () => {
            this.setLoved(!(this.loved))
        })


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
        this.stream_start = this._track.stream_start
        this.stream_end = this._track.stream_end
        this._position_tracker = this.audio_player.on("stream-position", (pos) => {
            this._waveform.seekAndCenter(pos*1000000 / this._track.track_length)
        })

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
                    container: `#main-player-waveform`,
                    deferInit: false,
                })
            ]
        });       
        this._waveform.on(
            "ready", () => {
                this._waveform.zoom(0)
                this._region = this._waveform.addRegion({
                    start: this._track.stream_start / 1000000000, 
                    end:   this._track.stream_end / 1000000000,
                    color: "rgba(25,100,0,0.5)"
                })
                //console.log(this._region)
                this._region.on("update", 
                    () => {
                        this.stream_start = Math.round(this._region.start * 1000000000)
                        this.stream_end = Math.round(this._region.end * 1000000000)
                        this.stream_length = this.stream_end - this.stream_start
                        document.getElementById("main-player-track-start").innerHTML = `${format_nanoseconds(this.stream_start)}`
                        document.getElementById("main-player-track-end").innerHTML   = `${format_nanoseconds(this.stream_end)}`
                        document.getElementById("main-player-track-duration").innerHTML   = `${format_nanoseconds(this.stream_length)}`
                    }
                )
            }
        )
        this._waveform.on(
            "seek", (p) => {
                this.current_stream_position = p
            }
        )


    }

    setRating (num) {
        this.rating = num
        var html = "";
        for (let i=1; i<6; i++) {
            html+=`<i id='rating-star-${i}' class='fa ${( i <= num ? "fa-star" : "fa-star-o")}' style='margin-left:3px'></i>`;
        }
        document.getElementById("main-player-rating").innerHTML = html
        for (let i=1; i<6; i++) {
            document.getElementById(`rating-star-${i}`).addEventListener('click', () => {
                if (i == 1 && this.rating == 1) {
                    this.setRating(0)
                } else {
                    this.setRating(i)
                }
            })
        }
    }
    
    setLoved (value) {
        var html = "";
        this.loved = value
        html+="<i title='"+value+"' class='fa " + (value ? "fa-heart" : "fa-heart-o") +"'></i>";
        document.getElementById("main-player-loved").innerHTML = html
    }

    getValues() {
        let F = (x) => document.getElementById(x)
        let v = {
            title:  F("main-player-track-title").value, 
            album:  F("main-player-track-album").value, 
            artist: F("main-player-track-artist").value,
            bpm:    F("main-player-track-bpm").value,
            genre:  F("main-player-track-genre").value,
            year:   F("main-player-track-year").value,
            stream_start: this.stream_start,
            stream_end:   this.stream_end,
            favorite:     this.loved,
            rating:       this.rating
        }
        v.year = (v.year != "") ? v.year : null
        return v
    }
}

// document.getElementById("main-player-track-start").innerHTML,
// document.getElementById("main-player-track-end").innerHTML,
// document.getElementById("main-player-track-duration").innerHTML,
