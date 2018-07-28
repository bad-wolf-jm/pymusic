var jsmediatags = require("jsmediatags");
var fs = require('fs-extra');
var path = require('path');
const {spawn} = require ('child_process');
var async = require('async');
var Jimp = require("jimp");

class TrackAddProgressDialog {
    constructor(settings, id_start, track_list) {
        this.track_list = track_list
        this.id_start = id_start
        this.settings = settings
        this.num = this.track_list.length
        this._win = webix.ui({
            view:"window",
            modal:true,
            position:"center",
            width:600,
            height:400,
            head: false,
            body:{
                rows:[
                    {height:10},
                    {
                        id:'track_add_progress',
                        view: "label",
                        label:"Processing track ### of ###",
                        css: {
                            'text-align': 'center',
                            'font-size':  '20px',
                        }
                    },
                    {height:10},
                    {
                        id:'track_add_title',
                        view: "label",
                        label:"Title Of Song",
                        css: {
                            'text-align': 'center',
                            'font-size': '20px',
                        }
        
                    },
                    {
                        id:'track_add_artist',
                        view: "label",
                        label:"Artist - Album",
                        css: {
                            'text-align': 'center',
                            'font-size':  '15px',
                        }
        
                    }
                ]
            }
        })
        this._add_tracks({}, this.id_start, this.track_list.length)
        this._win.show()
    }

    getFileExtension(f_name) {
        return f_name.slice((Math.max(0, f_name.lastIndexOf(".")) || Infinity) + 1);
    }
    
    _add_tracks (settings, id, total) {
        if (this.track_list.length > 0) {
            let data = this.track_list.pop();
            let mp3_file = `track_${id}.${this.getFileExtension(data.filename)}`
            let mp3_path = `${this.settings.music_root}/${mp3_file}`
            // console.log(data.filename, mp3_path)
            var original_image_file = null;
            var large_image_file = null;
            var medium_image_file = null;
            var small_image_file = null;
            // var wave_path = null;
    
            $$('track_add_progress').define('label', `ADDING TRACK ${total - this.track_list.length} OF ${total}`)
            $$('track_add_progress').refresh()
            $$('track_add_title').define('label', `<b>${data.title}</b>`)
            $$('track_add_title').refresh()
            $$('track_add_artist').define('label', `${data.artist} - ${data.album}`)
            $$('track_add_artist').refresh()
    
            fs.copy(data.filename, mp3_path).then( () => {
                    if (data.picture != undefined) {
                        let image_type = data.picture.format;
                        let extensions = {
                            'image/jpeg': 'jpg',
                            'image/png': 'png'
                        }
                        if (image_type in extensions) {
                            let ext = extensions[image_type];
                            let image_root = `${this.settings.image_root}`
                            original_image_file = `cover_original_${id}.${ext}`
                            large_image_file = `cover_large_${id}.${ext}`
                            medium_image_file = `cover_medium_${id}.${ext}`
                            small_image_file = `cover_small_${id}.${ext}`
                            Jimp.read(
                                new Buffer(data.picture.data),
                                (err, image) => {
                                    if (err) throw err;
                                    image.write(`${image_root}/${original_image_file}`);
                                    image.resize(320,320).write(`${image_root}/${large_image_file}`)
                                    image.resize(160,160).write(`${image_root}/${medium_image_file}`)
                                    image.resize(100,100).write(`${image_root}/${small_image_file}`)
                                }
                            )
                        }
                    }
                    let NOW = new Date()
                    let track_info = {
                        'id': id,
                        'title': STRING(addslashes(data.title)),
                        'artist': STRING(addslashes(data.artist)),
                        'album': STRING(addslashes(data.album)),
                        'year': STRING(none_to_null(data.year)),
                        'genre': STRING(addslashes(data.genre)),
                        'bpm': STRING(none_to_null(data.bpm)),
                        'rating': data.rating,
                        'disabled': 0,
                        'favorite': data.favorite,
                        'comments': STRING(addslashes(null)),
                        'waveform': "NULL", 
                        'cover_medium': STRING(addslashes(medium_image_file)),
                        'cover_small': STRING(addslashes(small_image_file)),
                        'cover_large': STRING(addslashes(large_image_file)),
                        'cover_original': STRING(addslashes(original_image_file)),
                        'track_length': data.duration,
                        'stream_start': 0,
                        'stream_end': data.duration,
                        'stream_length': data.duration,
                        'color': "NULL",
                        'date_added': DATE(NOW),
                        'date_modified': DATE(NOW),
                        'bitrate': data.bit_rate,    
                        'samplerate': data.samplerate, 
                        'file_name': STRING(addslashes(mp3_file)),
                        'original_file_name': STRING(addslashes(data.filename)),
                        'file_size': data.file_size, 
                        'hash': 'NULL',
                        'grouping': STRING(none_to_null(addslashes(data.grouping))),
                        'category': 'NULL', 
                        'description': 'NULL', 
                    }
                    DB.add_track(track_info, () => {this._add_tracks (settings, id+1, total)})
                // }
            //             foo.src = mp3_path
             }).catch(console.log)
        } else {
            this._win.hide();
        }
    }
    
}





