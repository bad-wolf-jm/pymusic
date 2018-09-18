class TrackListView extends EventDispatcher {
    constructor(dom_ids) {
        super()
        this.dom_id         = dom_ids.list
        this.controller     = undefined
        this.name_dom       = document.getElementById(dom_ids.name); 
        this.num_tracks_dom = document.getElementById(dom_ids.num_tracks); 
        this.duration_dom   = document.getElementById(dom_ids.duration);
    }

    set_controller(controller) {
        this.controller = controller
        this.controller.addView(this)
        this.controller.on("content-changed", this.set_list.bind(this))
        this.controller.ready(this.set_list.bind(this))
    }

    _get_rating(track_object) {
        let html = "";
        for (let j=1; j<6; j++) {
            html+="<i class='fa " + ( j <= track_object.rating ? "fa-star" : "fa-star-o") +"' style='font-size:8pt; margin-left:3px'></i>";
        }
        return html
    }

    set_list(name, queue) {
        this.view_list_order = []
        let queue_rows       = []  

        for(let i=0; i<queue.length; i++) {
            let element = {
                id:          queue[i].id,
                color:       queue[i].color,
                loved:       "<i title='"+i+"' class='fa " + (queue[i].favorite ? "fa-heart" : "fa-heart-o") +"'></i>",
                title:       queue[i].title,
                artist:      queue[i].artist,
                genre:       queue[i].genre,
                last_played: (queue[i].last_played != null) ? moment(queue[i].last_played).format('MM-DD-YYYY') : "",
                play_count:  queue[i].play_count,
                rating:      this._get_rating(queue[i]), 
                bpm:         queue[i].bpm,
                duration:    format_nanoseconds(queue[i].stream_length),
            }
            queue_rows.push(element)
            this.view_list_order.push(queue[i].id)
        }
        this.name_dom.innerHTML       = `${name}`
        this.num_tracks_dom.innerHTML = `${this.controller.q_length()} tracks`
        this.duration_dom.innerHTML   = `${format_seconds_long(Math.round(this.controller.duration() / 1000000000))}`
        jui.ready([ "grid.table" ], (table) => {
                table("#track-list-elements", {
                    data: queue_rows,
                    scroll: false,
                    resize: false
                });
                this.connect_drag()
                this.table_rows = {}
                let elements = document.querySelectorAll('.track-entry');
                [].forEach.call(document.querySelectorAll('.track-entry'),
                    (x) => {
                        let track_id = parseInt(x.attributes["data-track-id"].value)
                        this.table_rows[track_id] = x
                    } 
                )
            }
        )
    }

    handle_drag_start(e) {
        let track_id = parseInt(e.target.attributes["data-track-id"].value)
        let track_element = this.controller.get_id(track_id)
        e.dataTransfer.setData("text/plain", JSON.stringify(track_element))
    }

    handle_double_click(e) {
        let track_id = parseInt(e.target.parentElement.attributes["data-track-id"].value)
        let track_element = this.controller.get_id(track_id)
        pc.play(track_element)
    }

    select_row(e) {
        let x = e.target.closest("tr")
        x.classList.add("selected")
        //console.log(x)
    }


    connect_drag() {
        let elements = document.querySelectorAll('.track-entry');
        [].forEach.call(elements, (e) => {
            e.addEventListener('dragstart', this.handle_drag_start.bind(this), false);
            e.addEventListener('dblclick', this.handle_double_click.bind(this), false);
            e.addEventListener("click", this.select_row.bind(this))
            //console.log(e)
        });
    }


}