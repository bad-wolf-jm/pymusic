class PlayedTracksModel extends BaseListModel {
    constructor(tracks_model) {
        super()
        this.tracks_model = tracks_model
        DB.get_played_tracks( (tracks) => { 
            this.track_list = {}
            tracks.forEach((t) => {
                this.track_list[t.id] = this.tracks_model.get_track_by_id(t.id)
            })
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
        Q = []
        Object.keys(this.track_list).forEach((x) => {Q.push(this.track_list[x])})
        Q.sort(this.compare_tracks)
        return Q
    }

    get_track_by_id(id) {
        return this.track_list[id]
    }

    set_metadata(track, metadata) {
        X = this.track_list[track.id]
        metadata_keys = Object.keys(metadata)
        Object.keys(metadata).forEach((x) => {
            X[x] = metadata[x]
        })
        DB.update_track_data(id, metadata, () => {
            this.dispatch("metadata-changed", this.track_list[id])
        })
    }
}