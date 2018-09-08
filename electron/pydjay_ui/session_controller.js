class SessionController extends EventDispatcher {
    constructor() {
        super()
        this.queue = undefined
        this.queue_table = undefined
        this.ready_wait_queue = []
        this.views = []
        DB.get_played_queue_elements((queue) => {
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

    ready(func) {
        if (this.queue != undefined) {
            func(this.queue)
        } else {
            this.ready_wait_queue.push(func)
        }
    }

    add(element) {
        if (this.queue != undefined) {
            this.queue.push(element)
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
}