class UnionModel extends EventDispatcher {
    constructor() {
        super()
        this.models = {}
        this.model_tracks = {}
    }

    addModel(name, model) {
        if (this.models[name] == undefined) {
            this.models[name] = model
            model.ready((q) => {
                if (q != undefined) {
                    this.model_tracks[name] = model.get_all_tracks().map((x) => {return (x != null) ? x.id : null})
                }
            })
            this.model_tracks[name] = [] 
            this.models[name].on("content-changed", (q) => {
                if (q != undefined) {
                    Q = q.map((x) => {return (x != null) ? x.id : null})
                } else {
                    Q = []
                }
                let tracks_to_add    = this.difference(Q, this.model_tracks[name]) 
                let tracks_to_remove = this.difference(this.model_tracks[name], Q) 
                let current_tracks   = this.get_all_track_ids()
                tracks_to_remove.forEach((i) => {
                    if (current_tracks[i] == 1) {
                        this.dispatch("track-available", this.models[name].get_track_by_id(i))
                    }
                }) 
                tracks_to_add.forEach((i) => {
                    if (current_tracks[i] == undefined) {
                        this.dispatch("track-unavailable", this.models[name].get_track_by_id(i))
                    }
                }) 
                this.model_tracks[name] = Q
            })
        }
    }

    difference(A, B) {
        let filter = {}
        B.forEach((i) => {filter[i] = true})
        return A.filter((x) => {return (filter[x] == undefined)})
    }

    get_all_track_ids() {
        let models = Object.keys(this.model_tracks)
        let track_set = {}
        for (let i=0; i<models.length; i++) {
            this.model_tracks[models[i]].forEach((j) => {
                track_set[j] = (track_set[j] == undefined) ? 1 : (track_set[j] + 1)
            })
        }
        return track_set
    }
}