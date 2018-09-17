class QueueView extends EventDispatcher {
    constructor(dom_ids) {
        super()
        this.dom_id         = dom_ids.list
        this.controller     = undefined
        this.list_dom       = document.getElementById(dom_ids.list); 
        this.num_tracks_dom = document.getElementById(dom_ids.num_tracks); 
        this.duration_dom   = document.getElementById(dom_ids.duration);

        this.view_list_order = []
        let queue_list = document.getElementById("queue-list-elements")
        queue_list.addEventListener('dragenter', this.handle_drag_enter.bind(this), false);          
        queue_list.addEventListener('dragover',  this.on_drag_over.bind(this), false);
        queue_list.addEventListener('dragend',   this.handle_drag_end.bind(this), false);
        queue_list.addEventListener('drop',      this.handle_drop.bind(this), true);

        this.sortable = Sortable.create(this.list_dom, 
            {
                animation: 150,
                ghostClass: "ghost",

                onStart: function (evt) {
                    console.log("start");
                },
                onEnd: (evt) => {
                    let new_order = []
                    for(i=0; i<this.list_dom.rows.length; i++) {
                        new_order.push(parseInt(this.list_dom.rows[i].attributes["data-track-id"].value))
                    }
                    this.view_list_order = new_order
                    this.dispatch("reorder", this.view_list_order)
                },
            }
        )
    }

    set_controller(controller) {
        this.controller = controller
        this.controller.addView(this)
        this.controller.on("content-changed", this.set_queue.bind(this))
        this.controller.ready(this.set_queue.bind(this))
    }

    set_queue(queue) {
        this.view_list_order = []
        let queue_rows = []  

        for(i=0; i<queue.length; i++) {
            let element = {
                id:       queue[i].id,
                title:    queue[i].title,
                artist:   queue[i].artist,
                bpm:      queue[i].bpm,
                duration: format_nanoseconds(queue[i].stream_length),
            }
            if (queue[i].cover == null) {
                element.cover = "../../../resources/images/default_album_cover.png"
            } else {
                element.cover = `file://${queue[i].image_root}/${queue[i].cover}`
            }
            queue_rows.push(element)
            this.view_list_order.push(queue[i].id)
        }
        this.num_tracks_dom.innerHTML = `${this.controller.q_length()} tracks`
        this.duration_dom.innerHTML = `${format_seconds_long(Math.round(this.controller.duration() / 1000000000))}`
        jui.ready([ "grid.table" ], (table) => {
                table("#queue-list-elements", {
                    data:queue_rows,
                    scroll: false,
                    resize: false
                });
                this.connect_events()
            }
        )
    }

    handle_double_click(e) {
        let x = e.target.closest(".queued-track")
        let track_id = parseInt(x.attributes["data-track-id"].value)
        let track_element = this.controller.get_id(track_id)
        pc.play(track_element)
    }

    handle_drag_enter(e) {
        console.log(e)
    }

    handle_drag_end(e) {
        console.log(e)
    }

    on_drag_over(evt) {
        if (evt.preventDefault) {
            evt.preventDefault();
        }
        console.log(evt)
        evt.dataTransfer.dropEffect = 'move';
    }

    handle_drop(evt) {
        console.log(evt)
        if (evt.stopPropagation) {
            evt.stopPropagation();
        }
        let d = evt.dataTransfer.getData("text/plain")
        try {
            let track = JSON.parse(d)
            this.controller.append(track)
        } catch (error) {
            //pass            
        }

    }

    connect_events() {
        let elements = document.querySelectorAll('.queued-track');
        [].forEach.call(elements, (e) => {
            e.addEventListener('dblclick', this.handle_double_click.bind(this), false);
        });
    }

}