class TrackAdder extends EventDispatcher {
    constructor(filenames) {
        super()
        this.filenames = filenames
        this._num = this.filenames.length
        this.track_info_array = []
        this.track_info_editor = undefined
        this.display_track_info()
    }

    parse_tag(filename, tag) {
        var p_tag = {
            filename: filename,
            title: tag.tags.title,
            artist: tag.tags.artist,
            album: tag.tags.album,
            genre: tag.tags.genre,
            year: tag.tags.year,
            comment: tag.tags.comment,
            picture: tag.tags.picture,
            favorite:0,
            rating:0
        }
        if (tag.type == 'ID3') {
            p_tag.bpm = (tag.tags.TBPM != undefined) ? tag.tags.TBPM.data : null;
            p_tag.grouping = null;
        }
        let bit_info = mp3Duration(filename)
        p_tag.duration = bit_info.duration
        p_tag.file_size = bit_info.file_size
        p_tag.bit_rate = bit_info.bit_rate
        p_tag.samplerate = bit_info.samplerate
        return p_tag;
    }

    display_track_info () {
        for (let i=0; i<this.filenames.length; i++) {
            jsmediatags.read(this.filenames[i], {
                    onSuccess: (tag) => {
                        this._num --;
                        this.track_info_array.push(this.parse_tag(this.filenames[i], tag));
                            if (this._num == 0) {
                                this.show_track_info_editor()
                            }
                    },
                    onError: function(error) {
                        num --;
                        if (num == 0) {
                            this.show_track_info_editor()
                        }
                    }
                }
            );
        }
    }

    color(e) {
        if (e.color != undefined) {
            return `<span style='background-color:${e.color}; border-radius:4px; padding-right:10px;'>&nbsp</span> ${e.color}`
        } else {
            return `<span style='background-color:#ffffff; border-radius:4px; padding-right:10px;'>&nbsp</span> Default`
        }
    }

    rating(obj, common, value) {
        var html = "";
        for (var i=1; i<6; i++) {
            html+="<div rating='"+i+"' class='rating_star fa " + ( i <= obj.rating ? "fa-star" : "fa-star-o") +"' style='font-size: 14px'></div>";
        }
        return html
    }

    custom_checkbox(obj, common, value){
        return `<label class="favorite">
                    <input type="checkbox" ${obj.favorite == 0 ? "unckecked" : "checked"}>
                    <i class="fa fa-heart-o unchecked"></i>
                    <i class="fa fa-heart checked"></i>
                </label>`;
    }

