class QueueAreaView extends EventDispatcher {
    constructor(queue_view, playlist_editor) {
        super()

        this.element = document.getElementById("queue-list")
        this.queue_view = queue_view
        this.playlist_editor = playlist_editor

        this.displayed = undefined


        document.getElementById("edit-playlist-save").addEventListener("click", () => {
            this.controller.save_playlist_tracks(this.view_list_order, () => {
                this.hide_playlist_editor()
                // document.getElementById("playlist-edit-display").style.display = null
                // document.getElementById("queue-list-display").style.display = "block"    
            })
        })
        document.getElementById("edit-playlist-cancel").addEventListener("click", () => {
            this.hide_playlist_editor()
            this.playlist_editor.set_queue("",  [])
        })

    }


    show_playlist_editor() {
        document.getElementById("playlist-edit-display").style.display = "block"
        document.getElementById("queue-list-display").style.display = null
        this.displayed = this.playlist_editor
    }

    hide_playlist_editor() {
        document.getElementById("playlist-edit-display").style.display = null
        document.getElementById("queue-list-display").style.display = "block"
        this.displayed = this.queue_view
    }

    focus() {
        this.element.classList.add("focus")
    }

    blur() {
        this.element.classList.remove("focus")
    }

    delete_selection() {
        if (this.displayed != undefined) {
            this.displayed.delete_selection()
        }
    }


    move_down() {
        if (this.displayed != undefined) {
            this.displayed.move_down()
        }
    }


    move_up() {
        if (this.displayed != undefined) {
            this.displayed.move_up()
        }
    }

    // selected_element() {
    //     if (this.current_selection != undefined) {
    //         let track_id = parseInt(this.current_selection.attributes["data-track-id"].value)
    //         // console.log(track_id)
    //         if (!isNaN(track_id)) {
    //             return this.controller.get_id(track_id)
    //         } else {
    //             return null
    //         }
    //     }
    //     return undefined
    // }

    add_element(e) {
        if (this.displayed != undefined) {
            this.displayed.add_element(e)
        }        
    }

    move_last() {

    }


    move_first() {

    }

    page_up() {
        if (this.displayed != undefined) {
            this.displayed.page_up()
        }
        // let scroller = document.getElementById("queue-list-area")
        // let y = scroller.getBoundingClientRect()
        // scroller.scrollTop -= y.height
    }

    page_down() {
        if (this.displayed != undefined) {
            this.displayed.page_down()
        }
        // let scroller = document.getElementById("queue-list-area")
        // let y = scroller.getBoundingClientRect()
        // scroller.scrollTop += y.height
    }

    add_selection_to_queue() {

    }

    add_selection_to_shortlist() {

    }

    add_selection_to_unavailable() {

    }

    remove_selection_from_unavailable() {

    }

    // ensure_row_visible(row) {
    //     let scroller = document.getElementById("queue-list-area")
    //     let scrollerRect = scroller.getBoundingClientRect()

    //     if (row == undefined) {
    //         scroller.scrollTop -= (30)
    //     } else {
    //         let rowRect = row.getBoundingClientRect()
    //         let offsetTop = (rowRect.y - scrollerRect.y)
    //         let offsetBottom = offsetTop + rowRect.height
    //         let y = scroller.getBoundingClientRect()
    //         if (offsetBottom > y.height) {
    //             scroller.scrollTop += (offsetBottom - y.height)
    //         } else if (offsetTop < 0) {
    //             scroller.scrollTop += (offsetTop)
    //         }
    //     }
    // }

    move_selection_up() {
        if (this.displayed != undefined) {
            this.displayed.move_selection_up()
        }
        // let selected = this.selected_element()
        // let selected_id;
        // if (selected !== undefined) {
        //     selected_id = (selected != null) ? selected.id : selected
        //     let position = this.view_list_order.indexOf(selected_id)
        //     if (position > 0) {
        //         let x = this.view_list_order[position - 1]
        //         this.view_list_order[position - 1] = selected_id
        //         this.view_list_order[position] = x
        //         this.dispatch("reorder", this.view_list_order)
        //         this.sortable.sort(this.view_list_order)
        //         this.num_tracks_dom.innerHTML = `${this.controller.q_length()} tracks`
        //         this.duration_dom.innerHTML = `${format_seconds_long(Math.round(this.controller.duration() / 1000000000))}`
        //     }
        // }
    }

