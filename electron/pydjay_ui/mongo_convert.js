var mysql = require('mysql');
var path = require('path');
const Datastore = require("nedb-async-await").Datastore;
const { EventDispatcher } = require("event_dispatcher")
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


class MusicDatabase extends EventDispatcher {
    constructor(name) {
        super()
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

    async getTrackById(id) {
        return (await this.getTracksByIds([id]))[0]
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

    async setTrackData(track, new_data) {
        let [num, modified] = await this.tracks.update(
            {"_id": track._id}, 
            {$set: new_data}, 
            {returnUpdatedDocs: true})
        if (num > 0) {
            this.dispatch("track-metadata-changed". modified)
        }
        return modified
    }

    insertTrack(track) {
        return this.tracks.insert(track)    
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

    // (await db.getAllSessions()).forEach(async (pl) => {
    //     console.log(pl.object.event, await pl.duration())
    // })

    // let x = (await db.getTracksByIds(["09lWty9X6kR6v6T8"]))[0]
    // console.log(x)
    // db.setTrackData(x, {"title": "Take Me To Church"})
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
                    track_id: r.related_track_id,
                    reason: r.reason,
                    count: r.count,
                    date: r.date
                }
            })
            track.relations = t_relations

            let history = await connection.query(`SELECT * FROM session_tracks WHERE track_id=${tr.id} ORDER BY position`);
            history = history.map((x) => {return {
                session: x.session_id,
                time: x.start_time,
                status: x.status
            }})
            track.history = history
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
