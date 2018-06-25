class TrackEditWindow extends EventDispatcher {

    ID () {
        return '_' + Math.random().toString(36).substr(2, 9);
      };

    show(track_info) {
        this._win = webix.ui(this.layout)
        this._track_info = track_info
        this._win.attachEvent("onShow", () => this.load_window_content())
        this._win.show()
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
                scrollParent: false,
                hideScrollbar: true,
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
                this._position_tracker = this.audio_player.on("stream-position", 
                (pos) => {
                    this._waveform.seekTo(pos*1000000 / this._track_info.track_length)
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
        this.setValue(this.main_title_edit_id, this._track_info.title)
        this.setValue(this.main_artist_edit_id, this._track_info.artist)
        this.setValue(this.main_album_edit_id, this._track_info.album)
        this.setValue(this.main_genre_edit_id, this._track_info.genre)
        this.setValue(this.main_year_edit_id, this._track_info.year)
        this.setValue(this.main_grouping_edit_id, this._track_info.grouping)
        this.setValue(this.main_track_bpm_edit_id, this._track_info.bpm)
        this.setValue(this.main_color_edit_id, "#FAFAFA")
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

        this._win.hide()
    }

    dismissChanges () {
        this.dispatch("dismiss-changes")
        this.audio_player.stop()
        this.audio_player.un("stream-position", this.updateWaveformPosition)

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
        this.stream_start = 0
        this.stream_end = Infinity
        this.track_length = Infinity
        this.audio_player = audio_context
        this.layout = {
            id: "track_edit_window",
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
                            {
                                id:'edit_zoom_first_10_seconds_button',
                                view:'button',
                                type:'icon',
                                label: 'FIRST 10 SECONDS',
                                click : function () {
                                }
                            },
                            {
                                id:'edit_zoom_first_30_seconds_button',
                                view:'button',
                                type:'icon',
                                label: 'FIRST 30 SECONDS',
                                click : function () {
                                }
                            },
                            {},
                            {
                                id:'edit_reset_zoom_button',
                                view:'button',
                                type:'icon',
                                label: 'RESET',
                                click : function () {
                                }
                            },
                            {},
                            {
                                id:'edit_zoom_last_30_seconds_button',
                                view:'button',
                                type:'icon',
                                label: 'LAST 30 SECONDS',
                                click : function () {
                                }
                            },
                            {
                                id:'edit_zoom_last_10_seconds_button',
                                view:'button',
                                type:'icon',
                                label: 'LAST 10 SECONDS',
                                click : function () {
                                }
                            }
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
                    {height:30},
                    {
                        cols: [
                            {width:30},
                            {
                                id:'edit_play_button',
                                view:'button',
                                label: 'PLAY FULL TRACK',
                                click : () => {
                                    this.audio_player.playBuffer(this._waveform.backend.buffer, this.stream_start / 1000000, this.stream_end / 1000000)
                                }
                            },
                            {
                                id:'edit_play_last_30_seconds_button',
                                view:'button',
                                label: 'LAST 30 SECONDS',
                                click : function () {
                                }
                            },
                            {
                                id:'edit_play_last_10_seconds_button',
                                view:'button',
                                label: 'LAST 10 SECONDS',
                                click : function () {
                                }
                            },
                            {},
                            {
                                id:'edit_stop_button',
                                view:'button',
                                label: 'STOP',
                                click : function () {
                                }
                            },
                            {width:30}
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