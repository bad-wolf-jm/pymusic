class PlaylistsController extends EventDispatcher {
    constructor() {
        super()
        this.queue = undefined
        this.queue_table = undefined
        this.ready_wait_queue = []
        this.views = []
        this.refresh(() => {
            for(let i=0; i<this.ready_wait_queue.length; i++) {
                this.ready_wait_queue[i](this.queue)
            }    
            this.dispatch("content-changed", this.queue)
        })
    }

    refresh(k) {
        DB.get_group_list((queue) => {
            this.queue = queue
            this.queue_table = {}
            for (let i=0; i<queue.length; i++) {
                this.queue_table[queue[i].id] = queue[i]
            }
            k()
            
        })
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

    check_name_availability(name, k) {
        DB.check_playlist_name_availability(name, k)
    }

}