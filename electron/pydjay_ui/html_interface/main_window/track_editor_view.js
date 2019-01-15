const { ColorPicker } = require("ui/popup/colorpicker.js")
//const {EventDispatcher} = require("notify/event_dispatcher.js")
const { PydjayAudioBufferPlayer } = require("webaudio/audio_player_buffer.js")

function rgb2hex(rgb) {
    rgb = rgb.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);
    function hex(x) {
        return ("0" + parseInt(x).toString(16)).slice(-2);
    }
    return "#" + hex(rgb[1]) + hex(rgb[2]) + hex(rgb[3]);
}
class TrackEditorView extends EventDispatcher {
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
        this.audio_player.addOutput("headphones")
        this.setOutputDeviceId("null")
        // this.audio_player.connectOutputs({headphones:{left:0, right:1}})

        this.menu = new Menu()
        this.menu.append(new MenuItem({label: 'Change', click: () => {
            remote.dialog.showOpenDialog({ properties: ['openFile']}, (files) => {
                if ((files != undefined)) {
                    let new_cover = files[0]
                    Jimp.read(new_cover, (error, image) => {
                        if (!error) {
                            document.getElementById('track-editor-track-cover').src = new_cover
                            this.cover_image = image
                        }
                    })
                }
            })
        }}))
        this.menu.append(new MenuItem({label: 'Revert to original', click: () => {
            let cover_source;
            if (this.original_cover_image == null) {
                cover_source = "../../resources/images/default_album_cover.png"
                this.cover_image = null
            } else {
                cover_source = this.original_cover_image;
                this.cover_image = null
            }
            document.getElementById('track-editor-track-cover').src = cover_source
        }}))


        this.menu.append(new MenuItem({label: 'Remove cover art', click: () => {
            let cover_source;
            cover_source = "../../resources/images/default_album_cover.png"
            this.cover_image = null
            document.getElementById('track-editor-track-cover').src = cover_source
        }}))



        document.getElementById("track-editor-track-cover").addEventListener("contextmenu", (e) => {
            this.menu.popup({window: remote.getCurrentWindow()})
        })

        document.getElementById("track-editor-color").addEventListener("click", (ev) => {
            let e = document.getElementById("track-editor-color")

            if (this.color_chooser != undefined) {
                this.color_chooser.close()
                this.color_chooser = undefined
            } else {
                this.color_chooser = new ColorPicker(document.getElementById("track-edit-dialog"), {
                    cancel: () => {
                        this.color_chooser.close()
                        this.color_chooser = undefined
                    },
                    chooseColor: (color) => {
                        this.color = color
                        let x = document.getElementById("track-editor-color")
                        x.style.backgroundColor = this.color
                        this.color_chooser.close()
                        this.color_chooser = undefined
                    }                    
                })
                this.color_chooser.open(e)
            }

        })

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

        document.getElementById("track-editor-loved").addEventListener("click", () => {
            this.setLoved(!(this.loved))
        })

        document.getElementById("track-editor-save").addEventListener("click", (ev) => {
            this.save()
        })

        document.getElementById("track-editor-cancel").addEventListener("click", (ev) => {
            this.close()
        })


        // this.audio_player.on("playback-started", () => {
        //     ipcRenderer.send("playback-started")
        // })

        // this.audio_player.on("playback-paused", () => {
        //     ipcRenderer.send("playback-stopped")
        // })

