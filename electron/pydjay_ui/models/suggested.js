class SuggestedModel extends BaseObjectSubsetModel {
    constructor(tracks_model) {
        super(tracks_model)
        this.initialize() 
    }

    refresh(k) {
        DB.get_suggested_tracks( (tracks) => { 
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
}