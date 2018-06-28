function edit_track_data(id) {
    DB.get_track_by_id(id, 
        function (t) {
            t = t[0]
            t.file_name = path.join(t.music_root, t.file_name);
            t.stream_length = t.stream_end - t.stream_start
            if (t.cover != null) {
                t.cover_small = path.join(t.image_root, t.cover);
                t.cover_medium = path.join(t.image_root, t.cover);
                t.cover_large = path.join(t.image_root, t.cover);
                t.cover_original = path.join(t.image_root, t.cover);
            }
            var edit_window = new TrackEditWindow(pl)
            edit_window.on("accept-changes", (info) => DB.update_track_data(id, info, (x) => {}))
            edit_window.show(t)
            pl.stop()
        }
    )
}




class TrackEditWindow extends EventDispatcher {

    ID () {
        return '_' + Math.random().toString(36).substr(2, 9);
      };

    show(track_info) {
        this._win = webix.ui(this.layout)
        this._track_info = track_info
        this._win.attachEvent("onShow", () => this.load_window_content())
        webix.UIManager.addHotKey("escape", () => this.dismissChanges(), $$(this.id));
        webix.UIManager.addHotKey("enter", () => this.play_track(), $$(this.id));
        webix.UIManager.addHotKey("shift+enter", () => this.play_last_10_seconds(), $$(this.id));
        webix.UIManager.addHotKey("ctrl+shift+enter", () => this.play_last_30_seconds(), $$(this.id));
        webix.UIManager.addHotKey("space", () => this.pause_playback(), $$(this.id));
        webix.UIManager.addHotKey("shift+left", () => this.preview_backward_seek_short(), $$(this.id));
        webix.UIManager.addHotKey("shift+right", () => this.preview_forward_seek_short(), $$(this.id));
        webix.UIManager.addHotKey("ctrl+shift+left", () => this.preview_backward_seek_long(), $$(this.id));
        webix.UIManager.addHotKey("ctrl+shift+right", () => this.preview_forward_seek_long(), $$(this.id));
        webix.UIManager.addHotKey("ctrl+x", () => this.zoom_waveform_last_10_seconds(), $$(this.id));
        webix.UIManager.addHotKey("ctrl+z", () => this.zoom_waveform_first_10_seconds(), $$(this.id));
        webix.UIManager.addHotKey("shift+c", () => this.set_start_marker(), $$(this.id));
        webix.UIManager.addHotKey("shift+h", () => this.move_start_marker_backward_long(), $$(this.id));
        webix.UIManager.addHotKey("shift+j", () => this.move_start_marker_forward_long(), $$(this.id));
        webix.UIManager.addHotKey("shift+n", () => this.move_start_marker_backward_short(), $$(this.id));
        webix.UIManager.addHotKey("shift+m", () => this.move_start_marker_forward_short(), $$(this.id));
        webix.UIManager.addHotKey("ctrl+shift+c", () => this.set_end_marker(), $$(this.id));
        webix.UIManager.addHotKey("ctrl+shift+h", () => this.move_end_marker_backward_long(), $$(this.id));
        webix.UIManager.addHotKey("ctrl+shift+j", () => this.move_end_marker_forward_long(), $$(this.id));
        webix.UIManager.addHotKey("ctrl+shift+n", () => this.move_end_marker_backward_short(), $$(this.id));
        webix.UIManager.addHotKey("ctrl+shift+m", () => this.move_end_marker_forward_short(), $$(this.id));
        // webix.UIManager.addHotKey("ctrl+plus", () => this.zoom_in(), $$(this.id));
        // webix.UIManager.addHotKey("ctrl+minus", () => this.zoom_out(), $$(this.id));
        this._win.show()
    }


    play_last_30_seconds() {
        this.audio_player.play(this._waveform.backend.buffer, this.stream_end / 1000000 - 30000, this.stream_end / 1000000)
    }

    play_last_10_seconds() {
        this.audio_player.play(this._waveform.backend.buffer, this.stream_end / 1000000 - 10000, this.stream_end / 1000000)
    }

    play_track() {
        if (this.audio_player.state == "PLAYING") {
            this.audio_player.stop()
            this.current_stream_position = null
            $$(this.play_button_id).define("icon", "play")
            $$(this.play_button_id).refresh()
        } else {
            let start;
            if (this.current_stream_position != null) {
                start = this.current_stream_position * this._track_info.track_length  / 1000000               
            } else {
                start = this.stream_start / 1000000
            }
            this.audio_player.play(this._waveform.backend.buffer, start, this.stream_end / 1000000)
            $$(this.play_button_id).define("icon", "stop")
            $$(this.play_button_id).refresh()
        }
    }

    pause_playback() {
        this.audio_player.togglePause()
    }

    preview_forward_seek_short() {
        this.audio_player.skip(5)
    }

