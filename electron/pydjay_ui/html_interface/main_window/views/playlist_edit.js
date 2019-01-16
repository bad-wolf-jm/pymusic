const {remote} = require('electron')
const {Menu, MenuItem} = remote
const {BrowserWindow} = remote
const electron = require('electron');


class PlaylistEditView extends EventDispatcher {
    constructor(dom_ids) {
        super()

        this.element = document.getElementById("queue-list")

        this.dom_id         = dom_ids.list
        this.controller     = undefined
        this.context_menu_element = undefined
        this.list_dom       = document.getElementById(dom_ids.list);
        this.num_tracks_dom = document.getElementById(dom_ids.num_tracks);
        this.duration_dom   = document.getElementById(dom_ids.duration);

        this.view_list_order = []
        let queue_list = document.getElementById("playlist-edit-area")
        queue_list.addEventListener('dragenter', this.handle_drag_enter.bind(this), false);
        queue_list.addEventListener('dragover',  this.on_drag_over.bind(this), false);
        queue_list.addEventListener('dragend',   this.handle_drag_end.bind(this), false);
        queue_list.addEventListener('drop',      this.handle_drop.bind(this), true);

        this.queue_content = undefined

        this.menu = new Menu()
        this.menu.append(new MenuItem({label: 'Track info', click: () => {`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             `
            // let window = new BrowserWindow({width: 1250, height: 750})
            // window.on('closed', () => {
            //     window = null
            // })
            // window.webContents.once("did-finish-load", () => {window.webContents.send("track-id", this.context_menu_element)})
            // window.loadURL('file://' + __dirname + '/../track_edit/layout.html')
            pc.stop()
            view.set_track(this.context_menu_element)
            document.getElementById("track-edit-dialog").showModal()


        }}))
        this.menu.append(new MenuItem({type: 'separator'}))
        this.menu.append(new MenuItem({label: 'Preview',
            submenu: [
                {label: 'Full track', click: () => {
                    pc.play(this.context_menu_element)
                }},
                {label: 'Last 30 seconds', click: () => {
                    pc.play_last_30_seconds(this.context_menu_element)
                }},
                {label: 'Last 10 seconds', click: () =>{
                    pc.play_last_10_seconds(this.context_menu_element)
                }}
            ]}))

        this.menu.append(new MenuItem({type: 'separator'}))
        this.menu.append(new MenuItem({label: 'Remove', click: () =>{ 
            this.controller.remove(this.context_menu_element) 
        }}))

        this.menu.on("menu-will-show", (e) => {})
        this.menu.on("menu-will-close", (e) => {})

        this.sortable = Sortable.create(this.list_dom,
            {
                animation: 150,
                ghostClass: "ghost",
                dataIdAttr: "data-track-id",
                onStart: (evt) => {

                },
                onEnd: async (evt) => {
                    let new_order = []
                    for(let i=0; i<this.list_dom.rows.length; i++) {
                        if (this.list_dom.rows[i].attributes["data-track-id"].value == 'null') {
                            new_order.push(null)
                        } else {
                            new_order.push((this.list_dom.rows[i].attributes["data-track-id"].value))
                        }
                    }
                    this.view_list_order = new_order
                    this.dispatch("reorder", this.view_list_order)
                    this.num_tracks_dom.innerHTML = `${await this.controller.q_length()} tracks - ${format_seconds_long(await Math.round(this.controller.duration() / 1000000000))}`
                },
            }
        )
    }

    set_controller(controller) {
        this.controller = controller
        this.controller.addView(this)
        this.controller.on("content-changed", this.set_queue.bind(this))
    }

    async set_queue(name, queue) {
        this.view_list_order = []
        let queue_rows = []
        for(let i=0; i<queue.length; i++) {
            let element = (queue[i] == null) ? {id: null, stream_length:0} : {
                id:       queue[i]._id,
                title:    queue[i].metadata.title,
                artist:   queue[i].metadata.artist,
                bpm:      queue[i].track.bpm,
                duration: format_nanoseconds(queue[i].track.stream_end - queue[i].track.stream_start),
            }
            if (element.id != null) {
                if (queue[i].metadata.cover == null) {
                    element.cover = "../../resources/images/default_album_cover.png"
                } else {
                    element.cover = `file://${queue[i].metadata.cover.small}`
                }
            }
            queue_rows.push(element)
            this.view_list_order.push(element.id)
        }
        document.getElementById("playlist-edit-name").innerHTML = name
        this.num_tracks_dom.innerHTML = `${await this.controller.q_length()} tracks - ${format_seconds_long(Math.round(await this.controller.duration() / 1000000000))}`
        jui.ready([ "grid.table" ], (table) => {
                if (this.queue_content != undefined) {
                    this.queue_content.reset()
                }
                this.queue_content = table("#playlist-edit-elements", {
                    data: queue_rows,
                    scroll: false,
                    resize: false
                });
                this.connect_events()
            }
        )
    }


    focus() {
        this.element.classList.add("focus")
    }

