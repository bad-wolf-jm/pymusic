var mysql = require('mysql');
var path = require('path');
const Datastore = require("nedb-async-await").Datastore;
// const MongoClient = require('mongodb').MongoClient;


// const connectionString = 'mongodb://localhost:27017';

// class Database {
//     constructor( config ) {
//         this.connection = mysql.createConnection( config );
//     }
//     query( sql, args ) {
//         return new Promise( ( resolve, reject ) => {
//             this.connection.query( sql, args, ( err, rows ) => {
//                 if ( err )
//                     return reject( err );
//                 resolve( rows );
//             } );
//         } );
//     }
//     close() {
//         return new Promise( ( resolve, reject ) => {
//             this.connection.end( err => {
//                 if ( err )
//                     return reject( err );
//                 resolve();
//             } );
//         } );
//     }
// }

class Playlist {
    constructor(db, object) {
        this.db = db
        this.object = object
    }

    getTracks() {
        return this.db.getTracksByIds(Object.keys(this.object.tracks)) 
    }

    duration() {
        return this.db.duration(Object.keys(this.object.tracks)) 
    }
}

class Session {
    constructor(db, object) {
        this.db = db
        this.object = object
    }

    async getTracks() {
        let track_ids = this.object.tracks.map((t) => {return t.track_id})
        let tracks = await this.db.getTracksByIds(track_ids)
        let x = {}
        tracks.forEach((t) => {x[t._id] = t})
        return this.object.tracks.map((t) => {return x[t.track_id]})
    }

    duration() {
        let track_ids = this.object.tracks.map((t) => {return t.track_id})
        return this.db.duration(track_ids) 
    }
}


class MusicDatabase {
    constructor(name) {

        this.tracks = Datastore({
            filename: path.join(".ds", name, "tracks.json"),
            autoload:true,
            timestampData:true})

        this.sessions = Datastore({
            filename: path.join(".ds", name, "sessions.json"),
            autoload:true, 
            timestampData:true})

        this.playlists = Datastore({
            filename: path.join(".ds", name, "playlists.json"),
            autoload:true,
            timestampData:true})

        this.logistics = Datastore({
            filename: path.join(".ds", name, "logistics.json"),
            autoload:true,
            timestampData:true})
        }

    getAllTracks() {
        return this.tracks.find({})
    }

    getTracksByIds(id_array) {
        if (id_array != undefined) {
            return this.tracks.find({"_id": {"$in":id_array}})
        } else {
            return this.tracks.find({})
        }
    }

    async getAllPlaylists() {
        let sessions = await this.playlists.find({})
        return sessions.map((s) => {return new Playlist(this, s)})
    }

    async getAllSessions() {
        let sessions = await this.sessions.find({})
        return sessions.map((s) => {return new Session(this, s)})
    }

    async duration(id_array) {
        let tracks = await this.getTracksByIds(id_array)
        let dur = 0
        tracks.forEach((track) => {
            dur += (track.bounds.end - track.bounds.start)
        })
        return dur
    }
}


function trackBSON(tr) {
    let track_object = {
        title: tr.title,
        artist: tr.artist,
        album: tr.album,
        genre: tr.genre,
        year: tr.year,
        color:  tr.color,
        duration: tr.track_length,
        favorite: tr.loved,
        rating: tr.rating,
        bpm: tr.bpm,
        createdAt: tr.date_added,
        updatedAt: tr.date_modified,
        bounds: {
            start: tr.stream_start,
            end: tr.stream_end
        },
        bitrate: tr.bitrate,
        samplerate: tr.samplerate,
        size: tr.file_size,
        path: path.join(tr.music_root, tr.file_name)
    }
    if (tr.cover_original != null) {
        track_object.cover = {
            original: path.join(tr.image_root, tr.cover_original),
            small: path.join(tr.image_root, tr.cover_small),
            medium: path.join(tr.image_root, tr.cover_medium),
            large: path.join(tr.image_root, tr.cover_large),
        }
    }
    return track_object
}

const db = new MusicDatabase("pymusic")


