class BaseObjectListModel extends EventDispatcher {
    constructor() {
        super()
        this.objects = {}
        this.controllers = []
        this.ready_wait_queue = []
        this.initialize()
    }

    ready(func) {
        if (this.track_list != undefined) {
            func(this.get_all_objects())
        } else {
            this.ready_wait_queue.push(func)
        }
    }

    add(element) {
        if (this.objects[element.id] == undefined) {
            this.objects[element.id] = element
            this.dispatch("content-changed", this.get_all_tracks())    
        }
    }

    remove(element) {
        if (this.objects[element.id] != undefined) {
            this.objects[element.id] = undefined
            this.dispatch("content-changed", this.get_all_tracks())    
        }
    }

    refresh(k) {
        return k()
    }

    initialize() {
        this.refresh(() => {
            this.trigger_waiting_init_functions()
        })
    }

    trigger_waiting_init_functions() {
        for(let i=0; i<this.ready_wait_queue.length; i++) {
            this.ready_wait_queue[i]()
        }
    }

    addController(controller) {
        this.controllers.push(controller)
    }

    removeController(controller) {
        let X = this.controllers.indexOf(controller)
        (X != -1) && this.controllers.splice(X, 1);
    }

    get_object_by_id(id) {
        return this.objects[id]
    }

    get_objects(idxs, cmp) {
        if (idxs == undefined) {
            idxs = Object.keys(this.objects).map((i) => {return parseInt(i)})
        }
        let objects = idxs.map((id) => {this.objects[id]}) 
        if (cmp != undefined) {
            objects.sort(cmp)
        }
        return objects
    }

    get_all_objects() {
        let objects = Object.values(this.objects)
        if (this.compare_objects != undefined) {
            objects.sort(this.compare_objects)
        }
        return objects
    }

    set_metadata(object, metadata) {
        object = this.objects[object.id]
        Object.keys(metadata).forEach((x) => {
            object[x] = metadata[x]
        })
        this.dispatch("object-metadata-changed", this.objects[object.id])
    }

    length() {
        if (this.objects != undefined) {
            return Object.keys(this.objects).length
        }
        return undefined
    }

    duration(idxs) {
        if (idxs == undefined) {
            idxs = Object.keys(this.objects).map((i) => {return parseInt(i)})
        }
        if (this.objects != undefined) {
            let d = 0
            idxs.forEach((id) => {
                d += (this.objects[id] != undefined) ? this.objects[id].stream_length : 0
            })
            return d
        }
        return undefined
    }
}