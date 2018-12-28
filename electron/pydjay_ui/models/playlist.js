class PlaylistModel extends BaseListModel {
    constructor(playlist, tracks_model) {
        super()
        this.tracks_model = tracks_model
        this.info = playlist

        this.tracks_model.on('metadata-changed', (x) => {
            this.dispatch("metadata-changed", x)
        })

        DB.get_playlist_tracks(playlist.id, 
            (tracks) => { 
                this.track_list = {}
                this.tracks_order = []
                let elements = {}
                tracks.forEach((t) => {
                    elements[t.id] = true 
                })
                this.tracks_order = Object.keys(elements)
                for(let i=0; i<this.ready_wait_queue.length; i++) {
                    this.ready_wait_queue[i]()
                }                                                            
            }
        )            
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
        this.tracks_order.forEach((x) => {
            Q.push(this.tracks_model.get_track_by_id(x))
        })
        Q.sort(this.compare_tracks)
        return Q
    }

    get_track_by_id(id) {
        return this.tracks_model.get_track_by_id(id)
    }

    set_metadata(track, metadata) {
        this.tracks_model.set_metadata(track, metadata)
    }

    save() {
        let elements = {}
        this.tracks_order.forEach((t) => {
            elements[t] = true 
        })
        DB.set_playlist_tracks(this.info.id, Object.keys(elements), () => {})
    }
    

    _check_availability(element, do_insert) {
        if ((this.tracks_order.indexOf(element.id.toString()) == -1)) {
            do_insert(element)
        }
    }


    add(element) {
        if (this.tracks_order != undefined) {
            this._check_availability(element, (e) => {
                this.tracks_order.push(e.id.toString())
                this.save()
                this.dispatch("content-changed", this.get_all_tracks())    
            })
        }
    }

    remove(index) {
        console.log(index)
        console.log(this.tracks_order)
        if (this.tracks_order != undefined) {
            let I = this.tracks_order.indexOf(index.id.toString())
            if (I != -1) {
                this.tracks_order.splice(I, 1)
                this.save()
                this.dispatch("content-changed", this.get_all_tracks())
            }
        }
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