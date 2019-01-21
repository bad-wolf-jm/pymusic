class SessionsController extends EventDispatcher {
    constructor() {
        super()
        this.queue = undefined
        this.queue_table = undefined
        this.ready_wait_queue = []
        this.views = []
    }

    async refresh(k) {
        this.queue = Object.values(await this.model.getAllObjects())
        this.queue_table = {}
        for (let i=0; i<this.queue.length; i++) {
            this.queue_table[this.queue[i]._id] = this.queue[i]
        }
        this.dispatch("content-changed", this.queue)
    }

    setModel(model) {
        this.model = model
        this.model.on("content-changed", (x) => {
            console.log(x)
            this.dispatch("content-changed", x)
        })
        this.refresh()
    }

    addView(view) {
        this.views.push(view)
    }
}