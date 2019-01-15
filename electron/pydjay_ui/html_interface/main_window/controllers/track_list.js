class TrackListController extends EventDispatcher {
    constructor(unavailable_model) {
        super()
        this.list             = []
        this.unavailable      = unavailable_model
        this.views            = []
        this.selection        = undefined
        this.model            = undefined

        // this.unavailable.on("track-unavailable", (t) => {
        //     this.dispatch("track-unavailable", t)
        // }) 
        // this.unavailable.on("track-available", (t) => {
        //     this.dispatch("track-available", t)
        // }) 

        this.on_content_changed = async (q) => {
            this.set_list(this.name, q)
            let U = await this.unavailable.getTracks()
            Object.keys(U).forEach(async (id) => {
                this.dispatch("track-unavailable", (await this.model.getElementById(id)))})
        }
        this.on_metadata_changed = (q) => {
            this.list[q.id] = q
            this.dispatch("element-updated", q)
        }
    }

    async set_model(name, model) {
        if (this.model != undefined) {
            this.model.un('content-changed', this.on_content_changed)
            this.model.un('object-updated', this.on_metadata_changed)
        }
        this.model = model
        this.model.on("content-changed", this.on_content_changed)
        this.model.on("object-updated", this.on_metadata_changed)

        let track_list = await this.model.getTracks()
        this.set_list(name, track_list)
    }

    addView(view) {
        this.views.push(view)
    }

    _do_set_list(name, queue) {
        this.name = name
        this.list = queue
    }

    getElementById(id) {
        return this.model.getElementById(id)
    }

    set_list(name, queue) {
        this._do_set_list(name, queue)
        this.dispatch("content-changed", name, queue)
    }

    q_length() {
        return this.model.length()
    }

    async select_element(id) {
        this.selection = [await this.model.getElementById(id)]
        this.dispatch("selection-changed", this.selection)
    }

    select_next() {
        if ((this.selection == undefined) || (this.selection.length == 0)) {
            this.selection = [this.model.get_first_track()]
        } else {
            this.selection = [this.model.get_next_track(this.selection[0])]
            this.dispatch("selection-changed", this.selection)    
        }
    }

    async setTrackMetadata(track, metadata) {
        if (this.model != undefined) {
            await this.model.setTrackMetadata(track, metadata)
        }
    }



    duration () {
        return this.model.duration()
    }

    async filter_ids (func) {
        let mapping = {}
        let x = (await this.model.getTracks()).forEach((t) => {
            mapping[t._id] = func(t)
        })
        return mapping
    }
}