    show_track_info_editor() {
        this.editor_window = webix.ui({
            view:"window",
            modal:true,
            position:"center",
            width:1600,
            height:950,
            head: "ADD TRACKS",
            body:{
                rows:[
                    {height:10},
                    {
                        view:"datatable",
                        id:"add_file_list",
                        select:"row",
                        editaction:'dblclick',
                        editable: true,
                        resizeColumn:{headerOnly:true},
                        css:{
                            'background-color':'#303030',
                            border: '0px solid #5c5c5c'
                         },
                        data: this.track_info_array,
                        columns:[
                            { 
                                id:"id",            
                                header:"",  
                                width:30, 
                                hidden:true
                            },
                            { 
                                id:"color",      
                                header:"<b>Color</b>",  
                                width:125, 
                                sort:'string', 
                                template: this.color , 
                                editor: 'color'
                            },
                            { 
                                id:"title",         
                                header:"<b>Title</b>",  
                                fillspace:true, 
                                sort:'string', 
                                editor: 'text'
                            },
                            { 
                                id:"artist",        
                                header:"<b>Artist</b>", 
                                fillspace:true, 
                                sort:'string', 
                                editor: 'text'
                            },
                            { 
                                id:"album",         
                                header:"<b>Album</b>",  
                                fillspace:true, 
                                sort:'string', 
                                editor: 'text'
                            },
                            { 
                                id:"year",          
                                header:"<b>Year</b>",   
                                width:75, 
                                sort:'string', 
                                editor: 'text'
                            },
                            { 
                                id:"genre",         
                                header:"<b>Genre</b>",  
                                width:110, 
                                sort:'string', 
                                editor: 'text'
                            },
                            { 
                                id:"grouping",      
                                header:"<b>Grouping</b>", 
                                fillspace:true, 
                                sort:'string', 
                                editor: 'text'
                            },
                            { 
                                id:"bit_rate",      
                                header:"<b>Kbps</b>", 
                                width:75,
                                sort:'int', 
                                // editor: 'text'
                            },
                            { 
                                id:"samplerate",      
                                header:"<b>Freq</b>", 
                                width:75,
                                sort:'int', 
                            },
                            { 
                                id:"file_size",      
                                header:"<b>Size</b>", 
                                width:75,
                                sort:'int', 
                            },
                            { 
                                id:"bpm", 
                                header: {
                                    text:"<b style='font-size: 13px'><span class='fa fa-heartbeat' style='font-size: 15px'/></b>", 
                                    css:{"text-align":'center'}
                                }, 
                                width:50, 
                                css: { 
                                    "text-align":'right'
                                }, 
                                sort:'int', 
                            },
                            { 
                                id:"rating",        
                                header:"<b>Rating</b>", 
                                width:125, 
                                sort:'string', 
                                template: (x, y, z) => this.rating(x, y, z),
                            },
                            { 
                                id:"favorite",      
                                header: {
                                    text: "<b><span class='fa fa-heart' style='font-size: 12px'/></b>", 
                                    height:25
                                },  
                                width:30, 
                                checkValue:1, 
                                uncheckValue:0,
                                template: (x, y, z) => this.custom_checkbox(x, y, z),
                                sort:'int', 
                            },
                            { 
                                id:"length",        
                                header:"<b>Time</b>", 
                                width:100, 
                                sort:'int',
                                template: (o) => {
                                    return `${format_nanoseconds(o.duration)}`
                                }
    
                            },
                        ],
                        onClick:{
                            favorite: (e, id)=> {
                                var item = $$("add_file_list").getItem(id.row);
                                if (item.favorite == 1) {
                                    item.favorite = 0
                                } else {
                                    item.favorite = 1
                                }
                                $$("add_file_list").updateItem(id.row, item)
                            },
                            rating_star: (e, id) => {
                                console.log(e)
                                var item = $$("add_file_list").getItem(id.row);
                                item.rating = e.target.getAttribute('rating')
                                $$("add_file_list").updateItem(id.row, item)
                            }
                        },
                    },
                    {height:30},
                    {
                        cols:[
                            {},
                            {
                                view: 'button',
                                label: 'ADD',
                                click: () => {
                                    this.editor_window.hide();
                                    this.perform_add_to_database();
                                }
                            },
                            {},
                            {
                                view: 'button',
                                label: 'CANCEL',
                                click: () => {this.editor_window.hide();}
                            },
                            {}
                        ]
                    },
                    {height:10}
                ]
            }
        })
        this.editor_window.show();
    }

    perform_add_to_database() {
        db_connection.query(
            "SELECT db_image_cache as image_root, db_music_cache as music_root, db_waveform_cache as waveform_root FROM settings",
            function (error, settings) {
                settings=settings[0]
                if (error) throw error;
                db_connection.query(
                    "SELECT max(id) + 1 AS first_available_id FROM tracks",
                    function (error, id_result) {
                        if (error) throw error;
                        var first_available_id = null;
                        if (id_result[0].first_available_id != null) {
                            first_available_id = id_result[0].first_available_id;
                        } else {
                            first_available_id = 1;
                        }
                        let items_to_add = []
                        $$('add_file_list').eachRow(
                            function (row) {
                                items_to_add.push($$('add_file_list').getItem(row))
                            }
                        )
                        var x = new TrackAddProgressDialog(settings, first_available_id, items_to_add)
                    }
                )
            }
        )
    }    
}

