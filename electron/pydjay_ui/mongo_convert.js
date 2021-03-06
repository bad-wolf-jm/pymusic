var mysql = require('mysql');
var path = require('path');
const Datastore = require("nedb-async-await").Datastore;
const { EventDispatcher } = require("event_dispatcher")
const { MusicDatabase } = require("musicdb/model.js") 
var fs = require('fs-extra');
const { existsSync } = require("fs")
const { homedir } = require("os")

// const path = require("path")

const { mp3Duration } = require("fileinfo/mp3_fileinfo")
// const { CollectionController } = require("musicdb/collection.js")
// // const { TrackListController } = require("musicdb/track_list.js")
// // const { TrackSetController } = require("musicdb/track_set.js")
// const { QueueController } = require("musicdb/queue.js")
// const { SessionController } = require("musicdb/session.js")
// const { PlaylistController } = require("musicdb/playlist.js")

// const MongoClient = require('mongodb').MongoClient;


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

function getFileExtension(f_name) {
    return f_name.slice((Math.max(0, f_name.lastIndexOf(".")) || Infinity) + 1);
}



const db = new MusicDatabase("pymusic")

main = async (db) => {
    let mysql = require('async-mysql'),
        connection,
        track_objects = {},
        back_track_objects = {},
        rows;


    try {

        // await db.state.d.insert({_id: "queue", elements:{}, ordering:[null]})
        // await db.state.d.insert({_id: "session", elements:{}, ordering:[]})
        // await db.state.d.insert({_id: "shortlist", elements:{}})
        // await db.state.d.insert({_id: "unavailable", elements:{}})
        // await db.state.d.insert({_id: "settings", elements:{

        //}})

        connection = await mysql.connect({host: 'localhost', user:"root", password:"root", database:'pymusic'});
        settings = await connection.query('SELECT * FROM settings');
        settings = settings[0]
        rows = await connection.query('SELECT * FROM tracks');

        for (let i=0; i < rows.length; i++) {
            let tr = rows[i]
            tr.image_root = settings.db_image_cache
            tr.music_root = settings.db_music_cache

            let track_file = path.join(tr.music_root, tr.file_name)
            console.log(`Adding track ${i+1} of ${rows.length} - ${tr.title} // ${tr.artist}`)

            new_id = await db.addFile(track_file)
            track_objects[tr.id] = new_id["_id"]
            back_track_objects[new_id["_id"]] = tr.id

            let last_played = await connection.query(`SELECT max(start_time) as last_played, count(*) as count FROM session_tracks WHERE track_id=${tr.id} ORDER BY position`);

            db.tracks.d.update({_id:new_id._id}, {$set: {
                "stats.last_played": last_played[0].last_played,
                "stats.play_count": last_played[0].count,
                "stats.rating": tr.rating,
                "stats.loved": tr.favorite && true,
                "track.bpm": tr.bpm, 
                "track.stream_start": tr.stream_start / 1000000, 
                "track.stream_end": tr.stream_end / 1000000,
                "metadata.color": tr.color, 
                "metadata.title": tr.title,
                "metadata.artist": tr.artist,
                "metadata.album": tr.album,
                "metadata.genre": tr.genre,
                "metadata.year": tr.year,
                "createdAt": tr.date_added,
                "updatedAt": tr.date_modified,
            }})

            if (tr.cover_original != null) {
                await fs.copy(path.join(tr.image_root, tr.cover_original), path.join(db.getCoverFolder(), `${new_id._id}_original.${getFileExtension(tr.cover_original)}`))
                await fs.copy(path.join(tr.image_root, tr.cover_large), path.join(db.getCoverFolder(), `${new_id._id}_large.${getFileExtension(tr.cover_large)}`))
                await fs.copy(path.join(tr.image_root, tr.cover_medium), path.join(db.getCoverFolder(), `${new_id._id}_medium.${getFileExtension(tr.cover_medium)}`))
                await fs.copy(path.join(tr.image_root, tr.cover_small), path.join(db.getCoverFolder(), `${new_id._id}_small.${getFileExtension(tr.cover_small)}`))

                db.tracks.d.update({_id: new_id._id}, {$set: {
                    "metadata.cover.original": `${new_id._id}_original.${getFileExtension(tr.cover_original)}`,
                    "metadata.cover.small": `${new_id._id}_large.${getFileExtension(tr.cover_large)}`,
                    "metadata.cover.medium":  `${new_id._id}_medium.${getFileExtension(tr.cover_medium)}`,
                    "metadata.cover.large":  `${new_id._id}_small.${getFileExtension(tr.cover_small)}`,
                }})
            }

        }

        let tracks = await db.tracks.d.find({})
        tracks.forEach(async (t) => {
            let relations = await connection.query(`SELECT * FROM track_relations WHERE track_id=${back_track_objects[t._id]}`);
            let t_relations = {}
            relations.forEach((r) => {
                t_relations[track_objects[r.related_track_id]] = r.count
            })
            await db.tracks.d.update({_id: t._id}, {$set: {"stats.relations": t_relations}})
        })

        let sessions = await connection.query('SELECT * FROM sessions');
        sessions.forEach(async (s) => {
            let session_data = {
                    event: s.event_name,
                    location: s.location,
                    address: s.address,
                    createdAt: s.start_date,
                    updatedAt: s.start_date,
                    date_start: s.start_date,
                    date_end: s.end_date
                }
            let session_tracks = await connection.query(`SELECT * FROM session_tracks WHERE session_id=${s.id} ORDER BY position`);
            session_data.elements = {}
            session_data.ordering = []
            session_tracks.forEach((t) => {
                session_data.ordering.push(track_objects[t.track_id])
                session_data.elements[track_objects[t.track_id]]  = {
                    status: t.status,
                    time_start: t.start_time,
                    time_end: t.end_time
                }
                
            })
            await db.sessions.d.insert(session_data)
        })

        let playlists = await connection.query('SELECT * FROM playlists');
        playlists.forEach(async (s) => {
            let playlist_data = {
                    name: s.name,
                    description: s.description,
                    createdAt: s.created
                }
            let playlist_tracks = await connection.query(`SELECT * FROM playlist_tracks WHERE playlist_id=${s.id}`);
            playlist_data.elements = {}
            playlist_tracks.forEach((t) => {
                playlist_data.elements[track_objects[t.track_id]] = true
            })
            await db.playlists.d.insert(playlist_data)
        })
        console.log("done")

    } catch (e) {
        console.log(e)
    }
};