// async function mongo_insert(collection, record) {
//     //#let client = await MongoClient.connect(connectionString, { useNewUrlParser: true });
//     //#let db = client.db('pymusic');
//     try {
//         const res = await db.insert(record);

//         return res["_id"]
//      } catch (e) {
//         console.log(e) //record)
//      }
//     //  } finally {
//     //      client.close();
//     //  }
// }
main = async () => {
    // let x = await db.getAllTracks()
    // x.forEach((e) => {
    //     console.log(e)
    // })

    (await db.getAllSessions()).forEach(async (pl) => {
        console.log(pl.object.event, await pl.duration())
    })

}

main2 = async () => {
    let mysql = require('async-mysql'),
        connection,
        track_objects = {},
        rows;


    try {
        connection = await mysql.connect({host: 'localhost', user:"root", password:"root", database:'pymusic'});
        settings = await connection.query('SELECT * FROM settings');
        settings = settings[0]
        rows = await connection.query('SELECT * FROM tracks');

        for (let i=0; i < rows.length; i++) {
            let tr = rows[i]
            tr.image_root = settings.db_image_cache
            tr.music_root = settings.db_music_cache
            let track = trackBSON(tr)
            let relations = await connection.query(`SELECT * FROM track_relations WHERE track_id=${tr.id}`);
            let t_relations = relations.map((r) => {
                return {
                    track_id:r.related_track_id,
                    reatin:r.reason,
                    count: r.count,
                    date: r.date
                }
            })

            if (t_relations.length > 0) {
                track.relations = t_relations
            }
            new_id = await db.tracks.insert(track)
            track_objects[tr.id] = new_id["_id"]
        }

        let sessions = await connection.query('SELECT * FROM sessions');
        sessions.forEach(async (s) => {
            let session_data = {
                    event: s.event_name,
                    location: s.address,
                    createdAt:s.start_date,
                    date: {
                        begin: s.start_date,
                        end:  s.end_date
                    }
                }
            let session_tracks = await connection.query(`SELECT * FROM session_tracks WHERE session_id=${s.id} ORDER BY position`);
            session_data.tracks = session_tracks.map((t) => {
                return {
                    track_id:track_objects[t.track_id],
                    status:t.status,
                    time: {
                        begin: t.start_time,
                        end:   t.end_time}
                }
            })
            await db.sessions.insert(session_data)
        })

        let playlists = await connection.query('SELECT * FROM playlists');
        playlists.forEach(async (s) => {
            let playlist_data = {
                    name: s.name,
                    description: s.description,
                    createdAt: s.created
                }
            let playlist_tracks = await connection.query(`SELECT * FROM playlist_tracks WHERE playlist_id=${s.id}`);
            playlist_data.tracks = {}
            playlist_tracks.forEach((t) => {
                // let obj = {}
                playlist_data.tracks[track_objects[t.track_id]] = true
                // return obj
            })
            await db.playlists.insert(playlist_data)
        })
        console.log("done")

    } catch (e) {
        console.log(e)
    }
};

main();







// var db_connection = mysql.createConnection({
//   host: "localhost",
//   user: "root",
//   password: "root",
//   database:'pymusic'
// });

// function $QUERY(sql, with_result) {
//     db_connection.query(
//         sql,
//         function (error, result) {
//             // console.log(error, result)
//             if (error) {
//                 // console.log(error)
//                 throw error;
//             } else {
//                 // console.log(result)
//                 with_result(result);
//             }
//         }
//     )
// }


// function addslashes(s) {
//     if (s == null) return null;
//     o = ""
//     d = {'"': '\\"',
//          "'": "\\'",
//          "\0":"\\\0",
//          "\\": "\\\\"}

//     for (var i=0; i<s.length; i++) {
//         if (s[i] in d) {
//             o += d[s[i]]
//         } else {
//             o += s[i]
//         }
//     }
//     return o
// }

// function none_to_null(v) {
//     return  (v == null) ? null : v
// }

// function none_to_zero(v) {
//     return  (v == null) ? 0 : v
// }

