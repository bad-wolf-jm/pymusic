class SessionController extends EventDispatcher {
    constructor() {
        super()
        this.model           = undefined

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

    add(element) {
        this.model.add(element)
    }

    q_length() {
        return this.model.length()
    }


    duration () {
        return this.model.duration()
    }
}

