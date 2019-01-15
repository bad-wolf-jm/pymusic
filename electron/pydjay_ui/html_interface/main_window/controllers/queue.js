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
        this.forward_object_updated = (q) => {
            this.dispatch("object-updated", q)
        }
    }

    async set_model(model) {
        if (this.model != undefined) {
            this.model.un("content-changed", this.forward_content_changed) 
            this.model.un("object-updated", this.forward_object_updated)
        }
        this.model = model
        this.model.on("content-changed", this.forward_content_changed) 
        this.model.on("object-updated", this.forward_object_updated)
        this.set_list(await this.model.getTracks())
    }

    set_list(list) {
        this.dispatch("content-changed", list)
    }

    addView(view) {
        this.views.push(view)
    }

    reorder_queue(new_order) {
        return this.model.reorder(new_order, true)
    }

    ready(func) {
        if (this.queue != undefined) {
            func(this.queue)
        } else {
            this.ready_wait_queue.push(func)
        }
    }

    async is_empty() {
        return await this.model.isEmpty()
    }

    async get_id(id) {
        return this.model.getElementById(id)
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