// function bool_to_int(b) {
//     return b ? 1 : 0
// }

// function STRING(s) {
//     return (s != null) ? `'${s}'` : 'NULL'
// }

// function DATE(s) {
//     pad = function(num) {
//         var norm = Math.floor(Math.abs(num));
//         return (norm < 10 ? '0' : '') + norm;
//     };
//     d = `${s.getFullYear()}-${pad(s.getMonth()+1)}-${pad(s.getDate())}T${pad(s.getHours())}:${pad(s.getMinutes())}:${pad(s.getSeconds())}`
//     return `'${d}'`
// }

// function DataProvider() {
//     var self = this

//     self.base_track_view_sql = function () {
//         return `SELECT availability.track_id IS NULL AS available,
//                     tracks.id                     AS id,
//                     tracks.id                     AS track_id,
//                     tracks.favorite               AS favorite,
//                     tracks.disabled               AS enabled,
//                     tracks.title                  AS title,
//                     tracks.artist                 AS artist,
//                     tracks.file_name               AS file_name,
//                     tracks.stream_start           AS stream_start,
//                     tracks.stream_end             AS stream_end,
//                     tracks.track_length           AS track_length,
//                     tracks.grouping               AS grouping,
//                     tracks.year                   AS year,
//                     tracks.color                  AS color,
//                     tracks.album                  AS album,
//                     tracks.genre                  AS genre,
//                     tracks.rating                 AS rating,
//                     tracks.bpm                    AS bpm,
//                     tracks.bitrate                AS bitrate,
//                     tracks.samplerate             AS samplerate,
//                     tracks.file_size               AS file_size,
//                     tracks.date_added             AS date_added,
//                     tracks.date_modified           AS date_modified,
//                     tracks.stream_length          AS stream_length,
//                     foo.play_count                AS play_count,
//                     tracks.cover_original         AS cover_original,
//                     tracks.cover_small            AS cover_small,
//                     tracks.cover_medium           AS cover_medium,
//                     tracks.cover_large            AS cover_large,
//                     settings.db_image_cache       AS image_root,
//                     settings.db_music_cache       AS music_root,
//                     max_play_times.time           AS last_played
//             FROM    tracks
//                     JOIN (SELECT *
//                         FROM   tracks
//                                 JOIN (SELECT id                            AS id_2,
//                                             COUNT(session_tracks.track_id) AS play_count
//                                     FROM   tracks
//                                             LEFT JOIN session_tracks
//                                                     ON tracks.id = session_tracks.track_id
//                                     GROUP  BY id) play_counts
//                                 ON tracks.id = play_counts.id_2) foo
//                     ON tracks.id = foo.id
//                     LEFT JOIN ((SELECT track_id FROM   unavailable_tracks)
//                                 UNION
//                                 (SELECT track_id FROM   session_queue)) availability
//                     ON availability.track_id = tracks.id
//                     LEFT JOIN (SELECT track_id,
//                                     MAX(start_time) AS time
//                             FROM   session_tracks
//                             GROUP  BY track_id) max_play_times
//                         ON tracks.id = max_play_times.track_id
//                     LEFT JOIN settings
//                         ON 1 `
//     }

//     self.get_track_by_id = function (id, k) {
//         sql = self.base_track_view_sql()
//         sql += ` WHERE tracks.id=${id}`
//         $QUERY(sql, k)
//     }

//     self.get_all_tracks = function (k) {
//         let sql = self.base_track_view_sql()
//         sql += ` ORDER BY title`
//         $QUERY(sql, k);
//     }

//     self.get_related_tracks = function (id, k) {
//         let sql = `(${self.base_track_view_sql()}) tracks_view`
//         sql = `SELECT tracks_view.* FROM track_relations JOIN ${sql} ON
//                 track_relations.related_track_id = tracks_view.id WHERE track_relations.track_id = ${id}`
//         $QUERY(sql, k)
//     }

//     self.get_playlist_tracks = function (id, k) {
//         let sql = `SELECT track_id as id, position FROM playlist_tracks WHERE playlist_id = ${id} ORDER BY position`
//         $QUERY(sql, k)
//     }

