class TrackEditWindow extends EventDispatcher {

    ID () {
        return '_' + Math.random().toString(36).substr(2, 9);
      };

    show(track_info) {
        this._win = webix.ui(this.layout)
        this._track_info = track_info
        this._win.attachEvent("onShow", () => this.load_window_content())
    }

    load_window_content () {
        this._waveform = WaveSurfer.create({
                container: '#track-waveform',
                pixelRatio: 1,
                scrollParent: false,
                hideScrollbar: true,
                waveColor: 'violet',
                progressColor: 'purple'
            });
    }

    constructor () {
        this.id = this.ID("track_edit_window")
        this.main_cover_image_edit_id = this.ID("main-cover-image-edit")
        this.main_title_edit_id = this.ID("main-title-edit")
        this.main_artist_edit_id = this.ID("main-artist-edit")
        this.main_album_edit_id = this.ID("main-album-edit")
        this.main_genre_edit_id = this.ID("main-genre-edit")
        this.main_length_id = this.ID("main-track-length")
        this.main_bpm_edit_id = this.ID("main-bpm-edit")
        this.main_display_color_edit_id = this.ID("main-display-color-edit")
        this.main_waveform_id = this.ID("track_waveform")
        this.stream_start = 0
        this.stream_end = Infinity


        this.layout = {
            id: "track_edit_window",
            view: "window",
            modal: true,
            position: "center",
            width: 1275,
            height: 700,
            head: "EDIT TRACK DATA",
            body:{
                rows:[
                    {height:30},
                    {
                        cols:[
                            {width:20},
                            {
                                id:'main-cover-image-edit',
                                view: 'template',
                                width:128,
                                height:128,
                                template: ""
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
                                                        view: 'label',
                                                        css: {
                                                            'text-align': 'left',
                                                            'text-transform': 'uppercase',
                                                            'font-weight': 'bold',
                                                            'font-size': '20px'
                                                        },
                                                        label: 'Title Of Song',
                                                        height:30
                                                    },
                                                    {height:5},
                                                    {
                                                        id: this.main_artist_edit_id,
                                                        view: 'label',
                                                        css: {
                                                            'text-align':'left',
                                                            'font-size': '20px',
                                                            'color': '#bfbfbf'
                                                        },
                                                        label: 'Artist',
                                                        height:30
                                                    },
                                                    {
                                                        id: this.main_album_edit_id,
                                                        view: 'label',
                                                        css: {
                                                            'text-align':'left',
                                                            'font-size': '20px',
                                                            'color': '#bfbfbf'
                                                        },
                                                        label: 'Album',
                                                        height:30
                                                    },
                                                    {
                                                        id:this.main_genre_edit_id,
                                                        view: 'label',
                                                        css: {
                                                            'text-align':'left',
                                                            'font-size': '20px',
                                                            'color': '#bfbfbf'
                                                        },
                                                        label: 'Genre',
                                                        height:30
                                                    },
                                                    {},
                                                    {
                                                        id:this.main_track_length_id,
                                                        view: 'label',
                                                        css: {
                                                            'text-align':'left',
                                                            'font-size':'20px'
                                                        },
                                                        label: 'length',
                                                        height:30
                                                    },
                                                    {
                                                        id:this.main_bpm_edit_id,
                                                        view: 'label',
                                                        css: {
                                                            'text-align':'left',
                                                            'font-size':'20px'
                                                        },
                                                        label: 'BPM',
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
                                click : function () {
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
                                click: function () {
                                }
                            },
                            {},
                            {
                                view: 'button',
                                label: 'CANCEL',
                                click: () => {
                                }
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