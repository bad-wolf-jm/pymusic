class QueueController extends EventDispatcher {
    constructor() {
        super()
        this.queue = undefined
        this.queue_table = undefined
        this.ready_wait_queue = []
        this.views = []
        DB.get_queue_elements((queue) => {
            this.queue = queue
            this.queue_table = {}
            for (let i=0; i<queue.length; i++) {
                this.queue_table[queue[i].id] = queue[i]
            }
            for(let i=0; i<this.ready_wait_queue.length; i++) {
                this.ready_wait_queue[i](this.queue)
            }
        })
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

    get_id(id) {
        return this.queue_table[id]
    }

    pop() {
        if (this.queue != undefined) {
            if (this.queue.length > 0) {
                let element = this.queue.shift()
                this.dispatch("content-changed", this.queue)
                return element
            } else {
                return undefined
            }
        }
        return undefined
    }

    insert(element, index) {
        if (this.queue != undefined) {
            this.queue.splice(index, 0, element)
            this.dispatch("content-changed", this.queue)
        }
    }

    append(element, index) {
        if (this.queue != undefined) {
            this.queue.push(element)
            this.queue_table[element.id] = element
            this.dispatch("content-changed", this.queue)
        }
    }

    remove(index) {
        if (this.queue != undefined) {
            this.queue.splice(index, 1)
            this.dispatch("content-changed", this.queue)
        }
    }

    q_length() {
        if (this.queue != undefined) {
            return this.queue.length
        }
        return undefined
    }

    duration () {
        if (this.queue != undefined) {
            let d = 0
            for (let i=0; i<this.queue.length; i++) {
                d += this.queue[i].stream_length
            }
            return d
        }
        return undefined
    }

    reorder () {
        if (this.queue != undefined) {
            this.dispatch("content-changed")
            return this.queue.length
        }
    }
}