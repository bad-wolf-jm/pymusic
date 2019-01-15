const { ColorPicker } = require("ui/popup/colorpicker.js")
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
        this.audio_player.connectOutputs({headphones:{left:0, right:1}})

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

    async set_track(track) {
        // console.log(track)
        this.track = track
        let file_name = track.track.path //path.join(track.music_root, track.file_name);
        let stream_length = (track.track.stream_end-track.track.stream_start);
        document.getElementById("track-editor-track-title").value = track.metadata.title
        document.getElementById("track-editor-track-album").value = track.metadata.album
        document.getElementById("track-editor-track-artist").value = track.metadata.artist
        document.getElementById("track-editor-track-bpm").value = track.track.bpm
        document.getElementById("track-editor-track-genre").value = track.metadata.genre
        document.getElementById("track-editor-track-year").value = track.metadata.year
        document.getElementById("track-editor-track-start").innerHTML = `${format_nanoseconds(track.track.stream_start)}`
        document.getElementById("track-editor-track-end").innerHTML = `${format_nanoseconds(track.track.stream_end)}`
        document.getElementById("track-editor-track-duration").innerHTML = `${format_nanoseconds(stream_length)}`
        document.getElementById("track-editor-color").style.backgroundColor = track.metadata.color

        var slider = document.querySelector('#slider');
        slider.oninput =  () => {
            var zoomLevel = Number(slider.value);
            this._waveform.zoom(zoomLevel);
          };
        this.setRating(track.rating)
        this.setLoved(track.favorite)
        let cover_source = undefined
        if (track.metadata.cover == null) {
            cover_source = "../../resources/images/default_album_cover.png"
            this.original_cover_image = null
            this.cover_image = null
        } else {
            cover_source = `file://${track.metadata.cover.original}`;
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
            this._waveform.seekAndCenter(pos*1000000 / this._track.duration)
        })

        let related_tracks = Object.values(await MDB.tracks.getObjectsByIds(Object.keys(track.stats.relations)))
        let rows = related_tracks.map((track) => {
            return {
                id:          track._id,
                color:       track.color,
                loved:       "<i title='"+track._id+"' class='fa " + (track.stats.loved ? "fa-heart" : "fa-heart-o") +"'></i>",
                title:       track.metadata.title,
                artist:      track.metadata.artist,
                genre:       track.metadata.genre,
                last_played: (track.stats.last_played != null) ? moment(track.stats.last_played).format('MM-DD-YYYY') : "",
                play_count:  track.stats.play_count,
                rating:      this._get_rating(track),
                bpm:         track.track.bpm,
                duration:    format_nanoseconds(track.track.stream_end - track.track.stream_start),
            }
        })
        jui.ready([ "grid.table" ], (table) => {
            var queue_content = table("#related-elements", {
                data:   rows,
                scroll: false,
                resize: false
            });
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
                    start: this._track.track.stream_start / 1000000000,
                    end:   this._track.track.stream_end / 1000000000,
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
            html+="<i class='fa " + ( j <= track_object.stats.rating ? "fa-star" : "fa-star-o") +"' style='font-size:8pt; margin-left:3px; color: rgb(70,70,70);'></i>";
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
            "metadata.title": F("track-editor-track-title").value,
            "metadata.album": F("track-editor-track-album").value,
            'metadata.artist': F("track-editor-track-artist").value,
            "track.bpm": F("track-editor-track-bpm").value,
            "metadata.genre": F("track-editor-track-genre").value,
            "metadata.year": F("track-editor-track-year").value,
            "metadata.color": this.color, 
            "track.stream_start": this.stream_start,
            "track.stream_end": this.stream_end,
            "stats.loved": this.loved,
            "stats.rating": this.rating
        }
        v.cover_image = this.cover_image
        v['metadata.year'] = (v['metadata.year'] != "") ? v['metadata.year'] : null
        v['track.bpm'] = (v['track.bpm'] != "") ? v['track.bpm'] : null
        return v
    }


    close() {
        this.audio_player.stop()
        document.getElementById("track-edit-dialog").close()
    }
    
    save() {
        let file_path = this.track.track.path
        let file_dir = path.dirname(file_path)
        let cover_dir = path.join(file_dir, ".covers")
        let new_values = this.getValues()
        if (new_values.cover_image != null) {
            new_values["metadata.album.cover.original"] = path.join(cover_dir, `cover_original_${this.track._id}`),
            new_values["metadata.album.cover.large"] = path.join(cover_dir, `cover_large_${this.track._id}`),
            new_values["metadata.album.cover.medium"] = path.join(cover_dir, `cover_medium_${this.track._id}`),
            new_values["metadata.album.cover.small"] = path.join(cover_dir, `cover_small_${this.track._id}`)    
            new_values.cover_image.write(new_values["metadata.album.cover.original"]);
            new_values.cover_image.resize(320,320).write(new_values["metadata.album.cover.large"])
            new_values.cover_image.resize(160,160).write(new_values["metadata.album.cover.medium"])
            new_values.cover_image.resize(100,100).write(new_values["metadata.album.cover.small"])
        } else if (new_values.cover_image !== undefined) {
            new_values.cover = undefined
        }
        MDB.tracks.setTrackMetadata(this.track, new_values)
        if (new_values.cover == undefined) {
            MDB.tracks.d.update({_id: this.track.id}, {$unset: {cover: true}})
        }
        this.close()
    }
    
}
