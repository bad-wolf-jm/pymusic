class PlaylistController extends TrackListController {
    constructor(unavailable) {
        super(unavailable)
        // this.queue = undefined
        // this.queue_table = undefined
        // this.ready_wait_queue = []
        // this.views = []

        // this.refresh(() => {
        //     for(let i=0; i<this.ready_wait_queue.length; i++) {
        //         this.ready_wait_queue[i](this.queue)
        //     }    
        // })


    }

    set_model(info, model) {
        super.set_model(info.name, model)
        this.info = info
        // if (this.model != undefined) {
        //     this.model.removeController(this)
        //     this.model.un('content-changed', this.on_content_changed)
        //     this.model.un('metadata-changed', this.on_metadata_changed)
        // }
        // this.model = model
        // this.model.addController(this)
        // this.model.on("content-changed", this.on_content_changed)
        // this.model.on("metadata-changed", this.on_metadata_changed)
        // this.model.ready(() => {
        //     let track_list = this.model.get_all_tracks()
        //     this.set_list(name, track_list)
        //     let U = this.unavailable.get_all_track_ids()
        //     Object.keys(U).forEach((id) => {
        //         this.dispatch("track-unavailable", this.model.get_track_by_id(id))})
        // })
    }

    save_playlist_tracks(y, k) {
        this.model.set_tracks(y, k)
    }

    // refresh(k) {
    //     DB.get_sessions_list((queue) => {
    //         this.queue = queue
    //         this.queue_table = {}
    //         for (let i=0; i<queue.length; i++) {
    //             this.queue_table[queue[i].id] = queue[i]
    //         }
    //         k()
    //         this.dispatch("content-changed", this.queue)
    //     })
    // }


    // addView(view) {
    //     this.views.push(view)
    // }

    // ready(func) {
    //     if (this.queue != undefined) {
    //         func(this.queue)
    //     } else {
    //         this.ready_wait_queue.push(func)
    //     }
    // }
}