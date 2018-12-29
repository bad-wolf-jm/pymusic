class ShortlistModel extends BaseListModel {
    constructor(tracks_model) {
        super()
        this.tracks_model = tracks_model

        this.tracks_model.on('metadata-changed', (x) => {
            this.dispatch("metadata-changed", x)
        })

        this.refresh(() => {
            for(let i=0; i<this.ready_wait_queue.length; i++) {
                this.ready_wait_queue[i]()
            }
        })
    }

    refresh(k) {
        DB.get_shortlisted_tracks( (tracks) => {
            this.tracks_order = []
            tracks.forEach((t) => {
                this.tracks_order.push(t.id)
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
        let Q = []
        this.tracks_order.forEach((x) => {
            Q.push(this.tracks_model.get_track_by_id(x))})
        Q.sort(this.compare_tracks)
        return Q
    }

    get_track_by_id(id) {
        return this.tracks_model.get_track_by_id(id)
    }

    add(element) {
        this.tracks_order.push(element.id)
        this.save()
        this.dispatch("content-changed", this.get_all_tracks())
    }

    remove(element) {
        if (this.tracks_order != undefined) {
            let I = this.tracks_order.indexOf(element.id)
            if (I != -1) {
                this.tracks_order.splice(I, 1)
                this.save()
                this.dispatch("content-changed", this.get_all_tracks())
            }
        }
    }


    save() {
        $QUERY("TRUNCATE short_listed_tracks", () => {
            let queue_tuples = []
            for (let i=0; i < this.tracks_order.length; i++) {
                T = this.tracks_order[i]
                queue_tuples.push(`(${T})`)
            }
            $QUERY(`INSERT INTO short_listed_tracks (track_id) VALUES ${queue_tuples.join(",")}`, () => {})
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
                let x = this.tracks_model.get_track_by_id(i)
                d += x.stream_length
            })
            return d
        }
        return undefined
    }

    set_metadata(track, metadata) {
        this.tracks_model.set_metadata(track, metadata)
    }
}