    move_selection_down() {
        if (this.displayed != undefined) {
            this.displayed.move_selection_down()
        }
        // let selected = this.selected_element()
        // let selected_id;
        // if (selected !== undefined) {
        //     selected_id = (selected != null) ? selected.id : selected
        //     let position = this.view_list_order.indexOf(selected_id)

        //     if (position + 1 < this.view_list_order.length) {
        //         let x = this.view_list_order[position + 1]
        //         this.view_list_order[position + 1] = selected_id
        //         this.view_list_order[position] = x
        //         this.dispatch("reorder", this.view_list_order)
        //         this.sortable.sort(this.view_list_order)
        //         this.num_tracks_dom.innerHTML = `${this.controller.q_length()} tracks`
        //         this.duration_dom.innerHTML = `${format_seconds_long(Math.round(this.controller.duration() / 1000000000))}`
        //     }
        // }
    }

    move_selection_to_top() {
        if (this.displayed != undefined) {
            this.displayed.move_selection_to_top()
        }
        // let selected = this.selected_element()
        // let selected_id;
        // if (selected !== undefined) {
        //     selected_id = (selected != null) ? selected.id : selected
        //     let position = this.view_list_order.indexOf(selected_id)

        //     this.view_list_order.splice(position, 1)
        //     this.view_list_order.splice(0, 0, selected_id)
        //     this.dispatch("reorder", this.view_list_order)
        //     this.sortable.sort(this.view_list_order)
        //     this.num_tracks_dom.innerHTML = `${this.controller.q_length()} tracks`
        //     this.duration_dom.innerHTML = `${format_seconds_long(Math.round(this.controller.duration() / 1000000000))}`
        // }
    }


    // handle_double_click(e) {
    //     let x = e.target.closest(".queued-track")
    //     let track_id = parseInt(x.attributes["data-track-id"].value)
    //     let track_element = this.controller.get_id(track_id)
    //     pc.play(track_element)
    // }

    // handle_drag_enter(e) {

    // }

    // handle_drag_end(e) {

    // }

    // on_drag_over(evt) {
    //     if (evt.preventDefault) {
    //         evt.preventDefault();
    //     }
    //     evt.dataTransfer.dropEffect = 'move';
    // }

    // handle_drop(evt) {
    //     if (evt.stopPropagation) {
    //         evt.stopPropagation();
    //     }
    //     let d = evt.dataTransfer.getData("text/plain")
    //     try {
    //         let track = JSON.parse(d)
    //         this.controller.append(track)
    //     } catch (error) {
    //         console.log(error)
    //     }

    // }

    // _select_row(x) {
    //     if (this.current_selection != undefined) {
    //         this.current_selection.classList.remove("selected")
    //     }
    //     x.classList.add("selected")
    //     this.current_selection = x
    //     this.ensure_row_visible(x)
    // }

    // select_row(e) {
    //     let x = e.target.closest(".element")
    //     this._select_row(x)
    //     focusWindow(this)
    // }

    // connect_events() {
    //     let elements = document.querySelectorAll('.queued-track');
    //     this.view_elements = {};
    //     [].forEach.call(elements, (e) => {
    //         let track_id = parseInt(e.attributes["data-track-id"].value)
    //         if (isNaN(track_id)) {
    //             track_id = null
    //         }
    //         this.view_elements[track_id] = e
    //         e.addEventListener('dblclick', this.handle_double_click.bind(this), false);
    //         e.addEventListener("click", this.select_row.bind(this))
    //         e.addEventListener('contextmenu', (e) => {
    //             e.preventDefault()
    //             let x = e.target.closest(".queued-track")
    //             let track_id = parseInt(x.attributes["data-track-id"].value)
    //             let track_element = this.controller.get_id(track_id)
    //             this.context_menu_element = track_element
    //             this.menu.popup({window: remote.getCurrentWindow()})
    //           }, false)

    //     });
    // }

}
