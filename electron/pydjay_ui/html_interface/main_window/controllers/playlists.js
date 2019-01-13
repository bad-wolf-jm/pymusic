class PlaylistsController extends EventDispatcher {
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
        //     this.dispatch("content-changed", this.queue)
        // })
    }

    async setModel(m) {
        this.model = m
        this.model.on("content-changed", (x) => {
            console.log(x)
            this.dispatch("content-changed", x)
        })
        this.refresh()
    }

    async refresh(k) {
        this.queue = Object.values(await this.model.getAllObjects())
        this.queue_table = {}
        for (let i=0; i<this.queue.length; i++) {
            this.queue_table[this.queue[i]._id] = this.queue[i]
        }
        this.dispatch("content-changed", this.queue)
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

    async append_to_playlist(playlist_id, track_id) {
        return await this.model.appendToPlaylist(playlist_id, track_id)
    }

    async create_playlist(name) {
        return await this.model.createPlaylist(name)
    }

    async rename_playlist(id, new_name) {
        return await this.model.renamePlaylist(id, new_name)
    }

    async duplicate_playlist(id) {
        return await this.model.duplicatePlaylist(id)
    }

    async delete_playlist(id) {
        return await this.model.deletePlaylist(id)
    }

    async checkNameAvailability(name, k) {
        return await this.model.checkNameAvailability(name)
    }

    async get_playlist_by_id(id, k) {
        return this.model.getObjectById(id)
    }

}