    blur() {
        this.element.classList.remove("focus")
    }

    delete_selection() {
        let selected = this.selected_element()
        if (selected != undefined) {
            let position = this.view_list_order.indexOf(selected.id)
            this.controller.remove(this.selected_element())
            this._select_row(this.view_elements[this.view_list_order[position]])
        }

    }


    add_element(e) {
        this.controller.append(e)
    }

    move_down() {
        if (this.current_selection != undefined) {
            let track_id = (this.current_selection.attributes["data-track-id"].value)
            if (track_id == "null") {
                track_id = null
            }
            let position = this.view_list_order.indexOf(track_id)
            let n
            if (position != -1) {
                n = (position+1) < this.view_list_order.length ? position+1 : this.view_list_order.length - 1
            } else {
                n = 0
            }

            this._select_row(this.view_elements[this.view_list_order[n]])
        } else {
            this._select_row(this.view_elements[this.view_list_order[0]])
        }
    }


    move_up() {
        if (this.current_selection != undefined) {
            let track_id = (this.current_selection.attributes["data-track-id"].value)
            if (track_id == "null") {
                track_id = null
            }
            let position = this.view_list_order.indexOf(track_id)
            let n
            if (position != -1) {
                n = (position-1) >= 0 ? position-1 : 0
            } else {
                n = 0
            }
            this._select_row(this.view_elements[this.view_list_order[n]])
        } else {
            this._select_row(this.view_elements[this.view_list_order[this.view_elements.length-1]])
        }

    }

    async selected_element() {
        if (this.current_selection != undefined) {
            let track_id = (this.current_selection.attributes["data-track-id"].value)
            if (track_id != "null") {
                return await this.controller.get_id(track_id)
            } else {
                return null
            }
        }
        return undefined
    }

    set_selected_rating(rating) {

    }

    
    toggle_selected_loved() {

    }


    move_last() {

    }

    move_first() {

    }

    page_up() {
        let scroller = document.getElementById("queue-list-area")
        let y = scroller.getBoundingClientRect()
        scroller.scrollTop -= y.height
    }

    page_down() {
        let scroller = document.getElementById("queue-list-area")
        let y = scroller.getBoundingClientRect()
        scroller.scrollTop += y.height
    }

    add_selection_to_queue() {

    }

    add_selection_to_shortlist() {

    }

    add_selection_to_unavailable() {

    }

    remove_selection_from_unavailable() {

    }

    ensure_row_visible(row) {
        let scroller = document.getElementById("playlist-edit-area")
        let scrollerRect = scroller.getBoundingClientRect()

        if (row == undefined) {
            scroller.scrollTop -= (30)
        } else {
            let rowRect = row.getBoundingClientRect()
            let offsetTop = (rowRect.y - scrollerRect.y)
            let offsetBottom = offsetTop + rowRect.height
            let y = scroller.getBoundingClientRect()
            if (offsetBottom > y.height) {
                scroller.scrollTop += (offsetBottom - y.height)
            } else if (offsetTop < 0) {
                scroller.scrollTop += (offsetTop)
            }
        }
    }

    move_selection_up() {

    }

    move_selection_down() {

    }

    move_selection_to_top() {

    }


    async handle_double_click(e) {
        let x = e.target.closest(".playlist-track")
        let track_id = (x.attributes["data-track-id"].value)
        let track_element = await this.controller.get_id(track_id)
        pc.play(track_element)
    }

    handle_drag_enter(e) {

    }

    handle_drag_end(e) {

    }

    on_drag_over(evt) {
        if (evt.preventDefault) {
            evt.preventDefault();
        }
        evt.dataTransfer.dropEffect = 'move';
    }

    async handle_drop(evt) {
        if (evt.stopPropagation) {
            evt.stopPropagation();
        }
        let track_id = evt.dataTransfer.getData("text/plain")
        let track = await MDB.getTrackById(track_id)
        this.controller.append(track)
    }

    _select_row(x) {
        if (this.current_selection != undefined) {
            this.current_selection.classList.remove("selected")
        }
        x.classList.add("selected")
        this.current_selection = x
        this.ensure_row_visible(x)
    }

    select_row(e) {
        let x = e.target.closest(".element")
        this._select_row(x)
    }

    connect_events() {
        let elements = document.querySelectorAll('.playlist-track');
        this.view_elements = {};
        [].forEach.call(elements, (e) => {
            let track_id = (e.attributes["data-track-id"].value)
            if (track_id == "null") {
                track_id = null
            }
            this.view_elements[track_id] = e
            e.addEventListener('dblclick', this.handle_double_click.bind(this), false);
            e.addEventListener("click", this.select_row.bind(this))
            e.addEventListener('contextmenu', async (e) => {
                e.preventDefault()
                let x = e.target.closest('.playlist-track')
                let track_id = (x.attributes["data-track-id"].value)
                let track_element = await this.controller.get_id(track_id)
                this.context_menu_element = track_element
                this.menu.popup({window: remote.getCurrentWindow()})
              }, false)

        });
    }

}