//main().then(console.log);
if (!(existsSync(path.join(homedir(), ".pymusic-library", "pymusic")))) {
    //let library = new MusicDatabase("pymusic")
    db.initialize().then(() => {main(db)})
    //library = undefined
  } else {
      main(db)
  }



// class Track extends EventDispatcher {
//     constructor(db, object) {
//         super()
//         this.db = db
//         this.object = object
//     }

//     getHistory() {

//     }

//     getRelatedTracks() {

//     }

//     setMetadata(metadata) {
//         this.object = this.db.setTrackData(this.object, metadata)
//         return this.object
//     }

//     getMetadata() {
//         return this.object
//     }
// }


// class Playlist {
//     constructor(db, object) {
//         this.db = db
//         this.object = object
//     }

//     getTracks() {
//         return this.db.getTracksByIds(Object.keys(this.object.tracks)) 
//     }

//     duration() {
//         return this.db.duration(Object.keys(this.object.tracks)) 
//     }
// }

// class Session {
//     constructor(db, object) {
//         this.db = db
//         this.object = object
//     }

//     async getTracks() {
//         let track_ids = this.object.tracks.map((t) => {return t.track_id})
//         let tracks = await this.db.getTracksByIds(track_ids)
//         let x = {}
//         tracks.forEach((t) => {x[t._id] = t})
//         return this.object.tracks.map((t) => {return x[t.track_id]})
//     }

//     duration() {
//         let track_ids = this.object.tracks.map((t) => {return t.track_id})
//         return this.db.duration(track_ids) 
//     }
// }

// class Queue {
//     constructor(db, q) {
//         this.db = db
//         this.q = q.tracks
//     }

//     _save() {

//     }

//     pop() {
//         return this.db.popFromQueue()
//     }

