class TrackListController extends EventDispatcher {
    constructor() {
        super()
        this.list             = []
        //this.list_table       = {}
        // this.ready_wait_queue = []
        this.views            = []
        this.selection        = undefined
        this.model            = undefined
    }

    set_model(name, model) {
        if (this.model != undefined) {
            this.model.removeController(this)
        }
        this.model = model
        this.model.addController(this)
        this.model.ready(() => {
            this.set_list(name, this.model.get_all_tracks())
        })
    }

    addView(view) {
        this.views.push(view)
    }

    // reorder_queue(new_order) {
    //     for (let i=0; i<new_order.length; i++) {
    //         this.queue[i] = this.queue_table[new_order[i]]
    //     }
    // }


    // ready(func) {
    //     if (this.queue != undefined) {
    //         func(this.queue)
    //     } else {
    //         this.ready_wait_queue.push(func)
    //     }
    // }

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
            // if (this.list != undefined) {
            //     return this.list.length
            // }
            // return undefined
    }

    select_element(id) {
        // console.log(id)
        this.selection = [this.model.get_track_by_id(id)]
        this.dispatch("selection-changed", this.selection)
    }

    set_data(element, field, value) {
        element[field] = value
        this.dispatch("element-updated", element)
    }

    duration () {
        return this.model.duration()
        // if (this.list != undefined) {
        //     let d = 0
        //     for (let i=0; i<this.list.length; i++) {
        //         d += this.list[i].stream_length
        //     }
        //     return d
        // }
        // return undefined
    }

    // reorder () {
    //     if (this.list != undefined) {
    //         this.dispatch("content-changed")
    //         return this.list.length
    //     }
    // }
}