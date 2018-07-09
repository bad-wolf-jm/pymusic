class MainPlayer extends PydjayAudioFilePlayer {
    constructor () {
        super()
        this.waveform_id = `waveform-${this.ID()}`
        this.cover_id = `cover-${this.ID()}`
        this.title_id = `title-${this.ID()}`
        this.artist_id = `artist-${this.ID()}`
        this.duration_id = `duration-${this.ID()}`
        this.remaining_id = `remaining-${this.ID()}`
        this.bpm_id = `bpm-${this.ID()}`
        this.rating_id = `rating-${this.ID()}`
        this.favorite_id = `favorite-${this.ID()}`
    }

    ID () {
        return Math.random().toString(36).substr(2, 9);
    }

    create_layout() {
        return {
            height: 213,
            rows: [
                {
                    view:'template',
                    template:this.waveform_id,
                    height:100
                },
                {
                    cols: [
                        {
                            view: 'template',
                            width:100,
                            height:100,
                            template: this.cover_id
                        },
                        {
                            width:10
                        },
                        {
                            rows: [
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
                                    id: this.title_id,
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
                                    id: this.title_id,
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
                                }
                            ]
                        },
                        {
                            width:100,
                            rows: [
                                {
                                    view:'label',
                                    label:'REMAINING',
                                    css: {
                                        'text-align':'left',
                                        'text-transform':'uppercase',
                                        'text-align': 'center',
                                        'font-weight':'bold',
                                        'font-size':"10pt",
                                        color:"#909090"
                                    },
                                },
                                {
                                    id: this.title_id,
                                    view:'label',
                                    label:'-03:26',
                                    css: {
                                        'text-align':'left',
                                        'text-transform':'uppercase',
                                        'text-align': 'center',
                                        'font-weight':'bold',
                                        'font-size':"20pt"//,
                                        // color:"#909090"
                                    },

                                }
                            ]
                        },
                        {
                            width:100,
                            rows: [
                                {
                                    view:'label',
                                    label:'DURATION',
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
                                    id: this.title_id,
                                    view:'label',
                                    label:'03:26',
                                    css: {
                                        'text-align':'left',
                                        'text-transform':'uppercase',
                                        'font-weight':'bold',
                                        'text-align': 'center',
                                        'font-size':"20pt",
                                        color:"#AFAFAF"
                                    },
                                }
                            ]
                        },
                        {
                            width:100,
                            rows: [
                                {
                                    view:'label',
                                    label:'BPM',
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
                                    id: this.title_id,
                                    view:'label',
                                    label:'120',
                                    css: {
                                        'text-align':'left',
                                        'text-transform':'uppercase',
                                        'font-weight':'bold',
                                        'font-size':"20pt",
                                        'text-align': 'center',
                                        color:"#AFAFAF"
                                    },
                                }
                            ]
                        },
                        {
                            width:100,
                            rows: [
                                {
                                    view:'label',
                                    label:'RATING',
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
                                    css: {
                                        'text-align':'left',
                                        'text-transform':'uppercase',
                                        'font-weight':'bold',
                                        'font-size':"20pt",
                                        'text-align': 'center',
                                        color:"#AFAFAF"
                                    },
                                }
                            ]
                        },
                        {
                            width:100,
                            rows: [
                                {
                                    view:'label',
                                    label:'FAV.',
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
                                    label:`<div class='webix_toggle_button_custom checked'><span class='fa fa-heart' style='font-size: 20px;'/></div>`,
                                    css: {
                                        'text-align':'left',
                                        'text-transform':'uppercase',
                                        'font-weight':'bold',
                                        'font-size':"20pt",
                                        'text-align': 'center',
                                        color:"#AFAFAF"
                                    },
                                }
                            ]
                        },
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
            html+="<div rating='"+i+"' class='rating_star fa " + ( i <= value ? "fa-star" : "fa-star-o") +"' style='font-size: 20px'></div>";
        }
        $$(this.rating_id).define('label', html)
        $$(this.rating_id).refresh()
        console.log(html)
    }
}