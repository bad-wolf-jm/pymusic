class TrackListModel extends BaseObjectListModel {
    constructor() {
        super()
        this.initialize()

    }

    refresh(k) {
        DB.get_all_tracks((tracks) => {
            this.objects = {}
            tracks.forEach((t) => {this.objects[t.id] = t})
            super.refresh(k)
        })
    }

    compare_tracks(a, b) {
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

    update(id) {
        DB.get_track_by_id(id, (result) => {
            let track = result[0]
            this.objects[id] = track
        })
    }

    set_metadata(track, metadata) {
        super.set_metadata(track, metadata)
        DB.update_track_data(track.id, metadata, () => {
            this.update(track.id)
        })
    }
}