//     self.get_playback_history = function(id, k) {
//         sql = `SELECT sessions.event_name, session_tracks.start_time,
//         session_tracks.end_time, session_tracks.position from session_tracks JOIN sessions
//         ON sessions.id=session_tracks.session_id WHERE track_id=${id} ORDER BY start_time DESC`
//         $QUERY(sql, k)
//     }

//     self.get_session_tracks = function (id, k) {
//         let sql = `SELECT track_id as id, position FROM session_tracks WHERE session_id = ${id} ORDER BY position`
//         $QUERY(sql, k)
//     }

//     self.get_never_played_tracks = function(k) {
//         let sql = `SELECT id FROM tracks WHERE id NOT IN (SELECT DISTINCT track_id as id FROM session_tracks)`
//         $QUERY(sql, k)
//     }

//     self.get_played_tracks = function(k) {
//         let sql = `SELECT DISTINCT track_id as id FROM session_tracks`
//         $QUERY(sql, k)
//     }

//     self.get_shortlisted_tracks = function (k) {
//         let sql = `SELECT track_id as id FROM short_listed_tracks`
//         $QUERY(sql, k)
//     }

//     self.get_unavailable_tracks = function (k) {
//         let sql = `SELECT track_id as id FROM unavailable_tracks`
//         $QUERY(sql, k)
//     }

//     self.get_session_info = function (id, k) {
//         $QUERY(`SELECT id, event_name as name, date(start_date) as date, counts.count as count FROM sessions
//         JOIN (select session_id, count(track_id) as count FROM session_tracks GROUP BY session_id) counts
//         ON sessions.id=counts.session_id WHERE sessions.id=${id}`,
//         (list) => {
//             return k(list[0])
//         })
//     }

//     self.get_sessions_list = function (k) {
//         $QUERY(`SELECT id, event_name as name, date(start_date) as date, counts.count as count FROM sessions
//         JOIN (select session_id, count(track_id) as count FROM session_tracks GROUP BY session_id) counts
//         ON sessions.id=counts.session_id ORDER BY date ASC`, k)
//     }

//     self.get_group_info = function (id, k) {
//         $QUERY(`SELECT playlists.id as id , playlists.name, IFNULL(counts.count, 0) as count FROM
//         playlists LEFT JOIN (SELECT playlist_id, count(track_id) as count FROM playlist_tracks GROUP BY playlist_id) counts
//         ON playlists.id=counts.playlist_id WHERE playlists.id=${id}`,
//         (list) => {
//             return k(list[0])
//         })
//     }

//     self.get_group_list = function (k) {
//         $QUERY(`SELECT playlists.id as id , playlists.name, IFNULL(counts.count, 0) as count FROM
//         playlists LEFT JOIN (SELECT playlist_id, count(track_id) as count FROM playlist_tracks GROUP BY playlist_id) counts
//         ON playlists.id=counts.playlist_id ORDER BY name`, k)
//     }

//     self.get_queue_elements = function (k) {
//         var tracks_sql = `(${self.base_track_view_sql()}) tracks_view`
//         var sql = `SELECT session_queue.position AS position, \`tracks_view\`.*
//                     FROM session_queue
//                     JOIN ${tracks_sql}
//                     ON tracks_view.id = session_queue.track_id
//                     WHERE session_queue.status='pending'
//                     ORDER BY session_queue.position`
//         $QUERY(sql, k)
//     }

//     self.get_queue_elements_ids = function (k) {
//         var sql = `SELECT track_id as id FROM current_queue ORDER BY position`
//         $QUERY(sql, k)
//     }

//     self.get_current_session_elements = function (k) {
//         var sql = `SELECT track_id, start_time, end_time, position, status FROM current_played_tracks ORDER BY start_time`
//         $QUERY(sql, k)
//     }

//     self.get_suggested_tracks = function (k) {
//         let sql = `SELECT DISTINCT related_track_id as id
//                         FROM track_relations
//                         WHERE track_relations.track_id IN
//                             (SELECT track_id FROM session_queue WHERE status='pending')`
//         $QUERY(sql, k)
//     }

