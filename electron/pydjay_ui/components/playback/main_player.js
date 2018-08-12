class SpectrumAnalyzer {
    constructor(canvas, analyzer) {
        this.analyzer = analyzer
        this.canvas_id = canvas
        this.animationId = null;
        this.status = 0; //flag for sound is playing 1 or stopped 0
        this.allCapsReachBottom = false;    
        this.capYPositionArray = [];   

    }

    drawMeter() {
        let cwidth = this.canvas.width
        let cheight = this.canvas.height - 2
        let meterWidth = 4 //width of the meters in the spectrum
        let gap = 0 //gap between meters
        let capHeight = 2
        let capStyle = '#fff'
        let meterNum = cwidth / (meterWidth + gap) //count of the meters
        // capYPositionArray = []; ////store the vertical position of hte caps for the preivous frame

        let array = new Uint8Array(this.analyzer.frequencyBinCount);
        this.analyzer.getByteFrequencyData(array);
        //console.log(this.status, array)
        if (this.status === 0) {
            //fix when some sounds end the value still not back to zero
            for (var i = array.length - 1; i >= 0; i--) {
                array[i] = 0;
            };
            this.allCapsReachBottom = true;
            for (var i = this.capYPositionArray.length - 1; i >= 0; i--) {
                this.allCapsReachBottom = this.allCapsReachBottom && (this.capYPositionArray[i] === 0);
            };
            if (this.allCapsReachBottom) {
                cancelAnimationFrame(this.animationId); //since the sound is stoped and animation finished, stop the requestAnimation to prevent potential memory leak,THIS IS VERY IMPORTANT!
                return;
            };
        };
        var step = Math.round(array.length / meterNum); //sample limited data from the total array
        this.ctx.clearRect(0, 0, cwidth, cheight);
        for (var i = 0; i < meterNum; i++) {
            var value = (array[i * step] / 255) * cheight;
            if (this.capYPositionArray.length < Math.round(meterNum)) {
                this.capYPositionArray.push(value);
            };
            this.ctx.fillStyle = capStyle;
            //draw the cap, with transition effect
            if (value < this.capYPositionArray[i]) {
                this.ctx.fillRect(i * (meterWidth + gap), cheight - (--this.capYPositionArray[i]), meterWidth, capHeight);
            } else {
                this.ctx.fillRect(i * (meterWidth + gap), cheight - value, meterWidth, capHeight);
                this.capYPositionArray[i] = value;
            };
            this.ctx.fillStyle = this.gradient; //set the filllStyle to gradient for a better look
            this.ctx.fillRect(i * (meterWidth + gap) /*meterWidth+gap*/ , cheight - value + capHeight, meterWidth, cheight); //the meter
        }
        this.animationId = requestAnimationFrame(() => this.drawMeter());
    }

    _drawSpectrum() {
        // let canvas = this.canvas,
        this.canvas = document.getElementById(this.canvas_id)
        this.ctx = this.canvas.getContext('2d')
        this.gradient = this.ctx.createLinearGradient(0, 0, 0, this.canvas.height);
        this.gradient.addColorStop(1, '#222');
        this.gradient.addColorStop(0.5, '#999');
        this.gradient.addColorStop(0.10, '#ccc');
        this.gradient.addColorStop(0, '#f00');
        this.animationId = requestAnimationFrame(() => this.drawMeter());
    }

    start() {
        this.status = 1;
        this._drawSpectrum()
    }

    stop() {
        this.status = 0;
    }

}


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
        this.spectrum_analyzer_id = `spectrum-${this.ID()}`

        this.on("stream-position", (pos) => {
            let remaining = Math.abs(this.source.duration*1000 - pos)
            $$(this.remaining_id).define('label', `-${format_nanoseconds(remaining*1000000)}`)
            $$(this.remaining_id).refresh()
        })
    }

    ID () {
        return Math.random().toString(36).substr(2, 9);
    }

    play(track) {
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
        let cover_image = `<img style="margin:0px; padding:0px;" src="${cover_source}" height='170' width='170'></img>`
        $$(this.cover_id).define('template', cover_image);
        $$(this.cover_id).refresh();
        this._track = track
        this._waveform.load(file_name)
    }

    pause() {
        super.pause()
        if (this.spectrum_analyzer != undefined) {
            this.spectrum_analyzer.stop()
        }
    }

    stop() {
        super.stop()
        if (this.spectrum_analyzer != undefined) {
            this.spectrum_analyzer.stop()
        }

    }

    init() {
        this._waveform = WaveSurfer.create({
            container: `#${this.waveform_id }`,
            pixelRatio: 2,
            scrollParent: true,
            hideScrollbar: false,
            waveColor: 'violet',
            progressColor: 'purple',
            height:30,
            barHeight:1,
            plugins: [
                WaveSurferRegions.create({
                    container: `#${this.main_waveform_id}`,
                    deferInit: false,
                })
            ]
        });       
        this._position_tracker = this.on("stream-position", 
            (pos) => {
                let p = pos*1000000 / this._track.track_length
                p = Math.max(p,0.0)
                p = Math.min(p,1.0)
                this._waveform.seekAndCenter(p)
            }
        )

        this._waveform.on(
            "ready", () => {
                this._waveform.zoom(0)
                let file_name = path.join(this._track.music_root, this._track.file_name);
                super.play(file_name,  this._track.stream_start / 1000000, this._track.stream_end / 1000000) //start_time / 1000000, end_time / 1000000)
                this.spectrum_analyzer.start()
            }
        )

        this.spectrum_analyzer = new SpectrumAnalyzer(
            this.spectrum_analyzer_id,
            this.audio_context.analyzer
        )
    }


    create_layout() {
        return {
            height: 170,
            css: {
                'border-bottom': '1px solid white',
                'margin-bottom': "1px",
                "background-color": "#1E1E1E"
            },

            rows: [

                {
                    cols: [
                        {
                            id: this.cover_id,
                            view: 'template',
                            width:170,
                            height:170,
                            template: "",
                            css: {
                                "background-color": "#1E1E1E"
                            },

                        },
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
                                                    height:20,
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
                                                    height:20,
                                                    css: {
                                                        'text-align':'left',
                                                        'text-transform':'uppercase',
                                                        'font-weight':'bold',
                                                        'font-size':"10pt",
                                                        color:"#909090"
                                                    },
                                                },    
                                                {height:7}    
                                            ]
                                        },
                                        {
                                            width:200,
                                            rows: [
                                                {
                                                    id: this.remaining_id,
                                                    view:'label',
                                                    label:'-03:26',
                                                    height:50,
                                                    css: {
                                                        'text-align':'left',
                                                        'text-transform':'uppercase',
                                                        'text-align': 'right',
                                                        'font-weight':'bold',
                                                        'font-size':"18pt"//,
                                                    },
                
                                                },
                                                {height:15},
                                                {
                                                    cols: [
                                                        {
                                                            gravity:.5,
                                                            id:'start-stop-button',
                                                            view:'button',
                                                            type:'icon',
                                                            icon:'play',
                                                            label:'START',
                                                            click: start_queue,
                                                            //maxHeight:35,
                                                            width:100
                                                        },
                                                        {
                                                            gravity:.5,
                                                            view:'button',
                                                            type:'icon',
                                                            icon:'step-forward',
                                                            label:'SKIP/STOP',
                                                            popup: "skip_stop_dialog",
                                                            //maxHeight:35,
                                                            width:100
                                                        },        
                                                    ]
                                                }
    
                                            ]
                                        },
                                        {width:10},
                                        {
                                            view: 'template',
                                            width:500,
                                            height:90,
                                            template: `<canvas id='${this.spectrum_analyzer_id}' style="border: \'1px solid black\'; width:100%; height:100%">`,
                                            // template: `<canvas id='${this.spectrum_analyzer_id}' style="border: \'1px solid black\'; width:600; height:100">`,
                                            css: {
                                                // 'border-bottom': '1px solid white',
                                                // 'margin-bottom': "1px",
                                                "background-color": "#1E1E1E"
                                            },
                                        }
                                    ]
                                },
                                {
                                    view:'template',
                                    css: {
                                        "background-color": "#1E1E1E"
                                    },
                                    template:`<div id="${this.waveform_id}" style="border: \'1px solid black\'; width:100%; height:100%; position:relative; top:0%;"></div>`,
                                    height:30
                                },
                
                                // {height:3},
                                {
                                    height:55,
                                    css: {
                                        'border-top': '1px solid white',
                                        //'margin-bottom': "10px"
                                    },
                                    cols: [
                                        {
                                            width:100,
                                            height:30,
                                            css: {
                                                'border-right': '1px solid white !important',
                                                // 'margin-bottom': "10px"
                                            },
        
                                            rows: [
                                                {height:10},
                                                {
                                                    view:'label',
                                                    label:'DURATION',
                                                    height:8,
                                                    css: {
                                                        'text-align':'left',
                                                        'text-transform':'uppercase',
                                                        'font-weight':'bold',
                                                        'text-align': 'center',
                                                        'font-size':"8pt",
                                                        color:"#909090"
                                                    },
                                                },
                                                {
                                                    id: this.duration_id,
                                                    view:'label',
                                                    height:20,
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
                                                //{}
                                            ]
                                        },
                                        {
                                            width:100,
                                            height:35,
                                            css: {
                                                'border-right': '1px solid white !important',
                                                // 'margin-bottom': "10px"
                                            },

                                            rows: [
                                                {height:10},
                                                {
                                                    view:'label',
                                                    label:'BPM',
                                                    height:8,
                                                    css: {
                                                        'text-align':'left',
                                                        'text-transform':'uppercase',
                                                        'font-weight':'bold',
                                                        'font-size':"8pt",
                                                        'text-align': 'center',
                                                        color:"#909090"
                                                    },
                                                },
                                                {
                                                    id: this.bpm_id,
                                                    view:'label',
                                                    label:'120',
                                                    height:20,
                                                    css: {
                                                        'text-align':'left',
                                                        'text-transform':'uppercase',
                                                        'font-weight':'bold',
                                                        'font-size':"10pt",
                                                        'text-align': 'center',
                                                        color:"#AFAFAF"
                                                    },
                                                },
                                                //{}
                                            ]
                                        },
                                        {
                                            width:100,                                            
                                            css: {
                                                'border-right': '1px solid white !important',
                                            },

                                            rows: [
                                                //{},
                                                {
                                                    id: this.rating_id,
                                                    view:'label',
                                                    height:40,
                                                    css: {
                                                        'text-align':'left',
                                                        'text-transform':'uppercase',
                                                        'font-weight':'bold',
                                                        'font-size':"10pt",
                                                        'text-align': 'center',
                                                        color:"#AFAFAF"
                                                    },
                                                },
                                                //{}
                                            ]
                                        },
                                        {
                                            width:100,
                                            css: {
                                                'border-right': '1px solid white !important',
                                            },

                                            rows: [
                                                //{},
                                                {
                                                    id: this.favorite_id,
                                                    view:'label',
                                                    label:`<div class='webix_toggle_button_custom checked'><span class='fa fa-heart'/></div>`,
                                                    height:40,
                                                    css: {
                                                        'text-align':'left',
                                                        'text-transform':'uppercase',
                                                        'font-weight':'bold',
                                                        'font-size':"9pt",
                                                        'text-align': 'center',
                                                        color:"#AFAFAF"
                                                    },
                                                },
                                                //{}
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
                                            height:35,
                                            width:100,
                                            popup:'session_popup'
                                        },        
                                        {width:50},        
                                        // {
                                        //     gravity:.5,
                                        //     view:'button',
                                        //     type:'icon',
                                        //     icon:'cog',
                                        //     label:'SETTINGS',
                                        //     click: playback_settings,
                                        //     maxHeight:35,
                                        //     width:100
                                        // },
                
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
    }

    setFavorite(value) {
        var html = "";
        if (value) {
            html = `<div class='webix_toggle_button_custom checked'><span class='fa fa-heart'></div>`
        } else {
            html = `<div class='webix_toggle_button_custom checked'><span class='fa fa-heart-o'></div>`
        }
        $$(this.favorite_id).define('label', html)
        $$(this.favorite_id).refresh()
        //console.log(html)
    }


}