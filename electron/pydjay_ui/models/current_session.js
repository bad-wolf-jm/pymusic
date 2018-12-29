class CurrentSessionModel extends BaseOrderedObjectSubsetModel {


    constructor(tracks_model) {
        super(tracks_model)
        this.initialize()
    }

    refresh(k) {
        DB.get_current_session_elements( (tracks) => { 
            this.objects = {}
            this.ordering = []
            tracks.forEach((t) => {
                this.ordering.push(t.track_id)
                this.objects[t.track_id] = t
            })
            super.refresh(k)
        })            
    }

    get_all_tracks() {
        return this.get_all_objects()
    }

    get_track_by_id(id) {
        return this.get_object_by_id(id)
    }

    check_membership(element) {
        if (this.is_ready()) {
            return (this.objects[element.id] != undefined)
        }
        return false
    }

    add(element) {
        if (this.is_ready())  {
            this.ordering.push(element.track_id)
            this.objects[element.track_id] = element
            this.dispatch("content-changed", this.get_all_objects())
            this.save()
        }
    }

    save() {
        $QUERY("TRUNCATE current_played_tracks", () => {
            let queue_tuples = []
            let position = 0

            this.ordering.forEach((i) => {
                position += 1;
                let session_track = this.objects[i]
                queue_tuples.push(`(${session_track.track_id}, ${DATE(session_track.start_time)}, ${DATE(session_track.end_time)}, ${position}, '${session_track.status}')`)
            })
            $QUERY(`INSERT INTO current_played_tracks (track_id, start_time, end_time, position, status) 
                    VALUES ${queue_tuples.join(",")}`, () => {})
        })
    }

    discard_session(k) {
        $QUERY(`TRUNCATE current_played_tracks`, () => {
            this.refresh(() => {
                this.dispatch('content-changed', this.get_all_tracks())
                k()
            })
        })
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