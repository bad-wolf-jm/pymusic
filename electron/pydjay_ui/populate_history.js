var mysql = require('mysql');
var path = require('path');
const Datastore = require("nedb-async-await").Datastore;
const { EventDispatcher } = require("event_dispatcher")
const { MusicDatabase } = require("musicdb/model.js") 
var fs = require('fs-extra');
const { existsSync } = require("fs")
const { homedir } = require("os")


const { mp3Duration } = require("fileinfo/mp3_fileinfo")

function getFileExtension(f_name) {
    return f_name.slice((Math.max(0, f_name.lastIndexOf(".")) || Infinity) + 1);
}



const db = new MusicDatabase("pymusic")

main = async (db) => {
    let i = 1
    let tracks =Object.values(await db.sessions.getAllObjects())
    // console.log

    for (let x=0; x < tracks.length; x++) {
        let trackObject = tracks[x]
        Object.keys(trackObject.elements).forEach(async (k) => {
            let logEntry = {
                trackId: k,
                time_start: trackObject.elements[k].time_start,
                time_end: trackObject.elements[k].time_end,
                status: trackObject.elements[k].status
            }
            console.log(logEntry)    
            await db.history.d.insert(logEntry)
        })
        // if (trackObject.metadata.color != null) {
        //     let t = await db.tags.d.find({color: trackObject.metadata.color.toLowerCase()})
        //     //console.log(t)
        //     if (t.length == 0) {
        //         // console.log(color)
        //         let color = trackObject.metadata.color.toLowerCase()
        //         let name = `Tag ${i++}`
        //         t = await db.tags.d.insert({name: name, color: color})
        //         console.log(t)
        //     } else {
        //         t = t[0]
        //     }
        //     let x = await db.tracks.setData(trackObject, {"metadata.tags": [t._id]})
        //     //console.log(await db.tracks.getObjectById(trackObject._id))
        // }
    }


    // tracks.forEach(async (trackObject) => {
    //     // console.log(trackObject.color)
    //     if (trackObject.metadata.color != null) {
            
    //         let t = await db.tags.d.find({color: trackObject.metadata.color.toLowerCase()})
    //         //console.log(t)
    //         if (t.length == 0) {
    //             // console.log(color)
    //             let color = trackObject.metadata.color.toLowerCase()
    //             let name = `Tag ${i++}`
    //             t = await db.tags.d.insert({name: name, color: color})
    //             console.log(t)
    //         } else {
    //             t = t[0]
    //         }
    //         let x = await db.tracks.setData(trackObject, {"metadata.tags": [t._id]})
    //         //console.log(await db.tracks.getObjectById(trackObject._id))
    //     }
    // })
}

main(db)