class TrackListModel extends BaseListModel {
    constructor() {
        super()
        DB.get_all_tracks((tracks) => {
            this.track_list = {}
            tracks.forEach((t) => {this.track_list[t.id] = t})
            for(let i=0; i<this.ready_wait_queue.length; i++) {
                this.ready_wait_queue[i]()
            }                                                            
        })
    }

    compare_tracks(a, b) {
        let x = a.title.toLowerCase();
        let y = b.title.toLowerCase();
        if (x < y) {return -1;}
        if (x > y) {return 1;}
        return 0;        
    }

    get_all_tracks() {
        let Q = []
        Object.keys(this.track_list).forEach((x) => {Q.push(this.track_list[x])})
        Q.sort(this.compare_tracks)
        return Q
    }

    get_track_by_id(id) {
        return this.track_list[id]
    }


    update(id) {
        DB.get_track_by_id(id, (result) => {
            let track = result[0]
            this.track_list[id] = track
            this.dispatch("metadata-changed", this.track_list[id])
        })
    }

    set_metadata(track, metadata) {
        let X = this.track_list[track.id]
        let metadata_keys = Object.keys(metadata)
        Object.keys(metadata).forEach((x) => {
            X[x] = metadata[x]
        })
        DB.update_track_data(track.id, metadata, () => {
            this.update(track.id)
        })
    }
}