class QueueModel extends BaseOrderedObjectSubsetModel {
    constructor(tracks_model, current_session_model) {
        super(tracks_model)
        this.current_session_model = current_session_model
        this.initialize()  
    }

    refresh(k) {
        DB.get_queue_elements_ids( (tracks) => { 
            console.log(tracks)
            this.ordering = []
            this.objects = {}
            if (tracks.length == 0) {
                this.ordering.push(null)
                this.save()
            } else {
                tracks.forEach((t) => {
                    this.ordering.push(t.id)
                    this.objects[t.id] = t
                })
            }
            super.refresh(k)
        })            
    }

    get_all_tracks() {
        let Q = []
        this.ordering.forEach((x) => {
            Q.push((x != null) ? this.get_object_by_id(x) : null)})
        return Q
    }

    get_track_by_id(id) {
        return this.get_object_by_id(id)
    }

    reorder_queue(new_order) {
        this.reorder(new_order)
        this.save()
    }

    is_empty() {
        return (super.is_empty()) || (this.ordering[0] == null)
    }

    pop() {
        if (this.is_ready()) {
            if (this.ordering.length > 0) {
                if (this.ordering[0] == null) {
                    return undefined
                }
                let element = this.ordering.shift()
                this.objects[element] = undefined
                this.save()
                this.dispatch("content-changed", this.get_all_tracks())
                return this.get_track_by_id(element)
            } else {
                return undefined
            }
        }
        return undefined
    }

    save() {
        $QUERY("TRUNCATE current_queue", () => {
            let queue_tuples = []
            if (this.ordering.length > 0) {
                for (let i=0; i < this.ordering.length; i++) {
                    queue_tuples.push(`(${i+1}, ${this.ordering[i]})`)
                }
                $QUERY(`INSERT INTO current_queue (position, track_id) VALUES ${queue_tuples.join(",")}`, () => {})    
            }
        })
    }

    _check_availability(element, do_insert) {
        if ((this.ordering.indexOf(element.id) == -1) && 
                !(this.current_session_model.check_membership(element))) {
            do_insert(element)
        }
    }

    insert(element, index) {
        if (this.is_ready()) {
            this._check_availability(element, (e) => {
                super.insert(element, index)
                this.save()
            })
        }
    }

    append(element) {
        if (this.is_ready()) {
            this._check_availability(element, (e) => {
                super.append(element)
                this.save()
            })
        }
    }

    remove(index) {
        if (this.is_ready()) {
            super.remove(index)
            this.save()
        }
    }

    length() {
        if (this.is_ready()) {
            let i = this.ordering.indexOf(null)
            return (i == -1) ? this.ordering.length : i 
        }
        return undefined
    }

    duration() {
        if (this.is_ready()) {
            let d = 0
            for (let i=0; i<this.ordering.length; i++) {
                
                if (this.ordering[i] == null) {
                    return d
                } else {
                    let x = this.get_track_by_id(this.ordering[i])
                    d += (x != undefined) ? x.stream_length : 0                        
                }
            }
            
            return d
        }
        return undefined
    }

}