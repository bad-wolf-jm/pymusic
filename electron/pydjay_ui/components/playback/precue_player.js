class PrecuePlayer extends PydjayAudioFilePlayer {
    constructor () {
        super()
        this.title_label_id = `title-${this.ID()}`
        this.artist_label_id = `artist-${this.ID()}`
        this.cover_id = `cover-${this.ID()}`
        this.time_label_id = `time-${this.ID()}`
        this.length_label_id = `length-${this.ID()}`
        this.position_id = `position-${this.ID()}`
        this.info_id = `info-${this.ID()}`
        this.info_details_id = `info-${this.ID()}`

        this.track = undefined

        this.on("stream-position", function (pos) {
            $$(this.time_label_id).define('label', `${format_nanoseconds(pos*1000000)}`)
            $$(this.time_label_id).refresh()
            $$(this.length_label_id).define('label', format_nanoseconds(pl.source.duration*1000000000))
            $$(this.length_label_id).refresh();
            this.preview_seek.animate(pos / (1000*pl.source.duration));
            this.preview_track_position = pos;
        })
        
        this.track_info_popup = webix.ui(
            {
                view:"popup",
                id:this.info_id,
                height:300,
                width:350,
                body:{
                    view:"property", 
                    id:this.info_details_id, 
                    disable:true,
                    height:285, 
                    labelWidth:100,
                    elements:[
                        { label:"Metadata", type:"label"},
                        { label:"<b>Title:</b>", id:"title"},
                        { label:"<b>Artist:</b>", id:"artist"},
                        { label:"<b>Album:</b>", id:"album"},
                        { label:"<b>Year:</b>", id:"year"},
                        { label:"<b>Genre:</b>", id:"genre"},
                        { label:"<b>Color:</b>", id:"color"},
                        { label:"<b>Rating:</b>", id:"rating"},
                        { label:"<b>Loved:</b>", id:"favorite"},
                    ]
                },
            }
        )
        this.preview_seek = undefined
        webix.ready( () => {
            this.preview_seek = new ProgressBar.Line(`#${this.position_id}`,
            {
                strokeWidth: 1,
                duration: 5,
                color: '#5a5a5a',
                trailColor: '#eee',
                trailWidth: 1,
                svgStyle: {width: '100%', height: '100%'}
            }
         );
            preview_seek.animate(0);
        });
        
        this.track_info_popup.hide();
        this.track_info_popup.attachEvent('onShow', function () {
            if (this.track.id != undefined) {
                DB.get_track_by_id(this.track.id,
                    function (track_info) {
                        $$("info_popup_property_sheet").setValues(track_info[0])
                    }
                )
            }
        })
    }

    ID () {
        return '_' + Math.random().toString(36).substr(2, 9);
    }

    create_layout() {
        return {
            height:95,
            css:{
                'background-color':'#6c6c6c',
                'padding':'1px',
                border: '1px solid #3c3c3c'
             },
            cols:[
                {
                    id: this.cover_id,
                    view: 'template',
                    width:95,
                    height:95,
                    template: ""
                },
                {width:10},
                {
                    cols: [
                        {
                            rows: [
                                {},
                                {
                                    cols: [
                                        {
                                            rows: [
                                                {
                                                    id: this.title_id,
                                                    view: 'label',
                                                    label: "<b>NO TRACK</b>",
                                                    height:20
                                                },
                                                {
                                                    id: this.artist_id,
                                                    view: 'label',
                                                    label: "NO ARTIST",
                                                    height:20
                                                },                
                                            ]
                                        },
                                        {width:5},
                                        {
                                            view:'button',
                                            type: 'icon',
                                            icon: 'headphones',
                                            width:30,
                                            popup: "preview_popup_menu"
                                        },
                                        {
                                            view:'button',
                                            type: 'icon',
                                            icon: 'info',
                                            width:30,
                                            popup: this.info_id
                                        },
                                    ]
                                },
                                {},
                                {
                                    cols: [
                                        {
                                            rows: [
                                                {
                                                    height:18,
                                                    template:`<div id="${this.position_id}" style="margin:0px; padding:0px; width:100%; height:100%; position:relative; top:0%; left:0%;"></div>`
                                                },
                                                {height: 7},
                                                {cols:[
                                                    {
                                                        id: this.time_label_id,
                                                        view: 'label',
                                                        css:{
                                                            'text-align':'left',
                                                            'text-transform':'uppercase'
                                                        },
                                                        label: '0:00',
                                                        height:15
                                                    },
                                                    {},
                                                    {
                                                        id: this.time_label_id,
                                                        view: 'label',
                                                        css:{'text-align':'right'},
                                                        label: '0:00',
                                                        height:15
                                                    }
                                                ]},                
                                            ]
                                        },
                                    ]
                                },
                                {}
                            ]
                        },
                        {width:10}
                    ]
                }
            ]
        }
    }

    play(track, stream_start, stream_end) {
        this.track = track
        file_name = path.join(this.track.music_root, this.track.file_name);
        cover_file_name = `${this.track.image_root}/${this.track.cover_small}`;
        stream_length = (this.track.stream_end-this.track.stream_start) / 1000000000;
        preview_play_id = this.track.id
        $$(this.title_label_id).define('label', `<b>${this.track.title}</b>`)
        $$(this.title_label_id).refresh()
        $$(this.artist_label_id).define('label', `${this.track.artist}`)
        $$(this.artist_label_id).refresh()
        if (this.track.cover_small == null) {
            cover_source = "../resources/images/default_album_cover.png"
        } else {
            cover_source = `file://${this.track.image_root}/${this.track.cover_small}`;
        }
        var cover_image = `<img style="margin:0px; padding:0px;" src="${cover_source}" height='95' width='95'></img>`
        $$(this.cover_id).define('template', cover_image);
        $$(this.cover_id).refresh();

        if (stream_start == undefined) {
            stream_start = this.track.stream_start
            stream_end = this.track.stream_end
        } else if (stream_end == undefined) {  
            stream_end = end = this.track.stream_end
            if (stream_start < 0) {
                stream_start = stream_end + stream_start;
            }
        }
        super.play(file_name, stream_start, stream_end)
    }
}