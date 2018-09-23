class SessionController extends EventDispatcher {
    constructor() {
        super()
        this.model           = undefined
        //this.queue_table      = undefined
        //this.ready_wait_queue = []
        //this.views            = []

        this.forward_content_changed = (q) => {
            this.dispatch("content-changed", q)
        }
        // DB.get_played_queue_elements((queue) => {
        //     this.queue = queue
        //     this.queue_table = {}
        //     for (let i=0; i<queue.length; i++) {
        //         this.queue_table[queue[i].id] = queue[i]
        //     }
        //     for(let i=0; i<this.ready_wait_queue.length; i++) {
        //         this.ready_wait_queue[i](this.queue)
        //     }
        // })
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

    // ready(func) {
    //     if (this.queue != undefined) {
    //         func(this.queue)
    //     } else {
    //         this.ready_wait_queue.push(func)
    //     }
    // }

    add(element) {
        this.model.add(element)
    }

    q_length() {
        return this.model.length()
    }


    duration () {
        return this.model.duration()
    }


    // q_length() {
    //     if (this.queue != undefined) {
    //         return this.queue.length
    //     }
    //     return undefined
    // }

    // duration () {
    //     if (this.queue != undefined) {
    //         let d = 0
    //         for (let i=0; i<this.queue.length; i++) {
    //             d += this.queue[i].stream_length
    //         }
    //         return d
    //     }
    //     return undefined
    // }
}