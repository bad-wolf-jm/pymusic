class QueueController extends EventDispatcher {
    constructor() {
        super()
        this.queue = undefined
        this.queue_table = undefined
        this.ready_wait_queue = []
        this.views = []
        this.forward_content_changed = (q) => {
            this.dispatch("content-changed", q)
        }
    }

    set_model(model) {
        if (this.model != undefined) {
            this.model.un("content-changed", this.forward_content_changed) 
        }
        this.model = model
        this.model.addController(this)
        this.model.on("content-changed", this.forward_content_changed) 
        this.model.ready(() => {
            this.set_list(this.model.get_all_tracks())
        })
    }

    set_list(list) {
        this.dispatch("content-changed", list)
    }

    addView(view) {
        this.views.push(view)
        view.on("reorder", this.reorder_queue.bind(this))
    }

    reorder_queue(new_order) {
        this.model.reorder_queue(new_order)
    }

    ready(func) {
        if (this.queue != undefined) {
            func(this.queue)
        } else {
            this.ready_wait_queue.push(func)
        }
    }

    get_id(id) {
        return this.model.get_track_by_id(id)
    }

    pop() {
       return this.model.pop() 
    }

    insert(element, index) {
        this.model.insert(element, index)
    }

    append(element) {
        this.model.append(element)
    }

    remove(index) {
        this.model.remove(index)
    }

    q_length() {
        return this.model.length()
    }


    duration () {
        return this.model.duration()
    }
}