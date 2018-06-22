var jsmediatags = require("jsmediatags");
var fs = require('fs');
const {spawn} = require ('child_process');
var async = require('async');
var Jimp = require("jimp");
var AV = require('av');
require('mp3.js');

var files_to_add = null;
var items_to_hide = null;
var conv_test_folder = '/Users/jihemme/Python/DJ/conv_test'
var conv_test_folder_img = '/Users/jihemme/Python/DJ/conv_test/images'
var audio_info = null;



function addslashes(s) {
    if (s == null) return null;
    o = ""
    d = {'"': '\\"',
         "'": "\\'",
         "\0":"\\\0",
         "\\": "\\\\"}

    for (var i=0; i<s.length; i++) {
        if (s[i] in d) {
            o += d[s[i]]
        } else {
            o += s[i]
        }
    }
    return o
}

function none_to_null(v) {
    return  (v == null) ? null : v
}

function none_to_zero(v) {
    return  (v == null) ? 0 : v
}

function bool_to_int(b) {
    return b ? 1 : 0
}

function STRING(s) {
    return (s != null) ? `'${s}'` : 'NULL'
}

function DATE(s) {
    pad = function(num) {
                var norm = Math.floor(Math.abs(num));
                //if (norm == 0)
                return (norm < 10 ? '0' : '') + norm;
            };
    d = `${s.getFullYear()}-${pad(s.getMonth()+1)}-${pad(s.getDate())}T${pad(s.getHours())}:${pad(s.getMinutes())}:${pad(s.getSeconds())}`
    return `'${d}'`
}

