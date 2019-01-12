class SessionsController extends EventDispatcher {
    constructor() {
        super()
        this.queue = undefined
        this.queue_table = undefined
        this.ready_wait_queue = []
        this.views = []

        // this.refresh(() => {
        //     for(let i=0; i<this.ready_wait_queue.length; i++) {
        //         this.ready_wait_queue[i](this.queue)
        //     }    
        // })


    }

    async refresh(k) {
        this.queue = await this.model.getAllObjects()
        // DB.get_sessions_list((queue) => {
        //     this.queue = queue
        this.queue_table = {}
        for (let i=0; i<this.queue.length; i++) {
            this.queue_table[this.queue[i]._id] = this.queue[i]
        }
        // k()
        this.dispatch("content-changed", this.queue)
        // })
    }

    setModel(model) {
        this.model = model
        this.refresh()
    }

    addView(view) {
        this.views.push(view)
    }

    ready(func) {
        if (this.queue != undefined) {
            func(this.queue)
        } else {
            this.ready_wait_queue.push(func)
        }
    }
}