var jsmediatags = require("jsmediatags");
var fs = require('fs-extra');
var path = require('path');
const {spawn} = require ('child_process');
var Jimp = require("jimp");
const { TrackImportProgressDialog } = require("iface/dialogs/track_add_progress")
const { mp3Duration } = require("fileinfo/mp3_fileinfo")

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

}