var track_add_progress_dialog =  webix.ui({
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
track_add_progress_dialog.hide();

function add_selected_files_to_database (settings, id, total) {
    if (items_to_add.length > 0) {
        let data = items_to_add.pop();
        let mp3_file = `track_${id}.mp3`
        let mp3_path = `${settings.music_root}/${mp3_file}`
        converter = spawn('avconv', ['-y', '-i', data.filename, '-acodec', 'libmp3lame', '-ab',  '320k', '-vn', '-r', '48000', mp3_path])
        var original_image_file = null;
        var large_image_file = null;
        var medium_image_file = null;
        var small_image_file = null;
        var wave_path = null;

        $$('track_add_progress').define('label', `ADDING TRACK ${total - items_to_add.length} OF ${total}`)
        $$('track_add_progress').refresh()
        $$('track_add_title').define('label', `<b>${data.title}</b>`)
        $$('track_add_title').refresh()
        $$('track_add_artist').define('label', `${data.artist} - ${data.album}`)
        $$('track_add_artist').refresh()

        converter.stdout.on(
            'data',
            function (data) {
                console.log(data)
            }
        )
        converter.on(
            'error',
            function (err) {
                console.log(err)
            }
        )
        converter.on(
            'close',
            function () {
                if (data.picture != undefined) {
                    image_type = data.picture.format;
                    extensions = {
                        'image/jpeg': 'jpg',
                        'image/png': 'png'
                    }
                    if (image_type in extensions) {
                        ext = extensions[image_type];
                        original_image_file = `cover_original_${id}.${ext}`
                        large_image_file = `cover_large_${id}.${ext}`
                        medium_image_file = `cover_medium_${id}.${ext}`
                        small_image_file = `cover_small_${id}.${ext}`
                        Jimp.read(
                            new Buffer(data.picture.data),
                            function (err, image) {
                                if (err) throw err;
                                image.write(`${settings.image_root}/${original_image_file}`);
                                image.resize(320,320).write(`${settings.image_root}/${large_image_file}`)
                                image.resize(160,160).write(`${settings.image_root}/${medium_image_file}`)
                                image.resize(100,100).write(`${settings.image_root}/${small_image_file}`)
                            }
                        )
                    }
                }
                wave_file = `waveform_${id}.wv`
                wave_path = `${settings.waveform_root}/${wave_file}`
                waveform_generator = spawn(
                    'python', ['-m', 'python.generate_waveform', mp3_path, wave_path]
                )
                waveform_generator.on(
                    'close',
                    function () {
                        bit_output = ""
                        bit_info = spawn(
                            'python', ['-m', 'python.file_info', mp3_path]
                        )
                        bit_info.stdout.on(
                            'data', function (x) {
                                console.log(x.toString())
                                bit_output += x.toString()
                            }
                        )
                        bit_info.on(
                            'close',
                            function () {
                                console.log(bit_output);
                                console.log(JSON.parse(bit_output));
                                bit_output = JSON.parse(bit_output);
                                NOW = new Date()
                                track_info = {
                                    'id': id,
                                    'title': STRING(addslashes(data.title)),
                                    'artist': STRING(addslashes(data.artist)),
                                    'album': STRING(addslashes(data.album)),
                                    'year': STRING(none_to_null(data.year)),
                                    'genre': STRING(addslashes(data.genre)),
                                    'bpm': STRING(none_to_null(data.bpm)),
                                    'rating': 0,
                                    'disabled': 0,
                                    'favorite': 0,
                                    'comments': STRING(addslashes(null)),
                                    'waveform': STRING(addslashes(wave_file)),
                                    'cover_medium': STRING(addslashes(medium_image_file)),
                                    'cover_small': STRING(addslashes(small_image_file)),
                                    'cover_large': STRING(addslashes(large_image_file)),
                                    'cover_original': STRING(addslashes(original_image_file)),
                                    'track_length': bit_output.length,
                                    'stream_start': 0,
                                    'stream_end': bit_output.length,
                                    'stream_length': bit_output.length,
                                    'date_added': DATE(NOW),
                                    'date_modified': DATE(NOW),
                                    'bitrate': bit_output.bitrate,
                                    'samplerate': bit_output.samplerate,
                                    'file_name': STRING(addslashes(mp3_file)),
                                    'original_file_name': STRING(addslashes(data.filename)),
                                    'file_size': bit_output.file_size,
                                    'hash': 'NULL',
                                    'grouping': STRING(none_to_null(addslashes(data.grouping))),
                                    'category': STRING(none_to_null(addslashes(data.category))),
                                    'description': STRING(none_to_null(addslashes(data.description)))
                                }
                                console.log(track_info);
                                console.log(ADD_TRACK(track_info))
                                db_connection.query(
                                    ADD_TRACK(track_info),
                                    function (error, _) {
                                        if (error) throw error;

                                        add_selected_files_to_database (settings, id+1, total)
                                    }
                                )

                            }
                        )
                    }
                )
            }
        )
    } else {
        track_add_progress_dialog.hide();
    }
}

function ADD_TRACK(track_info) {
    return `
    INSERT INTO tracks (
    id, title, artist, album, year, genre, bpm, rating, favorite, comments, waveform, cover_medium,
    cover_small, cover_large, cover_original, track_length, stream_start, stream_end, stream_length,
    date_added, date_modified, bitrate, samplerate, file_name, file_size, hash, category, description,
    disabled, original_file_name, grouping)
    VALUES
    (${track_info.id},${track_info.title}, ${track_info.artist}, ${track_info.album}, ${track_info.year},
    ${track_info.genre}, ${track_info.bpm}, ${track_info.rating}, ${track_info.favorite}, ${track_info.comments},
    ${track_info.waveform}, ${track_info.cover_medium}, ${track_info.cover_small}, ${track_info.cover_large},
    ${track_info.cover_original}, ${track_info.track_length}, ${track_info.stream_start}, ${track_info.stream_end},
    ${track_info.stream_length}, ${track_info.date_added}, ${track_info.date_modified}, ${track_info.bitrate},
    ${track_info.samplerate}, ${track_info.file_name}, ${track_info.file_size}, ${track_info.hash}, ${track_info.category},
    ${track_info.description}, ${track_info.disabled}, ${track_info.original_file_name}, ${track_info.grouping})`
}


function perform_add_to_database() {
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
                    items_to_add = []
                    $$('add_file_list').eachRow(
                        function (row) {
                            items_to_add.push($$('add_file_list').getItem(row))
                        }
                    )
                    $$('track_add_progress').define('label', ``)
                    $$('track_add_progress').refresh()
                    $$('track_add_title').define('label', ``)
                    $$('track_add_title').refresh()
                    $$('track_add_artist').define('label', ``)
                    $$('track_add_artist').refresh()
                    track_add_progress_dialog.show();
                    add_selected_files_to_database(settings, first_available_id, items_to_add.length)
                }
            )
        }
    )
}

