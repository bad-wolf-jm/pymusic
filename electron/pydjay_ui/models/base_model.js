class BaseListModel extends EventDispatcher {
    constructor() {
        super()
        this.track_list  = undefined
        this.controllers = []
        this.ready_wait_queue = []
    }

    ready(func) {
        if (this.track_list != undefined) {
            func(this.track_list)
        } else {
            this.ready_wait_queue.push(func)
        }
    }

    addController(controller) {
        this.controllers.push(controller)
    }

    removeController(controller) {
        let X = this.controllers.indexOf(controller)
        if (X != -1) {
            this.controllers.splice(X, 1 );
        }
    }

    get_all_tracks() {
        return []
    }

    length() {
        if (this.track_list != undefined) {
            return Object.keys(this.track_list).length
        }
        return undefined
    }

    duration() {
        if (this.track_list != undefined) {
            let d = 0
            let K = Object.keys(this.track_list).map((i) => {return parseInt(i)})
            for (let i=0; i<K.length; i++) {
                d += this.track_list[K[i]].stream_length
            }
            return d
        }
        return undefined
    }

}