class SessionModel extends BaseOrderedObjectSubsetModel {

    constructor(session, tracks_model) {
        super(tracks_model)
        this.session = session
        this.initialize()
    }

    refresh(k) {
        DB.get_session_tracks(this.session.id, (tracks) => {
            this.objects = {}
            this.ordering = []
            tracks.forEach((t) => {
                this.ordering.push(t.id)
                this.objects[t.id] = t
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
}