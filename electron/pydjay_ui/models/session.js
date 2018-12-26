class SessionModel extends BaseListModel {
    constructor(session, tracks_model) {
        super()
        this.tracks_model = tracks_model

        this.tracks_model.on('metadata-changed', (x) => {
            this.dispatch("metadata-changed", x)
        })

        DB.get_session_tracks(session.id, 
            (tracks) => { 
                this.track_list = {}
                this.tracks_order = []
                tracks.forEach((t) => {
                    this.tracks_order.push(t.id)
                    this.track_list[t.id] = this.tracks_model.get_track_by_id(t.id)
                })
                for(let i=0; i<this.ready_wait_queue.length; i++) {
                    this.ready_wait_queue[i]()
                }                                                            
            }
        )            
    }

    get_all_tracks() {
        Q = []
        this.tracks_order.forEach((x) => {Q.push(this.track_list[x])})
        return Q
    }

    get_track_by_id(id) {
        return this.track_list[id]
    }

    set_metadata(track, metadata) {
        this.tracks_model.set_metadata(track, metadata)
        // X = this.track_list[track.id]
        // metadata_keys = Object.keys(metadata)
        // Object.keys(metadata).forEach((x) => {
        //     X[x] = metadata[x]
        // })
        // DB.update_track_data(id, metadata, () => {
        //     this.dispatch("metadata-changed", this.track_list[id])
        // })
    }
}