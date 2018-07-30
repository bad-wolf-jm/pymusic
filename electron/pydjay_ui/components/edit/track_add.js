// TODO

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

        this.track_add_progress_id = this.ID()
        this.track_add_title_id = this.ID()
        this.track_add_artist_id = this.ID()

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
                        id:this.track_add_progress_id,
                        view: "label",
                        label:"Processing track ### of ###",
                        css: {
                            'text-align': 'center',
                            'font-size':  '20px',
                        }
                    },
                    {height:10},
                    {
                        id:this.track_add_title_id,
                        view: "label",
                        label:"Title Of Song",
                        css: {
                            'text-align': 'center',
                            'font-size': '20px',
                        }
        
                    },
                    {
                        id:this.track_add_artist_id,
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

    ID () {
        return '_' + Math.random().toString(36).substr(2, 9);
      };

    getFileExtension(f_name) {
        return f_name.slice((Math.max(0, f_name.lastIndexOf(".")) || Infinity) + 1);
    }
    
    _add_tracks (settings, id, total) {
        if (this.track_list.length > 0) {
            let data = this.track_list.pop();
            let mp3_file = `track_${id}.${this.getFileExtension(data.filename)}`
            let mp3_path = `${this.settings.music_root}/${mp3_file}`
            var original_image_file = null;
            var large_image_file = null;
            var medium_image_file = null;
            var small_image_file = null;
    
            $$(this.track_add_progress_id).define('label', `ADDING TRACK ${total - this.track_list.length} OF ${total}`)
            $$(this.track_add_progress_id).refresh()
            $$(this.track_add_title_id).define('label', `<b>${data.title}</b>`)
            $$(this.track_add_title_id).refresh()
            $$(this.track_add_artist_id).define('label', `${data.artist} - ${data.album}`)
            $$(this.track_add_artist_id).refresh()
    
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
                        'color': (data.color == undefined || data.color == "") ? "NULL" : STRING(data.color),
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

        this.add_file_list_id = this.ID()

        this.display_track_info()
    }

    ID () {
        return '_' + Math.random().toString(36).substr(2, 9);
      };


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
        console.log(e.color)
        if ((e.color != undefined) && (e.color != "")) {
            return `<span style='background-color:${e.color}; border-radius:4px; padding-right:10px;'>&nbsp&nbsp&nbsp</span> ${e.color}`
        } else {
            return `<span style='background-color:#ffffff; border-radius:4px; padding-right:10px;'>&nbsp&nbsp&nbsp</span> Default`
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
                        id:this.add_file_list_id,
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
                                width:100, 
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
                                header: {
                                    text:"<b>Year</b>", 
                                    css:{"text-align":'right'}
                                }, 
                                width:55, 
                                sort:'string', 
                                editor: 'text',
                                css: { 
                                    "text-align":'right'
                                }, 
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
                                width:135, 
                                sort:'string', 
                                editor: 'text'
                            },
                            { 
                                id:"bit_rate",      
                                header: {
                                    text: "<b>Kb/s</b>", 
                                    css:{"text-align":'right'},
                                    height:25
                                },  
                                width:55,
                                sort:'int', 
                                css: { 
                                    "text-align":'right'
                                }, 

                                // editor: 'text'
                            },
                            { 
                                id:"samplerate",      
                                header: {
                                    text: "<b>Freq.</b>", 
                                    css:{"text-align":'right'},
                                    height:25
                                },  
                                width:75,
                                sort:'int',                                 
                                css: { 
                                    "text-align":'right'
                                }, 

                            },
                            { 
                                id:"file_size",      
                                header: {
                                    text: "<b>Size</b>", 
                                    css:{"text-align":'right'},
                                    height:25
                                },  
                                width:75,
                                template: (o) => {
                                    return humanFileSize(o.file_size)
                                },
                                css: { 
                                    "text-align":'right'
                                }, 
                                sort:'int', 
                            },
                            { 
                                id:"bpm", 
                                header: {
                                    text:"<b style='font-size: 13px'><span class='fa fa-heartbeat' style='font-size: 15px'/></b>", 
                                    css:{"text-align":'right'}
                                }, 
                                width:50, 
                                css: { 
                                    "text-align":'right'
                                }, 
                                sort:'int', 
                            },
                            { 
                                id:"rating",        
                                //header:"<b>Rating</b>", 
                                header: {
                                    text:"<b>Rating</b>", 
                                    css:{"text-align":'right'}
                                }, 
                                width:80, 
                                sort:'string',                                 
                                css: { 
                                    "text-align":'right'
                                }, 

                                template: (x, y, z) => this.rating(x, y, z),
                            },
                            { 
                                id:"favorite",      
                                header: {
                                    text: "<b><span class='fa fa-heart' style='font-size: 12px'/></b>", 
                                    css:{"text-align":'right'},
                                    height:25
                                },  
                                width:30, 
                                checkValue:1, 
                                uncheckValue:0,
                                template: (x, y, z) => this.custom_checkbox(x, y, z),
                                sort:'int', 
                                css: { 
                                    "text-align":'center'
                                }, 
                            },
                            { 
                                id:"length",        
                                header:"<b>Time</b>", 
                                header: {
                                    text: "<b>Time</b>", 
                                    css:{"text-align":'right'},
                                    height:25
                                },  
                                width:65, 
                                sort:'int',
                                template: (o) => {
                                    return `${format_nanoseconds(o.duration)}`
                                },
                                css: { 
                                    "text-align":'right'
                                }, 
    
                            },
                        ],
                        onClick:{
                            favorite: (e, id)=> {
                                var item = $$(this.add_file_list_id).getItem(id.row);
                                if (item.favorite == 1) {
                                    item.favorite = 0
                                } else {
                                    item.favorite = 1
                                }
                                $$(this.add_file_list_id).updateItem(id.row, item)
                            },
                            rating_star: (e, id) => {
                                console.log(e)
                                var item = $$(this.add_file_list_id).getItem(id.row);
                                item.rating = e.target.getAttribute('rating')
                                $$(this.add_file_list_id).updateItem(id.row, item)
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
        DB.get_settings(
            (settings) => {
                let items_to_add = []
                $$(this.add_file_list_id).eachRow(
                    (row) => {
                        items_to_add.push($$(this.add_file_list_id).getItem(row))
                    }
                )
                var x = new TrackAddProgressDialog(settings, settings.next_id, items_to_add)
            }
        )
    }    
}