//     append(element) {
//         this.db.appendToQueue(element)
//     }

//     reorder(new_order) {
//         // if (new_order.length == this.ordering.length) {
//         //     if (new_order.every((x) => {return (this.objects[x] != undefined)})) {
//         //         this.ordering = new_order
//         //         this.db.dispatch("reorder", this.get_all_objects())
//         //     }
//         // }
//         this.db.setQueueElements(new_order)
//     }

//     async getTracks() {
//         let tracks = await this.db.getTracksByIds(this.q)
//         let x = {}
//         tracks.forEach((t) => {x[t._id] = t})
//         return this.q.tracks.map((t) => {return x[t]})
//     }

//     length() {
//         let i = this.q.indexOf(null)
//         return (i == -1) ? this.q.length : i 
//     }

//     duration() {
//         return this.db.duration(this.q.slice(0, this.length())) 
//     }
// }


// class CurrentSession {
//     constructor(db, q) {
//         this.db = db
//         this.q = q.tracks
//     }


//     _save() {

//     }

//     discard() {

//     }

//     save(name, location, address) {
//         // save session
//         // updatae track histories
//         // update last played
//         // update track relations
//     }

//     store_as_playlist(name) {

//     }

//     add(element) {
//         // this.db.appendToQueue(element)
//     }

//     reorder(new_order) {
//         this.db.reorderQueue(new_order)
//     }

//     async getTracks() {
//         let tracks = await this.db.getTracksByIds(this.q)
//         let x = {}
//         tracks.forEach((t) => {x[t._id] = t})
//         return this.q.tracks.map((t) => {return x[t]})
//     }

//     length() {
//         let i = this.q.indexOf(null)
//         return (i == -1) ? this.q.length : i 
//     }

//     duration() {
//         return this.db.duration(this.q.slice(0, this.length())) 
//     }
// }


// class MusicDatabaseSSS extends EventDispatcher {
//     constructor(name) {
//         super()
//         this.tracks = new CollectionController(path.join(".ds", name, "tracks.json"))
//         this.sessions = new CollectionController(path.join(".ds", name, "sessions.json"))
//         this.playlists = new CollectionController(path.join(".ds", name, "playlists.json"))
//         this.state = new CollectionController(path.join(".ds", name, "state.json"))
//         this.queue = new QueueController(this, this.state, "queue")
//         this.current_session = new SessionController(this, this.state, "session")
//         this.shortlisted_tracks = new PlaylistController(this, this.state, "shortlist")
//         this.unavailable_tracks = new PlaylistController(this, this.state, "unavailable")
        
//         // Datastore({
//         //     filename: path.join(".ds", name, "tracks.json"),
//         //     autoload: true,
//         //     timestampData: true})

//         // Datastore({
//             //     filename: path.join(".ds", name, "sessions.json"),
//             //     autoload: true, 
//             //     timestampData: true})
            
//         // Datastore({
//         //     filename: path.join(".ds", name, "playlists.json"),
//         //     autoload: true,
//         //     timestampData: true})

//         // Datastore({
//         //     filename: path.join(".ds", name, "state.json"),
//         //     autoload: true,
//         //     timestampData: true})

//     }


//     queueIsEmpty() {
//         let current_queue = this.getQueue().q
//         return (current_queue[0] == null)
//     }

//     // async popQueue() {
//     //     let current_queue = this.getQueue().q
//     //     if ((current_queue.length > 0) && (current_queue[0] != null)) {
//     //         let next_id = current_queue.shift()
//     //         await this.state.update({_id: "queue"}, {$set: {tracks: current_queue}}, {returnUpdatedDocs: true})
//     //         return this.getTrackById(next_id)
//     //     }
//     // }

//     // async addToQueue(track) {
//     //     let current_queue = this.getQueue().q
//     //     current_queue.push(track._id)
//     //     let new_queue = await this.state.update({_id: "queue"}, 
//     //         {$set: {tracks: current_queue}}, 
//     //         {returnUpdatedDocs: true})
//     //     this.dispatch("queue-changed", new_queue)
//     // }