function parse_tag(filename, tag) {
    var type = tag.type;
    var p_tag = {
        filename: filename,
        title: tag.tags.title,
        artist: tag.tags.artist,
        album: tag.tags.album,
        genre: tag.tags.genre,
        year: tag.tags.year,
        comment: tag.tags.comment,
        picture: tag.tags.picture,
    }
    if (tag.type == 'MP4') {
        p_tag.bpm = (tag.tags.tmpo != undefined) ? tag.tags.tmpo.data : null;
        p_tag.grouping = (tag.tags['\xa9grp'] != undefined) ? tag.tags['\xa9grp'].data : null;
        p_tag.category = (tag.tags['catg'] != undefined) ? tag.tags['catg'].data : null;
        p_tag.description = (tag.tags['desc'] != undefined) ? tag.tags['desc'].data : null;
    } else if (tag.type == 'ID3') {
        p_tag.bpm = (tag.tags.TBPM != undefined) ? tag.tags.TBPM.data : null;
        p_tag.grouping = '11';
        p_tag.category = null;
        p_tag.description = null;
    }

    return p_tag;
}

function select_tracks_to_add() {
    dialog.showOpenDialog(
        { properties: [ 'openFile', 'multiSelections']},
        function (filenames) {
            let num = filenames.length;
            let new_array = []
            for (let i=0; i<filenames.length; i++) {
                jsmediatags.read(filenames[i], {
                      onSuccess: function(tag) {
                          num --;
                          console.log(i, tag);
                          console.log(parse_tag(filenames[i], tag))
                          new_array.push(parse_tag(filenames[i], tag));
                          if (num == 0) {
                              $$('add_file_list').clearAll();
                              $$('add_file_list').define('data', new_array);
                              $$('add_file_list').refresh();
                              console.log(new_array);
                              console.log('DONE');
                              files_to_add = new_array;
                          }
                      },
                      onError: function(error) {
                          num --;
                          if (num == 0) {
                              $$('add_file_list').clearAll();
                              $$('add_file_list').define('data', new_array);
                              $$('add_file_list').refresh();
                              files_to_add = new_array;
                          }
                      }
                    }
                );
            }
        }
    )
}

function cover_art_b64(object) {
    if (object != undefined) {
        var u8 = new Uint8Array(object.data);
        var decoder = new TextDecoder('utf8');
        var b64encoded = btoa(decoder.decode(u8));
        image_format = object.format;
        console.log(b64encoded);
        return `<img src="data:${image_format};base64,${b64encoded}" />`
    }
    else {
        cover_size = 50;
        cover_source = "../resources/images/default_album_cover.png"
        return `<img style="padding-right:0px; padding-left:-10px; margin-left:-10px" src="${cover_source}" height='${cover_size}' width='${cover_size}'></img>`
    }
}

function add_track() {
    x = webix.ui({
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
                    cols: [
                        {
                            id:'wait_time',
                            view: "text",
                            value: `$HOME`,
                            labelWidth:100,
                            label:"Search folder:"
                        },
                        {
                            view: 'button',
                            type: 'icon',
                            icon: 'folder',
                            autowidth: true,
                            label: 'Browse',
                            click: select_tracks_to_add
                        }
                    ]
                },
                {height:30},
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
                    columns:[
                        { id:"id",            header:"",  width:30, hidden:true},
                        { id:"title",         header:"<b>Title</b>",  fillspace:true, sort:'string', editor: 'text'},
                        { id:"artist",        header:"<b>Artist</b>", fillspace:true, sort:'string', editor: 'text'},
                        { id:"album",         header:"<b>Album</b>",  fillspace:true, sort:'string', editor: 'text'},
                        { id:"year",          header:"<b>Year</b>",   width:50, sort:'string', editor: 'text'},
                        { id:"genre",         header:"<b>Genre</b>",  width:110, sort:'string', editor: 'text'},
                        { id:"bpm",           header:{text:"<b>BPM</b>", css:{"text-align":'center'}},    width:50, css:{"text-align":'right'}, sort:'int', editor: 'text'},
                        { id:"grouping",      header:"<b>Grouping</b>", fillspace:true, sort:'string', editor: 'text'},
                        { id:"category",      header:"<b>Category</b>",  fillspace:true, sort:'string', editor: 'text'},
                        { id:"description",   header:"<b>Description</b>", fillspace:true, sort:'string', editor: 'text'},
                    ],
            },
                {height:30},
                {
                    cols:[
                        {},
                        {
                            view: 'button',
                            label: 'ADD',
                            click: function () {
                                x.hide();
                                perform_add_to_database();
                            }
                        },
                        {},
                        {
                            view: 'button',
                            label: 'CANCEL',
                            click: () => {x.hide()}
                        },
                        {}
                    ]
                },
                {height:10}
            ]
        }
    })
    x.show();
}