    preview_forward_seek_long() {
        this.audio_player.skip(20)
    }

    preview_backward_seek_short() {
        this.audio_player.skip(-5)
    }

    preview_backward_seek_long() {
        this.audio_player.skip(-20)
    }

    set_start_marker() {
        let sec_pos = this.audio_player.stream_position / 1000
        let region_start = this._region.start
        this._region.onResize(sec_pos - region_start, "start")
    }

    set_end_marker() {
        let sec_pos = this.audio_player.stream_position / 1000
        let region_end = this._region.end
        this._region.onResize(sec_pos - region_end)
    }

    move_start_marker_forward_short() {
        this._region.onResize(0.1, 'start')
    }

    move_start_marker_forward_long() {
        this._region.onResize(1, 'start')
    }

    move_end_marker_forward_short() {
        this._region.onResize(0.1)
    }

    move_end_marker_forward_long() {
        this._region.onResize(1)
    }

    move_start_marker_backward_short() {
        this._region.onResize(-0.1, 'start')
    }

    move_start_marker_backward_long() {
        this._region.onResize(-1, 'start')
    }

    move_end_marker_backward_short() {
        this._region.onResize(-0.1)
    }

    move_end_marker_backward_long() {
        this._region.onResize(-1)
    }

    setValue(id, value) {
        $$(id).define('value', value)
        $$(id).refresh()
    }

    getValue(id) {
        return $$(id).getValue()
    }

    setRating (num){
        var html = "";
        this.rating = num
        for (var i=1; i<6; i++) {
            html+="<div title='"+i+"' class='fa " + ( i <= num ? "fa-star" : "fa-star-o") +"' style='font-size: 14px'></div>";
        }
        $$(this.main_rating_edit_id).define('template', html)
        $$(this.main_rating_edit_id).refresh()
    }

    setLoved (value){
        var html = "";
        this.loved = value
        html+="<div title='"+i+"' class='fa " + (value ? "fa-heart" : "fa-heart-o") +"' style='font-size: 14px'></div>";
        $$(this.main_loved_edit_id).define('template', html)
        $$(this.main_loved_edit_id).refresh()
    }

    load_window_content () {
        this._waveform = WaveSurfer.create({
                container: `#${this.main_waveform_id}`,
                pixelRatio: 1,
                scrollParent: true,
                hideScrollbar: false,
                waveColor: 'violet',
                progressColor: 'purple',
                plugins: [
                    WaveSurferRegions.create({
                        container: `#${this.main_waveform_id}`,
                        deferInit: false,
                    })
                ]
            });
        this._waveform.on(
            "ready", () => {
                this.stream_start = this._track_info.stream_start
                this.stream_end = this._track_info.stream_end
                this._waveform.zoom($$(this.zoom_slider_id).getValue())
                this._position_tracker = this.audio_player.on("stream-position", 
                    (pos) => {
                        //console.log(pos/ this._track_info.track_length)
                        this._waveform.seekAndCenter(pos*1000000 / this._track_info.track_length)
                    }
                )
                this._region = this._waveform.addRegion({start:this._track_info.stream_start / 1000000000, end:this._track_info.stream_end / 1000000000})
                this._region.on("update", 
                    () => {
                        this.stream_start = Math.round(this._region.start * 1000000000)
                        this.stream_end = Math.round(this._region.end * 1000000000)
                        this.setValue(this.main_stream_length_id, `${format_nanoseconds(this.stream_end - this.stream_start)}`)
                    }
                )
            }
        )
        this._waveform.on(
            "seek", (p) => {
                //console.log("seek", p)
                this.current_stream_position = p
                // this.stream_start = this._track_info.stream_start
                // this.stream_end = this._track_info.stream_end
                // this._waveform.zoom($$("edit_zoom_last_30_seconds_button").getValue())
                // this._position_tracker = this.audio_player.on("stream-position", 
                //     (pos) => {
                //         this._waveform.seekAndCenter(pos*1000000 / this._track_info.track_length)
                //         //this._stream_position
                //     }
                // )
                // this._region = this._waveform.addRegion({start:this._track_info.stream_start / 1000000000, end:this._track_info.stream_end / 1000000000})
                // this._region.on("update", 
                //     () => {
                //         this.stream_start = Math.round(this._region.start * 1000000000)
                //         this.stream_end = Math.round(this._region.end * 1000000000)
                //         this.setValue(this.main_stream_length_id, `${format_nanoseconds(this.stream_end - this.stream_start)}`)
                //     }
                // )
            }
        )

        this.setValue(this.main_title_edit_id, this._track_info.title)
        this.setValue(this.main_artist_edit_id, this._track_info.artist)
        this.setValue(this.main_album_edit_id, this._track_info.album)
        this.setValue(this.main_genre_edit_id, this._track_info.genre)
        this.setValue(this.main_year_edit_id, this._track_info.year)
        this.setValue(this.main_grouping_edit_id, this._track_info.grouping)
        this.setValue(this.main_track_bpm_edit_id, this._track_info.bpm)
        this.setValue(this.main_color_edit_id, this._track_info.color)
        this.setValue(this.main_stream_length_id, `${format_nanoseconds(this._track_info.stream_length)}`)
        this.setValue(this.main_track_length_id, `${format_nanoseconds(this._track_info.track_length)}`)
        this.setRating(this._track_info.rating)
        this.setLoved(this._track_info.favorite)
        let cover_source = undefined;
        if (this._track_info.cover_medium == null) {
            cover_source = "../resources/images/default_album_cover.png"
        } else {
            cover_source = `file://${this._track_info.cover_medium}`;
        }
        var cover_image = `<img style="margin:0px; padding:0px;" src="${cover_source}" height='225' width='225'></img>`
        $$(this.main_cover_image_edit_id).define('template', cover_image);
        $$(this.main_cover_image_edit_id).refresh();
        this._waveform.load(this._track_info.file_name)
    }

