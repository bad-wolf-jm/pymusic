class PlaylistsController extends EventDispatcher {
    constructor() {
        super()
        this.queue = undefined
        this.queue_table = undefined
        this.ready_wait_queue = []
        this.views = []
        DB.get_group_list((queue) => {
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
}