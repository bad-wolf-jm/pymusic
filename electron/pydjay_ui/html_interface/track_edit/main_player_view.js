
// pl_channel_config = {headphones:{left:4, right:5}}
// mpl_channel_config = {master:{left:0, right:1}, headphones:{left:4, right:5}}

// pl_channel_config2 = {headphones:{left:0, right:1}}
// mpl_channel_config2 = {master:{left:0, right:1}}

//const {remote} = require('electron')
const {Menu, MenuItem} = require('electron').remote
var Jimp = require("jimp");


function rgb2hex(rgb) {
    rgb = rgb.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);
    function hex(x) {
        return ("0" + parseInt(x).toString(16)).slice(-2);
    }
    return "#" + hex(rgb[1]) + hex(rgb[2]) + hex(rgb[3]);
} 
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
        this.cover_image = undefined
        this.original_cover_image = null

        this.audio_player = new PydjayAudioBufferPlayer()
        this.audio_player.connectOutputs({headphones:{left:0, right:1}})    


        // this.audio_player = new PydjayAudioBufferPlayer()
        // if (this.audio_player.audio_context.audio_ctx.destination.maxChannelCount == 6) {
        //     this.audio_player.connectOutputs(pl_channel_config)    
        // } else {
        //     this.audio_player.connectOutputs(pl_channel_config2)    
        // }


        // if (this.audio_player.audio_context.audio_ctx.destination.maxChannelCount >= 6) {
        // } else {
        //     this.audio_player.connectOutputs(pl_channel_config2)    
        // }

        this.menu = new Menu()
        this.menu.append(new MenuItem({label: 'Change', click: () => {
            remote.dialog.showOpenDialog({ properties: ['openFile']}, (files) => {
                if ((files != undefined)) {
                    let new_cover = files[0]
                    Jimp.read(new_cover, (error, image) => {
                        if (!error) {
                            document.getElementById('main-player-track-cover').src = new_cover
                            this.cover_image = image    
                        }
                    })
                }
            })
        }}))
        // this.menu = new Menu()
        this.menu.append(new MenuItem({label: 'Revert to original', click: () => {
            // remote.dialog.showOpenDialog({ properties: ['openFile']}, (files) => {
            //     if ((files != undefined)) {
            //         let new_cover = files[0]
            let cover_source;
            if (this.original_cover_image == null) {
                cover_source = "../../resources/images/default_album_cover.png"
                this.cover_image = null
            } else {
                cover_source = this.original_cover_image;
                this.cover_image = null
            }
                //Jimp.read(this.original_cover_image, (error, image) => {
                //if (!error) {
            document.getElementById('main-player-track-cover').src = cover_source
            //        this.cover_image = null
            //    }
            //})
            //     }
            // })
        }}))


        this.menu.append(new MenuItem({label: 'Remove cover art', click: () => {
            let cover_source;
            cover_source = "../../resources/images/default_album_cover.png"
            this.cover_image = null
            document.getElementById('main-player-track-cover').src = cover_source
        }}))



        document.getElementById("main-player-track-cover").addEventListener("contextmenu", (e) => {
            this.menu.popup({window: remote.getCurrentWindow()})
        })

        document.getElementById("color-swatch-list").addEventListener("click", (e) => {
            let cp = document.getElementById("track-edit-color-chooser")
            //let track = this.controller.get_id(this.color_picker_track_id)
            //let x = e.target
            this.color = rgb2hex(e.target.style.backgroundColor)
            let x = document.getElementById("main-player-color")
            x.style.backgroundColor = this.color
            //this.controller.set_metadata(track, {color: rgb2hex(color)})
            cp.classList.remove("show")
        })

        document.getElementById("remove-color").addEventListener("click", (e) => {
            let cp = document.getElementById("track-edit-color-chooser")
            this.color = null
            let x = document.getElementById("main-player-color")
            x.style.backgroundColor = this.color
            //let track = this.controller.get_id(this.color_picker_track_id)
            //this.controller.set_metadata(track, {color: null})
            cp.classList.remove("show")
        })
 

        document.getElementById("main-player-color").addEventListener("click", (ev) => {
            let e = document.getElementById("main-player-color")
            //let track_id = parseInt(e.attributes['data-track-id'].value)
            let cp = document.getElementById("track-edit-color-chooser")
            let button_rect = e.getBoundingClientRect()
            //let scroller = document.getElementById("main-track-list-scroller")
            //let scroller_rect = scroller.getBoundingClientRect()
            //let button_offset = (button_rect.top - scroller_rect.top)

            //if (button_offset + 100 > scroller_rect.height) {
            // cp.className = "overlay-color-picker-bottom" + (cp.classList.contains("show") ? " show" : "")
            let button_offset = (button_rect.bottom - 200 + 25) 
            cp.style.top = (button_offset)+"px"
            //} else {
            //    let button_offset_to_frame = (button_rect.top - 100 +5) // + 53 + 25 - 100)
            //    cp.className = "overlay-color-picker-middle" + (cp.classList.contains("show") ? " show" : "")
            //    cp.style.top = (button_offset_to_frame)+"px"
           // }
            cp.style.left = (button_rect.left - 150)+"px"
            cp.style.top = button_rect.bottom + 17+"px"
            cp.classList.toggle("show")
            // this.color_picker_track_id = track_id
            // ev.preventDefault()
        })
    //})})


        this.audio_player.on("playback-started", () => {
            ipcRenderer.send("playback-started")
        })

        this.audio_player.on("playback-paused", () => {
            ipcRenderer.send("playback-stopped")
        })
        
        this.audio_player.on("playback-stopped", () => {
            ipcRenderer.send("playback-stopped")
        })
    }

    set_track(track) {
        let file_name = path.join(track.music_root, track.file_name);
        let stream_length = (track.stream_end-track.stream_start);
        document.getElementById("main-player-track-title").value = track.title
        document.getElementById("main-player-track-album").value = track.album
        document.getElementById("main-player-track-artist").value = track.artist
        document.getElementById("main-player-track-bpm").value = track.bpm
        document.getElementById("main-player-track-genre").value = track.genre
        document.getElementById("main-player-track-year").value = track.year
        document.getElementById("main-player-track-start").innerHTML = `${format_nanoseconds(track.stream_start)}`
        document.getElementById("main-player-track-end").innerHTML = `${format_nanoseconds(track.stream_end)}`
        document.getElementById("main-player-track-duration").innerHTML = `${format_nanoseconds(stream_length)}`
        document.getElementById("main-player-color").style.backgroundColor = track.color
        document.getElementById("play-button").addEventListener("click", () => {
            let start;
            if (this.audio_player.state == "PLAYING") {
                this.audio_player.stop()
                this.current_stream_position = null
            } else {
                if (this.current_stream_position != null) {
                    start = this.current_stream_position * this._track.track_length  / 1000000               
                } else {
                    start = this.stream_start / 1000000
                }
                if (this.stream_end == Infinity) {
                    this.audio_player.play(this._waveform.backend.buffer, start, this._track.stream_end)
                } else {
                    this.audio_player.play(this._waveform.backend.buffer, start, this.stream_end)
                }
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
            cover_source = "../../resources/images/default_album_cover.png"
            this.original_cover_image = null
            this.cover_image = null
        } else {
            cover_source = `file://${track.image_root}/${track.cover_original}`;
            this.original_cover_image = cover_source
            this.cover_image = undefined
        }
        document.getElementById("main-player-track-cover").src = cover_source
        this._track = track
        this._waveform.load(file_name)
        this.stream_start = this._track.stream_start
        this.stream_end = this._track.stream_end
        this._position_tracker = this.audio_player.on("stream-position", (pos) => {
            this.current_stream_position = pos*1000000
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
                this._region.on("update", 
                    () => {
                        this.stream_start = Math.round(this._region.start * 1000000000)
                        this.stream_end = Math.round(this._region.end * 1000000000)
                        this.stream_length = this.stream_end - this.stream_start
                        document.getElementById("main-player-track-start").innerHTML = `${format_nanoseconds(this.stream_start)}`
                        document.getElementById("main-player-track-end").innerHTML = `${format_nanoseconds(this.stream_end)}`
                        document.getElementById("main-player-track-duration").innerHTML = `${format_nanoseconds(this.stream_length)}`
                    }
                )
            }
        )
        this._waveform.on(
            "seek", (p) => {
                //console.log(p)
                this.current_stream_position = p
                // let s = (p * this._track.track_length)
                // this.current_stream_position = s
                // if (this.audio_player.state == "PLAYING") {
                //     this.audio_player.play(this._track, s, this._track.stream_end)
                // }
            }
        )
        //     }
        // )


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
            color:  this.color, //F("main-player-color").style.backgroundColor,
            stream_start: this.stream_start,
            stream_end:   this.stream_end,
            favorite:     this.loved,
            rating:       this.rating
        }
        v.cover = this.cover_image
        v.year = (v.year != "") ? v.year : null
        v.bpm = (v.bpm != "") ? v.bpm : null
        return v
    }
}