//     // async removeFromQueue(track) {
//     //     let current_queue = this.getQueue().q
//     //     let idx = current_queue.indexOf(track._id)
//     //     if ( idx != -1 ) {
//     //         current_queue.splice(index, 1)
//     //         let new_queue = await this.state.update({_id: "queue"}, 
//     //             {$set: {tracks: current_queue}}, 
//     //             {returnUpdatedDocs: true})
//     //         this.dispatch("queue-changed", new_queue)
//     //     } 
//     // }

//     // async reorderQueue(new_order) {
//     //     let current_queue = this.getQueue().q
//     //     let current_queue_objects = {}
//     //     current_queue.forEach((x) => {current_queue_objects[x] = true})
//     //     if (new_order.length == current_queue.length) {
//     //         if (new_order.every((x) => {return (this.objects[x] != undefined)})) {
//     //             let new_queue = await this.state.update({_id: "queue"}, {$set: {tracks: new_order}}, {returnUpdatedDocs: true})
//     //             this.dispatch("queue-reordered", new_order)
//     //         }
//     //     }
//     // }

//     async createPlaylist(name, description, tracks) {
//         let new_playlist = {name: name, description: description, tracks: {}}
//         tracks.forEach((t) => {new_playlist.tracks[t._id] = true})
//         let playlist = await this.playlists.insert(new_playlist)
//         this.dispatch("playlist-created", playlist)
//     }

//     async renamePlaylist(playlist, name) {
//         let p = await this.playlists.update(
//             {_id: playlist._id}, 
//             {$set: {name: name}}, 
//             {returnUpdatedDocs: true})
//         this.dispatch("playlist-updated", p)
//     }

//     async duplicatePlaylist(playlist) {
//         this.createPlaylist(
//             playlist.name + " (duplicate)", 
//             playlist.description, 
//             playlist.tracks)

//     }

//     async deletePlaylist(playlist) {
//         await this.playlists.remove({_id: playlist._id}, {})
//         this.dispatch("playlist-deleted", playlist)
//     }

//     async setPlaylistTracks(playlist, tracks) {
//         playlist.tracks = {}
//         tracks.forEach((t) => {playlist.tracks[t._id] = true})
//         let p = await this.playlists.update(
//             {_id:playlist._id}, 
//             {$set: {tracks:playlist.tracks}}, 
//             {returnUpdatedDocs: true})
//         this.dispatch("playlist-updated", p)
//     }

//     getSettings() {
//         return this.state.find({_id: "settings"})
//     }

//     async getQueue() {
//         let q = await this.state.find({_id: "queue"})
//         return new Queue(this, q)
//     }

//     getCurrentSession() {
//         return this.state.find({_id: "current_session"})
//     }

//     getUnavailableTracks() {
//         return this.state.find({_id: "unavailable"})
//     }

//     getShortList() {
//         return this.state.find({_id: "shortlist"})
//     }

//     getAllTracks() {
//         return this.tracks.find({})
//     }

//     getTracksByIds(id_array) {
//         if (id_array != undefined) {
//             return this.tracks.find({"_id": {"$in":id_array}})
//         } else {
//             return this.tracks.find({})
//         }
//     }

//     async getTrackById(id) {
//         return (await this.getTracksByIds([id]))[0]
//     }

//     async getAllPlaylists() {
//         let sessions = await this.playlists.find({})
//         return sessions.map((s) => {return new Playlist(this, s)})
//     }

//     async getAllSessions() {
//         let sessions = await this.sessions.find({})
//         return sessions.map((s) => {return new Session(this, s)})
//     }

//     async duration(id_array) {
//         let tracks = await this.getTracksByIds(id_array)
//         let dur = 0
//         tracks.forEach((track) => {
//             dur += (track.stream_end - track.stream_start)
//         })
//         return dur
//     }

//     async setTrackData(track, new_data) {
//         let [num, modified] = await this.tracks.update(
//             {"_id": track._id}, 
//             {$set: new_data}, 
//             {returnUpdatedDocs: true})
//         if (num > 0) {
//             this.dispatch("track-metadata-changed". modified)
//         }
//         return modified
//     }

//     insertTrack(track) {
//         return this.tracks.insert(track)    
//     }
// }

