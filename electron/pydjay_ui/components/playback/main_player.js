class MainPlayer extends PydjayAudioFilePlayer {
    constructor () {
        super()
        this.waveform_id = `waveform-${this.ID()}`
        this.cover_id = `cover-${this.ID()}`
        this.title_id = `title-${this.ID()}`
        this.artist_id = `artist-${this.ID()}`
        this.album_id = `album-${this.ID()}`
        this.duration_id = `duration-${this.ID()}`
        this.remaining_id = `remaining-${this.ID()}`
        this.bpm_id = `bpm-${this.ID()}`
        this.rating_id = `rating-${this.ID()}`
        this.favorite_id = `favorite-${this.ID()}`

        this.on("stream-position", (pos) => {
            let remaining = Math.abs(mpl.source.duration*1000 - pos)
            $$(this.remaining_id).define('label', `-${format_nanoseconds(remaining*1000000)}`)
            $$(this.remaining_id).refresh()
        })
    }

    ID () {
        return Math.random().toString(36).substr(2, 9);
    }

    play(track) {
        //result = result[0];
        console.log(track)

        let file_name = path.join(track.music_root, track.file_name);
        let stream_length = (track.stream_end-track.stream_start);
        $$(this.title_id ).define('label', track.title)
        $$(this.title_id ).refresh()
        $$(this.artist_id ).define('label', `${track.artist}`)
        $$(this.artist_id ).refresh()
        $$(this.album_id ).define('label', `${track.album}`)
        $$(this.album_id ).refresh()
        $$(this.duration_id ).define('label', `${format_nanoseconds(stream_length)}`)
        $$(this.duration_id ).refresh()
        $$(this.bpm_id ).define('label', `${track.bpm}`)
        $$(this.bpm_id ).refresh()
        this.setRating(track.rating)
        this.setFavorite(track.favorite)
        let cover_source = undefined
        if (track.cover == null) {
            cover_source = "../resources/images/default_album_cover.png"
        } else {
            cover_source = `file://${track.image_root}/${track.cover}`;
        }
        let cover_image = `<img style="margin:0px; padding:0px;" src="${cover_source}" height='145' width='145'></img>`
        $$(this.cover_id).define('template', cover_image);
        $$(this.cover_id).refresh();
        this._waveform.load(file_name)
        this._track = track
        super.play(file_name,  track.stream_start / 1000000, track.stream_end / 1000000) //start_time / 1000000, end_time / 1000000)
    }

    init() {
        this._waveform = WaveSurfer.create({
            container: `#${this.waveform_id }`,
            pixelRatio: 2,
            scrollParent: true,
            hideScrollbar: false,
            waveColor: 'violet',
            progressColor: 'purple',
            height:125,
            barHeight:1.25,
            barWidth:1,
            //barGap:1,
            plugins: [
                WaveSurferRegions.create({
                    container: `#${this.main_waveform_id}`,
                    deferInit: false,
                })
            ]
        });       
        this._waveform.on(
            "ready", () => {
                this._waveform.zoom(175)
                //this._waveform.zoom(0)
                this._position_tracker = this.on("stream-position", 
                    (pos) => {
                        let p = pos*1000000 / this._track.track_length
                        p = Math.max(p,0.0)
                        p = Math.min(p,1.0)
                        this._waveform.seekAndCenter(p)
                    }
                )
            }
        )
 
    }
    

    create_layout() {
        return {
            height: 245,
            css: {
                'border-bottom': '1px solid white',
                'margin-bottom': "1px"
            },

            rows: [
                {
                    view:'template',
                    template:`<div id="${this.waveform_id}" style="border: \'1px solid black\'; width:100%; height:100%; position:relative; top:0%;"></div>`,
                    height:100
                },

                {
                    cols: [
                        {
                            id: this.cover_id,
                            view: 'template',
                            width:145,
                            height:145,
                            template: ""
                        },
                        // {
                        //     width:10
                        // },
                        {
                            rows: [
                                {
                                    cols: [
                                        {
                                            width:10
                                        },
                                        {
                                            rows:[
                                                {
                                                    id: this.title_id,
                                                    view:'label',
                                                    label:'TITLE',
                                                    height:50,
                                                    css: {
                                                        'text-align':'left',
                                                        'text-transform':'uppercase',
                                                        'font-weight':'bold',
                                                        'font-size':"18pt",
                                                    },
                                                },
                                                {
                                                    id: this.artist_id,
                                                    view:'label',
                                                    label:'ARTIST',
                                                    height:25,
                                                    css: {
                                                        'text-align':'left',
                                                        'text-transform':'uppercase',
                                                        'font-weight':'bold',
                                                        'font-size':"10pt",
                                                        color:"#909090"
                                                    },
                
                                                },
                                                {
                                                    id: this.album_id,
                                                    view:'label',
                                                    label:'ALBUM',
                                                    height:25,
                                                    css: {
                                                        'text-align':'left',
                                                        'text-transform':'uppercase',
                                                        'font-weight':'bold',
                                                        'font-size':"10pt",
                                                        color:"#909090"
                                                    },
                                                },        
                                            ]
                                        },
                                        {
                                            width:100,
                                            rows: [
                                                {
                                                    id: this.remaining_id,
                                                    view:'label',
                                                    label:'-03:26',
                                                    height:50,
                                                    css: {
                                                        'text-align':'left',
                                                        'text-transform':'uppercase',
                                                        'text-align': 'center',
                                                        'font-weight':'bold',
                                                        'font-size':"18pt"//,
                                                    },
                
                                                }
                                            ]
                                        },
                    
        
                                    ]
                                },
                                {height:10},
                                {
                                    css: {
                                        'border-top': '1px solid white',
                                        'margin-bottom': "10px"
                                    },
                                    cols: [
                                        {
                                            width:100,
                                            css: {
                                                'border-right': '1px solid white !important',
                                                'margin-bottom': "10px"
                                            },
        
                                            rows: [
                                                {},
                                                {
                                                    view:'label',
                                                    label:'DURATION',
                                                    height:15,
                                                    css: {
                                                        'text-align':'left',
                                                        'text-transform':'uppercase',
                                                        'font-weight':'bold',
                                                        'text-align': 'center',
                                                        'font-size':"10pt",
                                                        color:"#909090"
                                                    },
                                                },
                                                {
                                                    id: this.duration_id,
                                                    view:'label',
                                                    height:15,
                                                    label:'03:26',
                                                    css: {
                                                        'text-align':'left',
                                                        'text-transform':'uppercase',
                                                        'font-weight':'bold',
                                                        'text-align': 'center',
                                                        'font-size':"10pt",
                                                        color:"#AFAFAF"
                                                    },
                                                },
                                                {}
                                            ]
                                        },
                                        {
                                            width:100,
                                            height:30,
                                            css: {
                                                'border-right': '1px solid white !important',
                                                'margin-bottom': "10px"
                                            },

                                            rows: [
                                                {},
                                                {
                                                    view:'label',
                                                    label:'BPM',
                                                    height:15,
                                                    css: {
                                                        'text-align':'left',
                                                        'text-transform':'uppercase',
                                                        'font-weight':'bold',
                                                        'font-size':"10pt",
                                                        'text-align': 'center',
                                                        color:"#909090"
                                                    },
                                                },
                                                {
                                                    id: this.bpm_id,
                                                    view:'label',
                                                    label:'120',
                                                    height:15,
                                                    css: {
                                                        'text-align':'left',
                                                        'text-transform':'uppercase',
                                                        'font-weight':'bold',
                                                        'font-size':"10pt",
                                                        'text-align': 'center',
                                                        color:"#AFAFAF"
                                                    },
                                                },
                                                {}
                                            ]
                                        },
                                        {
                                            width:100,                                            
                                            height:30,
                                            css: {
                                                'border-right': '1px solid white !important',
                                                'margin-bottom': "10px"
                                            },

                                            rows: [
                                                {
                                                    // view:'label',
                                                    // label:'RATING',
                                                    // height:15,
                                                    // css: {
                                                    //     'text-align':'left',
                                                    //     'text-transform':'uppercase',
                                                    //     'font-weight':'bold',
                                                    //     'font-size':"10pt",
                                                    //     'text-align': 'center',
                                                    //     color:"#909090"
                                                    // },
                                                },
                                                {
                                                    id: this.rating_id,
                                                    view:'label',
                                                    label:'03:26',
                                                    height:15,
                                                    css: {
                                                        'text-align':'left',
                                                        'text-transform':'uppercase',
                                                        'font-weight':'bold',
                                                        'font-size':"10pt",
                                                        'text-align': 'center',
                                                        color:"#AFAFAF"
                                                    },
                                                },
                                                {}
                                            ]
                                        },
                                        {
                                            width:100,
                                            height:30,
                                            css: {
                                                'border-right': '1px solid white !important',
                                                'margin-bottom': "10px"
                                            },

                                            rows: [
                                                {
                                                    // view:'label',
                                                    // label:'FAV.',
                                                    // height:15,
                                                    // css: {
                                                    //     'text-align':'left',
                                                    //     'text-transform':'uppercase',
                                                    //     'font-weight':'bold',
                                                    //     'font-size':"10pt",
                                                    //     'text-align': 'center',
                                                    //     color:"#909090"
                                                    // },
                                                },
                                                {
                                                    id: this.favorite_id,
                                                    view:'label',
                                                    label:`<div class='webix_toggle_button_custom checked'><span class='fa fa-heart'/></div>`,
                                                    height:15,
                                                    css: {
                                                        'text-align':'left',
                                                        'text-transform':'uppercase',
                                                        'font-weight':'bold',
                                                        'font-size':"9pt",
                                                        'text-align': 'center',
                                                        color:"#AFAFAF"
                                                    },
                                                },
                                                {}
                                            ]
                                        },
                                        {},
                                        {
                                            gravity:.5,
                                            view:'template',
                                            id: 'queue_stop_message',
                                            css: {
                                                'text-align':'center',
                                                'vertical-align': 'middle',
                                                color: '#fbbbbbb',
                                                'background-color': '#870053'
                                            },
                                            template:`<span style="vertical-align:bottom">
                                                        <b>Queue will stop after this song</b>
                                                    </span>`,
                                            maxHeight:35
                                        },
                                        {
                                            css: {
                                                'border-right': '1px solid white !important',
                                                'margin-bottom': "10px"
                                            },
                                        },
                                        {
                                            width:10
                                        },
                                        {
                                            view:'button',
                                            type:'icon',
                                            icon:'list',
                                            label:'SESSION',
                                            height:25,
                                            width:100,
                                            popup:'session_popup'
                                        },        
                                        {width:50},        
                                        {
                                            gravity:.5,
                                            id:'start-stop-button',
                                            view:'button',
                                            type:'icon',
                                            icon:'play',
                                            label:'START',
                                            click: start_queue,
                                            maxHeight:35,
                                            width:100
                                        },
                                        {
                                            gravity:.5,
                                            view:'button',
                                            type:'icon',
                                            icon:'step-forward',
                                            label:'SKIP/STOP',
                                            popup: "skip_stop_dialog",
                                            maxHeight:35,
                                            width:100
                                        },
                                        {
                                            gravity:.5,
                                            view:'button',
                                            type:'icon',
                                            icon:'cog',
                                            label:'SETTINGS',
                                            click: playback_settings,
                                            maxHeight:35,
                                            width:100
                                        },
                
                                    ]
                                }
                            ]
                        },
                    ]
                }
            ]
        }
    }

    setRating(value) {
        var html = "";
        for (var i=1; i<6; i++) {
            html+="<div rating='"+i+"' class='rating_star fa " + ( i <= value ? "fa-star" : "fa-star-o") +"' style='font-size: 10pt'></div>";
        }
        $$(this.rating_id).define('label', html)
        $$(this.rating_id).refresh()
        //console.log(html)
    }

    setFavorite(value) {
        var html = "";
        if (value) {
            html = `<div class='webix_toggle_button_custom checked'><span class='fa fa-heart'></div>`
        } else {
            html= `<div class='webix_toggle_button_custom checked'><span class='fa fa-heart-o'></div>`
        }
        $$(this.favorite_id).define('label', html)
        $$(this.favorite_id).refresh()
        //console.log(html)
    }


}