//     self.get_settings = function (k) {
//        $QUERY("SELECT db_image_cache as image_root, db_music_cache as music_root, db_waveform_cache as waveform_root FROM settings",
//             (settings) => {
//                 let S=settings[0]
//                 $QUERY("SELECT max(id) + 1 AS first_available_id FROM tracks",
//                     (id_result) => {
//                         if (id_result[0].first_available_id != null) {
//                             S.next_id = id_result[0].first_available_id;
//                         } else {
//                             S.next_id = 1;
//                         }
//                         return k(S)
//                     }
//                 )
//             }
//         )
//     }

//     self.add_track = function (track_info, k) {
//         sql = `INSERT INTO tracks (
//         id, title, artist, album, year, genre, bpm, rating, favorite, comments, waveform, cover_medium,
//         cover_small, cover_large, cover_original, track_length, stream_start, stream_end, stream_length,
//         date_added, date_modified, bitrate, samplerate, file_name, file_size, hash, category, description,
//         disabled, original_file_name, grouping, color)
//         VALUES (${track_info.id},${track_info.title}, ${track_info.artist}, ${track_info.album}, ${track_info.year},
//         ${track_info.genre}, ${track_info.bpm}, ${track_info.rating}, ${track_info.favorite}, ${track_info.comments},
//         ${track_info.waveform}, ${track_info.cover_medium}, ${track_info.cover_small}, ${track_info.cover_large},
//         ${track_info.cover_original}, ${track_info.track_length}, ${track_info.stream_start}, ${track_info.stream_end},
//         ${track_info.stream_length}, ${track_info.date_added}, ${track_info.date_modified}, ${track_info.bitrate},
//         ${track_info.samplerate}, ${track_info.file_name}, ${track_info.file_size}, ${track_info.hash}, ${track_info.category},
//         ${track_info.description}, ${track_info.disabled}, ${track_info.original_file_name}, ${track_info.grouping},  ${track_info.color})`
//         $QUERY(sql, k)
//     }

//     self.update_track_data = function (id, track_info, k) {
//         let sql = "UPDATE tracks SET "
//         let fields = Object.keys(track_info);
//         sql += fields.indexOf("title")          != -1 ? `title=${STRING(addslashes(track_info.title))},\n` : ''
//         sql += fields.indexOf("artist")         != -1 ? `artist=${STRING(addslashes(track_info.artist))},\n` : ''
//         sql += fields.indexOf("album")          != -1 ? `album=${STRING(addslashes(track_info.album))},\n` : '';
//         sql += fields.indexOf("year")           != -1 ? `year=${(track_info.year != null) ? track_info.year : 'NULL'},\n` : ''
//         sql += fields.indexOf("genre")          != -1 ? `genre=${STRING(addslashes(track_info.genre))},\n` : ''
//         sql += fields.indexOf("bpm")            != -1 ? `bpm=${track_info.bpm != null ? track_info.bpm : 'NULL'},\n` : ''
//         sql += fields.indexOf("rating")         != -1 ? `rating=${track_info.rating},\n` : ''
//         sql += fields.indexOf("favorite")       != -1 ? `favorite=${track_info.favorite},\n` : ''
//         sql += fields.indexOf("color")          != -1 ? `color=${STRING(track_info.color)},\n` : ''
//         sql += fields.indexOf("comments")       != -1 ? `comments=${STRING(addslashes(track_info.comments))},\n` : ''
//         sql += fields.indexOf("cover_medium")   != -1 ? `cover_medium=${STRING(none_to_null(addslashes(track_info.cover_medium)))},\n` : ''
//         sql += fields.indexOf("cover_small")    != -1 ? `cover_small=${STRING(none_to_null(addslashes(track_info.cover_small)))},\n` : ''
//         sql += fields.indexOf("cover_large")    != -1 ? `cover_large=${STRING(none_to_null(addslashes(track_info.cover_large)))},\n` : ''
//         sql += fields.indexOf("cover_original") != -1 ? `cover_original=${STRING(none_to_null(addslashes(track_info.cover_original)))},\n` : ''
//         sql += fields.indexOf("stream_start")   != -1 ? `stream_start=${track_info.stream_start},\n` : ''
//         sql += fields.indexOf("stream_end")     != -1 ? `stream_end=${track_info.stream_end},\n` : ''
//         sql += fields.indexOf("stream_length")  != -1 ? `stream_length=${track_info.stream_length},\n` : ''
//         sql += fields.indexOf("disabled")       != -1 ? `disabled=${track_info.disabled},\n` : ''
//         sql += fields.indexOf("grouping")       != -1 ? `grouping=${STRING(addslashes(track_info.grouping))}\n` : ''
//         sql += `date_modified=${DATE(new Date())}\n`
//         sql += `WHERE id=${id}`

