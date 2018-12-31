class PlaylistModel extends BaseObjectSubsetModel {
    constructor(playlist, tracks_model) {
        super(tracks_model)
        this.info = playlist
        this.initialize()
    }

    refresh(k) {
        DB.get_playlist_tracks(this.info.id, (tracks) => {
            this.objects = {}
            tracks.forEach((t) => {
                this.objects[t.id] = t
            })
            super.refresh(k)
        })            
    }

    compare_objects(a, b) {
        let x = a.title.toLowerCase();
        let y = b.title.toLowerCase();
        if (x < y) {return -1;}
        if (x > y) {return 1;}
        return 0;        
    }

    get_all_tracks() {
        return this.get_all_objects()
    }

    get_track_by_id(id) {
        return this.get_object_by_id(id)
    }

    save() {
        DB.set_playlist_tracks(this.info.id, Object.keys(this.objects), () => {})
    }
    

    _check_availability(element, do_insert) {
        return (this.objects[element.id] == undefined)
    }

    add(element) {
        if (this.is_ready() && this._check_availability(element))  {
            super.add(element)
            this.save()
        }
    }
    
    remove(index) {
        if (this.is_ready()) {
            super.remove(index)
            this.save()
        }
    }
}