class TrackListController extends EventDispatcher {
    constructor(unavailable_model) {
        super()
        this.list             = []
        this.unavailable      = unavailable_model
        this.views            = []
        this.selection        = undefined
        this.model            = undefined
        this.unavailable.on("track-unavailable", (t) => {
            this.dispatch("track-unavailable", t)
        }) 
        this.unavailable.on("track-available", (t) => {
            this.dispatch("track-available", t)
        }) 

        this.on_content_changed = (q) => {
            this.set_list(this.name, q)
            let U = this.unavailable.get_all_track_ids()
            Object.keys(U).forEach((id) => {this.dispatch("track-unavailable", this.model.get_track_by_id(id))})
        }
        this.on_metadata_changed = (q) => {
            this.list[q.id] = q            
        }
    }
    
    

    set_model(name, model) {
        if (this.model != undefined) {
            this.model.removeController(this)
            this.model.un('content-changed', this.on_content_changed)
            this.model.un('metadata-changed', this.on_metadata_changed)
        }
        this.model = model
        this.model.addController(this)
        this.model.on("content-changed", this.on_content_changed)
        this.model.on("metadata-changed", this.on_metadata_changed)
        this.model.ready(() => {
            let track_list = this.model.get_all_tracks()
            this.set_list(name, track_list)
            let U = this.unavailable.get_all_track_ids()
            Object.keys(U).forEach((id) => {this.dispatch("track-unavailable", this.model.get_track_by_id(id))})
        })
    }

    addView(view) {
        this.views.push(view)
    }

    _do_set_list(name, queue) {
        this.name = name
        this.list = queue
    }

    get_id(id) {
        return this.model.get_track_by_id(id)
    }

    set_list(name, queue) {
        this._do_set_list(name, queue)
        this.dispatch("content-changed", name, queue)
    }

    q_length() {
        return this.model.length()
    }

    select_element(id) {
        this.selection = [this.model.get_track_by_id(id)]
        this.dispatch("selection-changed", this.selection)
    }

    set_data(element, field, value) {
        element[field] = value
        this.dispatch("element-updated", element)
    }

    duration () {
        return this.model.duration()
    }

    filter_ids (func) {
        let mapping = {}
        let x = this.model.get_all_tracks().forEach((t) => {
            mapping[t.id] = func(t)
        })
        return mapping
    }
}