    applyChanges() {
        let values = {
            title: this.getValue(this.main_title_edit_id), 
            artist: this.getValue(this.main_artist_edit_id),
            album: this.getValue(this.main_album_edit_id),
            genre: this.getValue(this.main_genre_edit_id),
            grouping: this.getValue(this.main_grouping_edit_id),
            yeaar: this.getValue(this.main_year_edit_id),
            bpm: this.getValue(this.main_track_bpm_edit_id),
            stream_start: this.stream_start,
            stream_end: this.stream_end,
            loved: this.loved,
            rating: this.rating,
            color: this.getValue(this.main_color_edit_id)
        }        
        this.dispatch("accept-changes", values)
        this.audio_player.stop()
        this.audio_player.un("stream-position", this.updateWaveformPosition)

        this.audio_player.audio_context.audio_ctx.close()
        this._win.hide()
    }

    dismissChanges () {
        this.dispatch("dismiss-changes")
        this.audio_player.stop()
        this.audio_player.un("stream-position", this.updateWaveformPosition)
        this.audio_player.audio_context.audio_ctx.close()

        this._win.hide()
    }

    constructor (audio_context) {
        super()
        this.id = this.ID("track_edit_window")
        this.main_cover_image_edit_id = this.ID("main-cover-image-edit")
        this.main_title_edit_id = this.ID("main-title-edit")
        this.main_artist_edit_id = this.ID("main-artist-edit")
        this.main_album_edit_id = this.ID("main-album-edit")
        this.main_genre_edit_id = this.ID("main-genre-edit")
        this.main_year_edit_id = this.ID("main-year-edit")
        this.main_grouping_edit_id = this.ID("main-grouping-edit")
        this.main_track_length_id = this.ID("main-track-length")
        this.main_stream_length_id = this.ID("main-stream-length")
        this.main_track_bpm_edit_id = this.ID("main-bpm-edit")
        this.main_display_color_edit_id = this.ID("main-display-color-edit")
        this.main_rating_edit_id = this.ID("main-rating-edit-edit")
        this.main_loved_edit_id = this.ID("main-loved-edit-edit")
        this.main_color_edit_id = this.ID("main-loved-edit-edit")
        this.main_waveform_id = this.ID("track_waveform")
        this.play_button_id = this.ID("play_button")
        this.zoom_slider_id = this.ID("zoom_slider")

        this.stream_start = 0
        this.stream_end = Infinity
        this.track_length = Infinity
        this.audio_player = new PydjayAudioBufferPlayer()
        this.audio_player.connectOutputs({master:{left:0, right:1}})
        this.current_stream_position = null
        this.layout = {
            id: this.id,
            view: "window",
            modal: true,
            position: "center",
            width: 1275,
            height: 900,
            head: "EDIT TRACK DATA",
            body:{
                rows:[
                    {height:30},
                    {
                        cols:[
                            {width:20},
                            {
                                rows: [
                                    {
                                        id:this.main_cover_image_edit_id,
                                        view: 'template',
                                        width:225,
                                        height:225,
                                        template: ""
                                    },
                                    {
                                        height: 40,
                                        cols: [
                                            {
                                                id:this.main_loved_edit_id,
                                                view: 'template',
                                                width:25,
                                                template: "<b><span class='fa fa-heart' style='font-size: 15px'/></b>"
                                            },
                                            {
                                                id:this.main_rating_edit_id,
                                                view: 'template',
                                                width:75,
                                                template: ""
                                            },
                                            {
                                                id:this.main_color_edit_id,
                                                view: 'colorpicker',
                                                width:125,
                                                label: ""
                                            },
                                        ]
                                    }
        
                                ]
                            },
                            {width:20},
                            {
                                rows:[
                                    {height:7},
                                    {
                                        cols: [
                                            {
                                                rows: [
                                                    {
                                                        id: this.main_title_edit_id,
                                                        view: 'text',
                                                        css: {
                                                            'text-align': 'left',
                                                            'text-transform': 'uppercase',
                                                            'font-size': '20px'
                                                        },
                                                        label: 'Title:',
                                                        labelWidth: 75,
                                                        height:30
                                                    },
                                                    {
                                                        id: this.main_artist_edit_id,
                                                        view: 'text',
                                                        css: {
                                                            'text-align':'left',
                                                            'font-size': '20px',
                                                            'color': '#bfbfbf'
                                                        },
                                                        label: 'Artist:',
                                                        labelWidth: 75,
                                                        height:30
                                                    },
                                                    {
                                                        id: this.main_album_edit_id,
                                                        view: 'text',
                                                        css: {
                                                            'text-align':'left',
                                                            'font-size': '20px',
                                                            'color': '#bfbfbf'
                                                        },
                                                        label: 'Album:',
                                                        labelWidth: 75,
                                                        height:30
                                                    },
                                                    {
                                                        id: this.main_year_edit_id,
                                                        view: 'text',
                                                        css: {
                                                            'text-align':'left',
                                                            'font-size': '20px',
                                                            'color': '#bfbfbf'
                                                        },
                                                        label: 'Year:',
                                                        labelWidth: 75,
                                                        height:30
                                                    },
                                                    {
                                                        id:this.main_genre_edit_id,
                                                        view: 'text',
                                                        css: {
                                                            'text-align':'left',
                                                            'font-size': '20px',
                                                            'color': '#bfbfbf'
                                                        },
                                                        label: 'Genre:',
                                                        labelWidth: 75,
                                                        height:30
                                                    },
                                                    {
                                                        id:this.main_grouping_edit_id,
                                                        view: 'text',
                                                        css: {
                                                            'text-align':'left',
                                                            'font-size': '20px',
                                                            'color': '#bfbfbf'
                                                        },
                                                        label: 'Grouping:',
                                                        labelWidth: 75,
                                                        height:30
                                                    },
                                                    {},
                                                    {
                                                        id:this.main_track_bpm_edit_id,
                                                        view: 'text',
                                                        css: {
                                                            'text-align':'left',
                                                            'font-size':'20px'
                                                        },
                                                        label: 'BPM:',
                                                        labelWidth: 75,
                                                        height:30
                                                    },
                                                    {
                                                        id:this.main_track_length_id,
                                                        view: 'text',
                                                        css: {
                                                            'text-align':'left',
                                                            'font-size':'20px'
                                                        },
                                                        labelWidth: 100,
                                                        label: 'File duration:',
                                                        height:30
                                                    },
                                                    {
                                                        id:this.main_stream_length_id,
                                                        view: 'text',
                                                        css: {
                                                            'text-align':'left',
                                                            'font-size':'20px'
                                                        },
                                                        label: 'Cut duration:',
                                                        labelWidth: 100,
                                                        height:30
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            },
                            {width:20}
                        ]
                    },
                    {height:50},
                    {
                        cols: [
                            {width:20}, 
                            {
                                id: this.play_button_id,
                                view:'button',
                                type:'icon',
                                icon:"play",
                                width:38,
                                click : () => {
                                    this.play_track()
                                }
                            },
                            {},
                            {
                                view:'button',
                                type:'icon',
                                icon:'search-minus',
                                width: 30,
                                click : function () {
                                }
                            },
                            {
                                id:this.zoom_slider_id,
                                view:'slider',
                                value:75,
                                min: 0, 
                                max: 300,
                                on: {
                                    "onSliderDrag": () => {
                                        this._waveform.zoom($$(this.zoom_slider_id).getValue())
                                    }
                                }
                            },
                            {
                                view:'button',
                                type:'icon',
                                icon:'search-plus',
                                width: 30,
                                click : function () {
                                }
                            },
                            {width:20}, 
                        ]
                    },
                    {
                        cols:[
                            {width:20},
                            {
                                height:175,
                                css:{
                                    margin:0,
                                    padding:0,
                                    border: '0px solid #3c3c3c'
                                },
                                template:`<div id="${this.main_waveform_id}" style="border: \'1px solid black\'; width:100%; height:100%; position:relative; top:0%;"></div>`
                            },
                            {width:20}
                        ]
                    },
                    {height:60},
                    {
                        cols:[
                            {width:30},
                            {
                                view: 'button',
                                label: 'APPLY',
                                click: () => this.applyChanges()
                            },
                            {},
                            {
                                view: 'button',
                                label: 'CANCEL',
                                click: () => this.dismissChanges()
                            },
                            {width:30}
                        ]
                    },
                    {height:10}
                ]
            }
        }
    }
}