class UnavailableModel extends BaseListModel {
    constructor(tracks_model) {
        super()
        this.tracks_model = tracks_model
        this.refresh(() => {
            for(let i=0; i<this.ready_wait_queue.length; i++) {
                this.ready_wait_queue[i]()
            }                                                            
        })
    }

    refresh(k) {
        DB.get_unavailable_tracks( (tracks) => { 
            this.tracks_order = []
            tracks.forEach((t) => {
                this.tracks_order.push(t)
            })
            k()
            this.dispatch("content-changed", this.queue)
        })            
    }


    compare_tracks(a, b) {
        let x = a.title.toLowerCase();
        let y = b.title.toLowerCase();
        if (x < y) {return -1;}
        if (x > y) {return 1;}
        return 0;        
    }

    ready(func) {
        if (this.tracks_order != undefined) {
            func(this.get_all_tracks())
        } else {
            this.ready_wait_queue.push(func)
        }
    }

    get_all_tracks() {
        Q = []
        this.tracks_order.forEach((x) => {
            Q.push(this.tracks_model.get_track_by_id(x.id))})
        Q.sort(this.compare_tracks)
        return Q
    }

    get_track_by_id(id) {
        return this.tracks_model.get_track_by_id(id)
    }

    add(element) {
        this.tracks_order.push(element)
        this.save()
        this.dispatch("content-changed", this.get_all_tracks())
    }

    save() {
        $QUERY("TRUNCATE unavailable_tracks", () => {
            let queue_tuples = []
            for (let i=0; i < this.tracks_order.length; i++) {
                T = this.tracks_order[i]
                queue_tuples.push(`(${T.id})`)
            }
            $QUERY(`INSERT INTO unavailable_tracks (track_id) VALUES ${queue_tuples.join(",")}`, () => {})
        })
    }

    length() {
        if (this.tracks_order != undefined) {
            return this.tracks_order.length
        }
        return undefined
    }

    duration() {
        if (this.tracks_order != undefined) {
            let d = 0
            this.tracks_order.forEach((i) => {
                let x = this.tracks_model.get_track_by_id(i.id)
                d += x.stream_length
            })
            return d
        }
        return undefined
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