//         console.log(sql)
//         $QUERY(sql, k)
//     }

//     self.get_queue_boundary_positions = function (cont){
//         sql = "SELECT min(position) as min, max(position) as max FROM session_queue WHERE status='pending'"
//         $QUERY(sql, function(result){
//             return cont(result[0].min, result[0].max)
//         })
//     }


//     self.add_id_to_short_list = function (id, k) {
//         sql = `SELECT 1 FROM short_listed_tracks WHERE track_id=${id} LIMIT 1`;
//         $QUERY(sql,
//             function (result){
//                 if (result.length == 0){
//                     insert_sql = `INSERT INTO short_listed_tracks (track_id) VALUES (${id})`;
//                     $QUERY(insert_sql, k)
//                 } else {
//                     webix.message({
//                         text:"Track is already in the short list",
//                         type:"info",
//                         expire: 3000,
//                         id:"message1"
//                     });
//                 }
//             }
//         )
//     },

//     self.add_id_to_unavailable = function (id, k) {
//         $QUERY(
//             `SELECT 1 FROM unavailable_tracks WHERE track_id=${id} LIMIT 1`,
//             function (result) {
//                 if (result.length == 0) {
//                     $QUERY(`INSERT INTO unavailable_tracks (track_id) VALUES (${id})`, k)
//                 }
//             }
//         )
//     },

//     self.remove_id_from_unavailable = function (id, k) {
//         $QUERY(`SELECT 1 FROM unavailable_tracks WHERE track_id=${id} LIMIT 1`,
//             function (result) {
//                 if (result.length > 0) {
//                     $QUERY(`DELETE FROM unavailable_tracks WHERE track_id=${id}`, k)
//                 }
//             }
//         )
//     }

//     self.get_waiting_time = function (k) {
//         $QUERY(`SELECT wait_time FROM settings`,
//             (r) => {
//                 k(r[0].wait_time)
//             }
//         )
//     }

//     self.add_id_to_playlist = function(track_id, playlist_id, k) {
//         $QUERY(`SELECT COUNT(*) as N FROM playlist_tracks WHERE track_id=${track_id} AND playlist_id=${playlist_id}`,
//             (count) => {
//                 if (count[0].N == 0) {
//                     $QUERY(`INSERT INTO playlist_tracks (playlist_id, track_id) VALUES (${playlist_id}, ${track_id})`, k)
//                 }
//             }
//         )
//     }

//     self.add_to_current_session = function (track_data, k) {
//         k()
//     }

//     self.create_playlist = function (name, done) {
//         $QUERY(`SELECT id FROM playlists WHERE name='${addslashes(name)}'`, (x) => {
//             if (x.length == 0) {
//                 current_time = DATE(new Date());
//                 $QUERY(`INSERT INTO playlists (name, created) VALUES ('${addslashes(name)}', ${current_time})`, (x) => {
//                     done(x)
//                 })
//             } else {
//                 done()
//             }
//         })
//     }

//     self.rename_playlist = function (id, name, done) {
//         $QUERY(`SELECT id FROM playlists WHERE name='${addslashes(name)}'`, (x) => {
//             if (x.length == 0) {
//                 current_time = DATE(new Date());
//                 $QUERY(`UPDATE playlists SET name='${addslashes(name)}' WHERE id=${id}`, done)
//             } else {
//                 done()
//             }
//         })
//     }

