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
        this.refresh()
    }

    async refresh(k) {
        //let ll = await this.model.getAll()
        // DB.get_group_list((queue) => {
        this.queue = await this.model.getAll()
        this.queue_table = {}
        for (let i=0; i<this.queue.length; i++) {
            this.queue_table[this.queue[i]._id] = this.queue[i]
        }
        // console.log(this.queue)
        this.dispatch("content-changed", this.queue)
        //     k()
        // })
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

    append_to_playlist(playlist_id, track_id) {
        DB.add_id_to_playlist(track_id, playlist_id, (x) => {})
    }

    create_playlist(name) {
        DB.create_playlist(name, () => {
            this.refresh(() => {
                this.dispatch("content-changed", this.queue)
            })
        })
    }

    rename_playlist(id, new_name) {
        DB.rename_playlist(id, new_name, () => {
            this.refresh(() => {
                this.dispatch("content-changed", this.queue)
            })
        })
    }

    duplicate_playlist(id) {
        DB.duplicate_playlist(id, () => {
            this.refresh(() => {
                this.dispatch("content-changed", this.queue)
            })
        })
    }

    delete_playlist(id) {
        DB.delete_playlist(id, () => {
            this.refresh(() => {
                this.dispatch("content-changed", this.queue)
            })
        })
    }

    check_name_availability(name, k) {
        DB.check_playlist_name_availability(name, k)
    }

    get_playlist_by_id(id, k) {
        DB.get_playlist_by_id(id, k)
    }

}