var jsmediatags = require("jsmediatags");
var fs = require('fs-extra');
var path = require('path');
const {spawn} = require ('child_process');
// var async = require('async');
var Jimp = require("jimp");
const { TrackImportProgressDialog } = require("iface/dialogs/track_add_progress")

// function trackBSON(tr) {
//     let track_object = {
//         metadata: {
//             title: tr.title,
//             artist: tr.artist,
//             album: tr.album,
//             genre: tr.genre,
//             year: tr.year,
//             color: tr.color,
//             tags: []
//         },
//         track: {
//             duration: tr.track_length / 1000000,
//             stream_start: tr.stream_start / 1000000,
//             stream_end: tr.stream_end / 1000000,
//             bpm: tr.bpm,
//             bitrate: tr.bitrate,
//             samplerate: tr.samplerate,
//             size: tr.file_size,
//             path: path.join(tr.music_root, tr.file_name)
//         },
//         stats: {
//             loved: tr.favorite,
//             rating: tr.rating,
//             last_played: null,
//             play_count: 0,
//             relations: {}
//         },
//         createdAt: tr.date_added,
//         updatedAt: tr.date_modified,
//     }
//     if (tr.cover_original != null) {
//         track_object.metadata.cover = {
//             original: path.join(tr.image_root, tr.cover_original),
//             small: path.join(tr.image_root, tr.cover_small),
//             medium: path.join(tr.image_root, tr.cover_medium),
//             large: path.join(tr.image_root, tr.cover_large),
//         }
//     }
//     return track_object
// }


function parse_tag(filename, tag) {

    var p_tag = {
        filename: filename,
        title: tag.tags.title,
        artist: tag.tags.artist,
        album: tag.tags.album,
        genre: tag.tags.genre,
        year: tag.tags.year,
        comment: tag.tags.comment.text,
        picture: tag.tags.picture,
        loved: 0,
        rating: 0
    }
    if (tag.type == 'ID3') {
        p_tag.bpm = (tag.tags.TBPM != undefined) ? tag.tags.TBPM.data : null;
    }
    let bit_info = mp3Duration(filename)
    p_tag.duration = bit_info.duration
    p_tag.file_size = bit_info.file_size
    p_tag.bit_rate = bit_info.bit_rate
    p_tag.samplerate = bit_info.samplerate
    return p_tag;
}


function read_metadata(filename) {
    return new Promise(function(resolve, reject) {
      jsmediatags.read(filename, {
        onSuccess: function(tag) {
          resolve(parse_tag(filename, tag));
        },
        onError: function(error) {
          reject(error);
        }
      });
    });
  }

class TrackAdder extends EventDispatcher {
    constructor(filenames, library) {
        super()
        this.filenames = filenames
        this._library = library
        this._num = this.filenames.length
        this._progress = 0
        this.track_info_array = []
        this.track_info_editor = undefined
        this.progress_dialog = new TrackImportProgressDialog()
        this.progress_dialog.open()
        // document.getElementById('track-add-progress-dialog').showModal()
        this.add_all_tracks()
    }

    getFileExtension(f_name) {
        return f_name.slice((Math.max(0, f_name.lastIndexOf(".")) || Infinity) + 1);
    }

    async add_all_tracks() {
        for (let i=0; i<this.filenames.length; i++) {
            this.progress_dialog.setProgress(i+1, this.filenames.length)
            let added = await this._library.addFile(this.filenames[i])
            this.progress_dialog.setCurrent(added)
        }

        this.progress_dialog.close()
    }


