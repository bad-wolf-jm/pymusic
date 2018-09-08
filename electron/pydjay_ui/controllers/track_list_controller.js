class TrackListController extends EventDispatcher {
    constructor() {
        super()
        this.list = []
        this.list_table = {}
        this.ready_wait_queue = []
        this.views = []
    }

    addView(view) {
        this.views.push(view)
        view.on("reorder", this.reorder_queue.bind(this))
    }

    reorder_queue(new_order) {
        for (let i=0; i<new_order.length; i++) {
            this.queue[i] = this.queue_table[new_order[i]]
        }
    }

    ready(func) {
        if (this.queue != undefined) {
            func(this.queue)
        } else {
            this.ready_wait_queue.push(func)
        }
    }

    _do_set_list(name, queue) {
        this.name = name
        this.list = queue
        this.list_table = {}
        for (let i=0; i<queue.length; i++) {
            this.list_table[queue[i].id] = queue[i]
        }
    }

    set_list(name, queue) {
        this._do_set_list(name, queue)
        this.dispatch("content-changed", name, queue)
    }

    q_length() {
        if (this.list != undefined) {
            return this.list.length
        }
        return undefined
    }

    duration () {
        if (this.list != undefined) {
            let d = 0
            for (let i=0; i<this.list.length; i++) {
                d += this.list[i].stream_length
            }
            return d
        }
        return undefined
    }

    reorder () {
        if (this.list != undefined) {
            this.dispatch("content-changed")
            return this.list.length
        }
    }
}