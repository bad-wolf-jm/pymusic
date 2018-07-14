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
            //main_player_progress.animate(pos / (1000*mpl.source.duration));
        
        })
        // this.on('end-of-stream', function () {
        //     if (!stop_request){
        //         db_connection.query(
        //             'SELECT COUNT(id) as queue_count FROM session_queue WHERE status="pending"',
        //             function (error, result) {
        //                 if (error) throw error;
        //                 if (result[0].queue_count > 0) {
        //                     mark_as_played(current_queue_position, play_next_track_after_time);
        //                 } else {
        //                     mark_as_played(current_queue_position, false);
        //                     queue_playing = false;
        //                     $$('start-stop-button').define('label', 'START');
        //                     $$('start-stop-button').define('icon', 'play');
        //                     $$('start-stop-button').refresh();
        //                     $$('queue_stop_message').hide()
        //                 }
        //             }
        //         )
        //     } else {
        //         mark_as_played(current_queue_position, false);
        //         queue_playing = false;
        //         $$('start-stop-button').define('label', 'START');
        //         $$('start-stop-button').define('icon', 'play');
        //         $$('start-stop-button').refresh();
        //         $$('queue_stop_message').hide()
        //     }
        // })
          

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
        let cover_image = `<img style="margin:0px; padding:0px;" src="${cover_source}" height='135' width='135'></img>`
        $$(this.cover_id).define('template', cover_image);
        $$(this.cover_id).refresh();
        // current_queue_position = position;
        //$$('queue_list').remove($$('queue_list').getFirstId())
        // update_queue_labels();
        //main_play(file_name, result.stream_start, result.stream_end)
        this._waveform.load(file_name)
        this._track = track
        super.play(file_name,  track.stream_start / 1000000, track.stream_end / 1000000) //start_time / 1000000, end_time / 1000000)
    }

    init() {
        this._waveform = WaveSurfer.create({
            container: `#${this.waveform_id }`,
            pixelRatio: 1,
            scrollParent: true,
            hideScrollbar: false,
            waveColor: 'violet',
            progressColor: 'purple',
            height:125,
            barHeight:1.5,
            plugins: [
                WaveSurferRegions.create({
                    container: `#${this.main_waveform_id}`,
                    deferInit: false,
                })
            ]
        });       
        this._waveform.on(
            "ready", () => {
                // this.stream_start = this._track_info.stream_start
                // this.stream_end = this._track_info.stream_end
                // this._waveform.zoom($$(this.zoom_slider_id).getValue())
                this._position_tracker = this.on("stream-position", 
                    (pos) => {
                        p = pos*1000000 / this._track.track_length
                        p = max(p,0.0)
                        p = min(p,1.0)
                        this._waveform.seekAndCenter(pos*1000000 / this._track.track_length)
                    }
                )
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
 
    }
    

    create_layout() {
        return {
            height: 265,
            rows: [
                {
                    //id: this.waveform_id,
                    view:'template',
                    template:`<div id="${this.waveform_id}" style="border: \'1px solid black\'; width:100%; height:100%; position:relative; top:0%;"></div>`,
                    height:100
                },

                {
                    cols: [
                        {
                            id: this.cover_id,
                            view: 'template',
                            width:135,
                            height:135,
                            template: ""
                        },
                        {
                            width:10
                        },
                        {
                            rows: [
                                {
                                    cols: [
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
                                                // {
                                                //     view:'label',
                                                //     label:'REMAINING',
                                                //     css: {
                                                //         'text-align':'left',
                                                //         'text-transform':'uppercase',
                                                //         'text-align': 'center',
                                                //         'font-weight':'bold',
                                                //         'font-size':"10pt",
                                                //         color:"#909090"
                                                //     },
                                                // },
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
                                                        // color:"#909090"
                                                    },
                
                                                }
                                            ]
                                        },
                    
        
                                    ]
                                },
                                {height:10},
                                {
                                    cols: [
                                        {
                                            width:100,

                                            rows: [
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
                                                }
                                            ]
                                        },
                                        {
                                            width:100,
                                            height:30,

                                            rows: [
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
                                                }
                                            ]
                                        },
                                        {
                                            width:100,                                            
                                            height:30,

                                            rows: [
                                                {
                                                    view:'label',
                                                    label:'RATING',
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
                                                }
                                            ]
                                        },
                                        {
                                            width:100,
                                            height:30,
                                            rows: [
                                                {
                                                    view:'label',
                                                    label:'FAV.',
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
                                                }
                                            ]
                                        },
                                        {},
                
                                    ]
                                }
                            ]
                        },
                        //############################
                        // { 
                        //     view:"property", 
                        //     id:this.main_property_edit_id, 
                        //     width:250,
                        //     disable:true,
                        //     height:118, 
                        //     labelWidth:100,
                        //     elements:[
                        //         // { label:"Metadata", type:"label"},
                        //         // { label:"<b>Title:</b>", type:"text", id:"title"},
                        //         // { label:"<b>Artist:</b>", type:"text", id:"artist"},
                        //         // { label:"<b>Album:</b>", type:"text", id:"album"},
                        //         // { label:"<b>Year:</b>", type:"text", id:"year"},
                        //         // { label:"<b>Genre:</b>", type:"text", id:"genre"},
                        //         // { label:"<b>Color:</b>", type:"color", id:"color"},
                        //         { label:"<b>Rating:</b>", type:"rating", id:"rating"},
                        //         { label:"<b>Loved:</b>", type:"toggle",  id:"favorite"},
                        //         // { label:"Info", type:"label"},
                        //         { label:"<b>BPM:</b>", type:"text", id:"bpm"},
                        //         { label:"<b>Duration:</b>", id:"track_length", template:format_nanoseconds},
                        //     ]
                        // },

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