    _perform_add(settings, image, data, continuation) {
        //console.log(data)
        fs.copy(data.filename, data.mp3_path).then( () => {
            if (image != null) {
                image.write(`${path.join(settings.image_root, data.original_image_file)}`);
                image.resize(320,320).write(`${path.join(settings.image_root, data.large_image_file)}`)
                image.resize(160,160).write(`${path.join(settings.image_root, data.medium_image_file)}`)
                image.resize(100,100).write(`${path.join(settings.image_root, data.small_image_file)}`)      
            }
            let NOW = new Date()
            let track_info = {
                'id':     data.id,
                'title':  STRING(addslashes(data.title)),
                'artist': STRING(addslashes(data.artist)),
                'album':  STRING(addslashes(data.album)),
                'year':   STRING(none_to_null(data.year)),
                'genre':  STRING(addslashes(data.genre)),
                'bpm':    STRING(none_to_null(data.bpm)),
                'rating': data.rating,
                'disabled': 0,
                'favorite': data.favorite,
                'comments': STRING(addslashes(null)),
                'waveform': "NULL", 
                'cover_medium': STRING(none_to_null(addslashes(data.medium_image_file))),
                'cover_small':  STRING(none_to_null(addslashes(data.small_image_file))),
                'cover_large':  STRING(none_to_null(addslashes(data.large_image_file))),
                'cover_original': STRING(none_to_null(addslashes(data.original_image_file))),
                'track_length':  data.duration,
                'stream_start':  0,
                'stream_end':    data.duration,
                'stream_length': data.duration,
                'color': (data.color == undefined || data.color == "") ? "NULL" : STRING(data.color),
                'date_added':   DATE(NOW),
                'date_modified': DATE(NOW),
                'bitrate':    data.bit_rate,    
                'samplerate': data.samplerate, 
                'file_name':   STRING(addslashes(data.mp3_file)),
                'original_file_name': STRING(addslashes(data.filename)),
                'file_size': data.file_size, 
                'hash':        'NULL',
                'grouping':    STRING(none_to_null(addslashes(data.grouping))),
                'category':    'NULL', 
                'description': 'NULL', 
            }
            DB.add_track(track_info, () => {
                document.getElementById("track-add-progress").innerHTML = `Added track ${this._progress} of ${this._num}`
                document.getElementById("track-add-info").innerHTML = `${data.title} - ${data.artist}`
                continuation()
            })
        })
    }


    add_single_track(filename, continuation) {
        DB.get_settings((settings) => {
            jsmediatags.read(filename, {
                onSuccess: (tag) => {
                    this._progress++;
                    let t = this.parse_tag(filename, tag)

                    let data = t //this.track_list.pop();
                    data.id = settings.next_id
                    data.mp3_file = `track_${settings.next_id}.${this.getFileExtension(data.filename)}`
                    data.mp3_path = path.join(settings.music_root, data.mp3_file)
                    var original_image_file = null;
                    var large_image_file = null;
                    var medium_image_file = null;
                    var small_image_file = null;
                    
                    if (data.picture != undefined) {
                        let image_type = data.picture.format;
                        let extensions = {
                            'image/jpeg': 'jpg',
                            'image/png': 'png'
                        }
                        if (image_type in extensions) {
                            Jimp.read(
                                new Buffer(data.picture.data),
                                (err, image) => {
                                    if (err) throw err;
                                    let ext = extensions[image_type];
                                    let image_root = `${settings.image_root}`
                                    data.original_image_file = `cover_original_${settings.next_id}.${ext}`
                                    data.large_image_file    = `cover_large_${settings.next_id}.${ext}`
                                    data.medium_image_file   = `cover_medium_${settings.next_id}.${ext}`
                                    data.small_image_file    = `cover_small_${settings.next_id}.${ext}`
                                    this._perform_add(settings, image, data, continuation)
                                }
                            )
                        } else {
                            data.original_image_file = null
                            data.large_image_file    = null
                            data.medium_image_file   = null
                            data.small_image_file    = null
                            this._perform_add(settings, null, data, continuation)
        
                        }                            
                    } else {
                        data.original_image_file = null
                        data.large_image_file    = null
                        data.medium_image_file   = null
                        data.small_image_file    = null
                        this._perform_add(settings, null, data, continuation)
                    }  
                },
                onError: (error) => {
                    this._progress++;
                }
            });
        })
    }

    // add_all_tracks() {
    //     if (this.filenames.length > 0) {
    //         this.add_single_track(this.filenames.pop(), () => {
    //             this.add_all_tracks()
    //         })
    //     } else {
    //         tracks_model.refresh()
    //         document.getElementById('track-add-progress-dialog').close()

    //     }
    // }


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
}