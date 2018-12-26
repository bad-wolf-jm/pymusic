class CurrentSessionModel extends BaseListModel {
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
        DB.get_current_session_elements( (tracks) => { 
            this.tracks_order = []
            tracks.forEach((t) => {
                this.tracks_order.push(t)
            })
            k()
            this.dispatch("content-changed", this.queue)
        })            
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
        this.tracks_order.forEach((x) => {Q.push(this.tracks_model.get_track_by_id(x.track_id))})
        return Q
    }

    check_membership(element) {
        if (this.tracks_order != undefined) {
            for (let i=0; i < this.tracks_order.length; i++) {
                if (element.id == this.tracks_order[i].track_id) {
                    return true
                }
            }
        }
        return false
    }

    add(element) {
        this.tracks_order.push(element)
        this.save()
        this.dispatch("content-changed", this.get_all_tracks())
    }

    get_track_by_id(id) {
        return this.tracks_model.get_track_by_id(id)
    }

    save() {
        $QUERY("TRUNCATE current_played_tracks", () => {
            let queue_tuples = []
            for (let i=0; i < this.tracks_order.length; i++) {
                T = this.tracks_order[i]
                queue_tuples.push(`(${T.track_id}, ${DATE(T.start_time)}, ${DATE(T.end_time)}, ${i+1}, '${T.status}')`)
            }
            $QUERY(`INSERT INTO current_played_tracks (track_id, start_time, end_time, position, status) VALUES ${queue_tuples.join(",")}`, () => {})
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
                let x = this.tracks_model.get_track_by_id(i.track_id)
                d += x.stream_length
            })
            return d
        }
        return undefined
    }


    set_metadata(track, metadata) {
        this.tracks_model.set_metadata(track, metadata)
        // X = this.track_list[track.id]
        // metadata_keys = Object.keys(metadata)
        // Object.keys(metadata).forEach((x) => {X[x] = metadata[x]})
        // DB.update_track_data(id, metadata, () => {
        //     this.dispatch("metadata-changed", this.track_list[id])
        // })
    }

    store_session(name, location, address, k) {
        $QUERY(`SELECT max(id) + 1 AS new_session_id FROM sessions`, (result) => {
            let new_session_id = result[0].new_session_id
            $QUERY(`SELECT min(start_time) AS start, max(end_time) AS end FROM current_played_tracks`, (time_bounds) => {
                let start_date = DATE(time_bounds[0].start);
                let end_date = DATE(time_bounds[0].end);
                $QUERY(`INSERT INTO sessions (id, event_name, start_date, end_date, location, address) 
                        VALUES (${new_session_id}, "${name}", ${start_date}, ${end_date}, "${location}", "${address}")`, () => {
                    let relation_data = []
                    let queue_tuples = []
                    for(var i =0; i<this.tracks_order.length; i++){
                        T = this.tracks_order[i]
                        if (i+1 < this.tracks_order.length) {
                            let relation_time = DATE(this.tracks_order[i+1].start_time);
                            relation_data.push(`(${this.tracks_order[i].track_id}, ${this.tracks_order[i+1].track_id}, 'PLAYED_IN_SET', 1, ${relation_time})`)
                            queue_tuples.push(`(${new_session_id}, ${T.track_id}, ${DATE(T.start_time)}, ${DATE(T.end_time)}, ${i+1}, '${T.status}')`)
                        }
                    }
                    $QUERY(`INSERT INTO track_relations (track_id, related_track_id, reason, count, date) 
                            VALUES ${relation_data.join(',')} ON DUPLICATE KEY UPDATE count=count+1`, () => {
                        $QUERY(`INSERT INTO session_tracks (session_id, track_id, start_time, end_time, position, status) VALUES ${queue_tuples.join(",")}`, () => {
                            $QUERY(`TRUNCATE current_played_tracks`, () => {
                                this.refresh(() => {
                                    this.dispatch('content-changed', this.get_all_tracks())
                                    k()
                                })
                            })
                        })
                    })
                })
            })
        })
    }
}