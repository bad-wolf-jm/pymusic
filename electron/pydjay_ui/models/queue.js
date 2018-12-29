class QueueModel extends BaseListModel {
    constructor(tracks_model, current_session_model) {
        super()
        this.current_session_model = current_session_model
        this.tracks_model = tracks_model
        this.tracks_order = []

        this.tracks_model.on('metadata-changed', (x) => {
            this.dispatch("metadata-changed", x)
        })

        DB.get_queue_elements_ids( (tracks) => { 
            this.tracks_order = []
            if (tracks.length == 0) {
                this.tracks_order.push(null)
                this.save()
            } else {
                tracks.forEach((t) => {
                    this.tracks_order.push(t.id)
                })
            }
            for(let i=0; i<this.ready_wait_queue.length; i++) {
                this.ready_wait_queue[i]()
            }     
        })            
    }

    get_all_tracks() {
        let Q = []
        this.tracks_order.forEach((x) => {Q.push((x != null) ? this.tracks_model.get_track_by_id(x) : null)})
        return Q
    }

    get_track_by_id(id) {
        return this.tracks_model.get_track_by_id(id) 
    }

    reorder_queue(new_order) {
        this.tracks_order = new_order
        this.save()
    }

    is_empty() {
        return (this.tracks_order == undefined) || (this.tracks_order.length == 0) || (this.tracks_order[0] == null)
    }

    pop() {
        if (this.tracks_order != undefined) {
            if (this.tracks_order.length > 0) {
                if (this.tracks_order[0] == null) {
                    return undefined
                }
                let element = this.tracks_order.shift()
                this.save() 
                this.dispatch("content-changed", this.get_all_tracks())
                return this.tracks_model.get_track_by_id(element)
            } else {
                return undefined
            }
        }
        return undefined
    }

    save() {
        $QUERY("TRUNCATE current_queue", () => {
            let queue_tuples = []
            if (this.tracks_order.length > 0) {
                for (let i=0; i < this.tracks_order.length; i++) {
                    queue_tuples.push(`(${i+1}, ${this.tracks_order[i]})`)
                }
                $QUERY(`INSERT INTO current_queue (position, track_id) VALUES ${queue_tuples.join(",")}`, () => {})    
            }
        })
    }

    _check_availability(element, do_insert) {
        //console.log(this.tracks_order.indexOf(element.id) )
        //console.log(this.current_session_model.tracks_order.indexOf(element.id) )
        if ((this.tracks_order.indexOf(element.id) == -1) && 
                !(this.current_session_model.check_membership(element))) {
            do_insert(element)
        }
    }

    insert(element, index) {
        if (this.tracks_order != undefined) {
            this._check_availability(element, (e) => {
                this.tracks_order.splice(index, 0, e.id)
                this.save()
                this.dispatch("content-changed", this.get_all_tracks())    
            })
        }
    }

    append(element) {
        if (this.tracks_order != undefined) {
            this._check_availability(element, (e) => {
                this.tracks_order.push(e.id)
                this.save()
                this.dispatch("content-changed", this.get_all_tracks())    
            })
        }
    }

    remove(index) {
        if (this.tracks_order != undefined) {
            let I = this.tracks_order.indexOf(index.id)
            if (I != -1) {
                this.tracks_order.splice(I, 1)
                this.save()
                this.dispatch("content-changed", this.get_all_tracks())
            }
        }
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

    length() {
        if (this.tracks_order != undefined) {
            let i = this.tracks_order.indexOf(null)
            return (i == -1) ? this.tracks_order.length : i 
        }
        return undefined
    }

    duration() {
        if (this.tracks_order != undefined) {
            let d = 0
            for (let i=0; i<this.tracks_order.length; i++) {
                
                if (this.tracks_order[i] == null) {
                    return d
                } else {
                    let x = this.tracks_model.get_track_by_id(this.tracks_order[i])
                    d += (x != undefined) ? x.stream_length : 0                        
                }
            }
            
            return d
        }
        return undefined
    }

}