        // this.audio_player.on("playback-stopped", () => {
        //     ipcRenderer.send("playback-stopped")
        // })
    }

    setOutputDeviceId(deviceId) {
        this.audio_player.setOutputDeviceId("headphones", deviceId)
    }

    getOutputDeviceId() {
        return this.audio_player.getOutputDeviceIds()["headphones"]
    }


    set_track(track) {
        this.track = track
        let file_name = path.join(track.music_root, track.file_name);
        let stream_length = (track.stream_end-track.stream_start);
        document.getElementById("track-editor-track-title").value = track.title
        document.getElementById("track-editor-track-album").value = track.album
        document.getElementById("track-editor-track-artist").value = track.artist
        document.getElementById("track-editor-track-bpm").value = track.bpm
        document.getElementById("track-editor-track-genre").value = track.genre
        document.getElementById("track-editor-track-year").value = track.year
        document.getElementById("track-editor-track-start").innerHTML = `${format_nanoseconds(track.stream_start)}`
        document.getElementById("track-editor-track-end").innerHTML = `${format_nanoseconds(track.stream_end)}`
        document.getElementById("track-editor-track-duration").innerHTML = `${format_nanoseconds(stream_length)}`
        document.getElementById("track-editor-color").style.backgroundColor = track.color

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
        document.getElementById("track-editor-track-cover").src = cover_source
        this._track = track
        this._waveform.load(file_name)
        this.stream_start = this._track.stream_start
        this.stream_end = this._track.stream_end
        this._position_tracker = this.audio_player.on("stream-position", (pos) => {
            this.current_stream_position = pos*1000000
            this._waveform.seekAndCenter(pos*1000000 / this._track.track_length)
        })

        DB.get_related_tracks(track.id, (queue) => {
            DB.get_playback_history(track.id, (history) => {
                let queue_rows = []
                for(let i=0; i<queue.length; i++) {
                    let element = {
                        id:          queue[i].id,
                        available:   queue[i].available,
                        color:       queue[i].color,
                        loved:       "<i title='"+i+"' class='fa " + (queue[i].favorite ? "fa-heart" : "fa-heart-o") +"'></i>",
                        title:       queue[i].title,
                        artist:      queue[i].artist,
                        genre:       queue[i].genre,
                        last_played: (queue[i].last_played != null) ? moment(queue[i].last_played).format('MM-DD-YYYY') : "",
                        play_count:  queue[i].play_count,
                        rating:      this._get_rating(queue[i]),
                        bpm:         queue[i].bpm,
                        duration:    format_nanoseconds(queue[i].stream_length),
                    }
                    queue_rows.push(element)
                }
                jui.ready([ "grid.table" ], (table) => {
                    var queue_content = table("#related-elements", {
                        data:   queue_rows,
                        scroll: false,
                        resize: false
                    });
                    var history_content = table("#playback-history", {
                        data:   history,
                        scroll: false,
                        resize: false
                    })
                })
            })
        })
    }


    init() {
        this._waveform = WaveSurfer.create({
            container:     `#track-editor-waveform`,
            waveColor:     'grey',
            progressColor: 'black',
            height:        100,
            barHeight:     1.25,
            plugins: [
                WaveSurferRegions.create({
                    container: `#track-editor-waveform`,
                    deferInit: false,
                })
            ]
        });
        this._waveform.on(
            "ready", () => {
                this._waveform.zoom(0)
                if (this._region != undefined) {
                    this._waveform.clearRegions()
                }
                this._region = this._waveform.addRegion({
                    start: this._track.stream_start / 1000000000,
                    end:   this._track.stream_end / 1000000000,
                    color: "rgba(25,25,25,0.35)"
                })
                this._region.on("update",
                    () => {
                        this.stream_start = Math.round(this._region.start * 1000000000)
                        this.stream_end = Math.round(this._region.end * 1000000000)
                        this.stream_length = this.stream_end - this.stream_start
                        document.getElementById("track-editor-track-start").innerHTML = `${format_nanoseconds(this.stream_start)}`
                        document.getElementById("track-editor-track-end").innerHTML = `${format_nanoseconds(this.stream_end)}`
                        document.getElementById("track-editor-track-duration").innerHTML = `${format_nanoseconds(this.stream_length)}`
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


    _get_rating(track_object) {
        let html = "";
        for (let j=1; j<6; j++) {
            html+="<i class='fa " + ( j <= track_object.rating ? "fa-star" : "fa-star-o") +"' style='font-size:8pt; margin-left:3px; color: rgb(70,70,70);'></i>";
        }
        return html
    }
    
    setRating (num) {
        this.rating = num
        var html = "";
        for (let i=1; i<6; i++) {
            html+=`<i id='rating-star-${i}' class='fa ${( i <= num ? "fa-star" : "fa-star-o")}' style='margin-left:3px; color:rgb(70,70,70);'></i>`;
        }
        document.getElementById("track-editor-rating").innerHTML = html
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
        html+="<i title='"+value+"' class='fa " + (value ? "fa-heart" : "fa-heart-o") +"', style='color:rgb(70,70,70);'></i>";
        document.getElementById("track-editor-loved").innerHTML = html
    }

    getValues() {
        let F = (x) => document.getElementById(x)
        let v = {
            title:  F("track-editor-track-title").value,
            album:  F("track-editor-track-album").value,
            artist: F("track-editor-track-artist").value,
            bpm:    F("track-editor-track-bpm").value,
            genre:  F("track-editor-track-genre").value,
            year:   F("track-editor-track-year").value,
            color:  this.color, 
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


    close() {
        this.audio_player.stop()
        document.getElementById("track-edit-dialog").close()
    }
    
    save() {
        DB.get_settings((settings) => {
            let new_values = this.getValues()
            let image_root = `${settings.image_root}`
            if (new_values.cover != null) {
                new_values.cover_original = `cover_original_${track_id}`
                new_values.cover_large    = `cover_large_${track_id}`
                new_values.cover_medium   = `cover_medium_${track_id}`
                new_values.cover_small    = `cover_small_${track_id}`
                new_values.cover.write(`${path.join(settings.image_root, new_values.cover_original)}`);
                new_values.cover.resize(320,320).write(`${path.join(settings.image_root, new_values.cover_large)}`)
                new_values.cover.resize(160,160).write(`${path.join(settings.image_root, new_values.cover_medium)}`)
                new_values.cover.resize(100,100).write(`${path.join(settings.image_root, new_values.cover_small)}`)
            } else if (new_values.cover !== undefined) {
                new_values.cover_original = null;
                new_values.cover_large    = null;
                new_values.cover_medium   = null;
                new_values.cover_small    = null;
            }
    
            tracks_model.set_metadata(this.track, new_values)
            this.close()
        })
    }
    
}