//     self.check_playlist_name_availability = function (name, done) {
//         $QUERY(`SELECT id FROM playlists WHERE name='${addslashes(name)}'`, (x) => {
//             done(x.length == 0)
//         })
//     }

//     self.get_playlist_by_id = function (id, done) {
//         $QUERY(`SELECT * FROM playlists WHERE id=${id}`, (x) => {
//             done(x[0])
//         })
//     }


//     self.duplicate_playlist = function (id, done) {
//         $QUERY(`SELECT name FROM playlists`, (name_list) => {
//             $QUERY(`SELECT name FROM playlists WHERE id=${id}`, (n) => {
//                 let name = n[0].name
//                 let l = name_list.map((x) => {x.name})
//                 let i = 1
//                 let new_name = name + `.${i}`

//                 while (l.indexOf(new_name) != -1) {
//                      i += 1
//                      new_name = name + `.${i}`
//                 }
//                 this.create_playlist(new_name, (x) => {
//                     if (x != undefined) {
//                         let new_id = x.insertId
//                         $QUERY(
//                             `SELECT track_id FROM playlist_tracks WHERE playlist_id=${id}`,
//                             function (list) {
//                                 playlist_data = []
//                                 if (list.length > 0) {
//                                     for (i=0; i<list.length; i++) {
//                                         playlist_data.push(`(${new_id}, ${list[i].track_id})`)
//                                     }
//                                     $QUERY(`INSERT INTO playlist_tracks (playlist_id, track_id) VALUES ${playlist_data.join(',')}`,
//                                             (x) => {
//                                                 done()
//                                             }
//                                         )
//                                 }
//                             }
//                         )
//                     }
//                 })
//             })
//         })
//     }

//     self.delete_playlist = function (playlist_id, done) {
//         $QUERY(`DELETE FROM playlists WHERE id=${playlist_id}`, function (r) {
//                 $QUERY(`DELETE FROM playlist_tracks WHERE playlist_id=${playlist_id}`, function (r) {
//                         done()
//                     }
//                 )
//             }
//         )
//     }

//     self.set_playlist_tracks = function(id, list, k) {
//         playlist_data = []
//         if (list.length > 0) {
//             for (i=0; i<list.length; i++) {
//                 playlist_data.push(`(${id}, ${list[i]})`)
//             }
//             delete_sql = `DELETE FROM playlist_tracks WHERE playlist_id=${id}`
//             replace_sql = `INSERT INTO playlist_tracks (playlist_id, track_id) VALUES ${playlist_data.join(',')}`
//             $QUERY(`DELETE FROM playlist_tracks WHERE playlist_id=${id}`,
//                 () => {
//                     $QUERY(`INSERT INTO playlist_tracks (playlist_id, track_id) VALUES ${playlist_data.join(',')}`,
//                         () => {k();})
//                 }
//             )
//         }

//     }


// }


// X = new DataProvider()

// async function mongo_insert(collection, record) {
//     let client = await MongoClient.connect(connectionString, { useNewUrlParser: true });
//     let db = client.db('pymusic');
//     try {
//         const res = await db.collection(collection).insert(record);
//         return res.insertedIds["0"]
//      } catch {
//         console.log(record)
//      } finally {
//          client.close();
//      }
// }



// var track_list = {}

// X.get_all_tracks((ll) => {
//     let i = 0
//     ll.forEach((tr) => {
//         track_list[tr.id] = trackBSON(tr)
//     })
//     X.get_sessions_list((sessions) => {
//         sessions.forEach((x) => {


//             let session_data = {
//                 id: x.id,
//                 date: x.date,
//                 name: x.name,
//                 tracks: []
//             }
//             DB.get_session_tracks(x.id, (tracks) => {
//                 tracks.forEach((tr) => {
//                     console.log(tr)
//                 })
//             })

//             console.log(session_data)
//         })
//     })
// })
