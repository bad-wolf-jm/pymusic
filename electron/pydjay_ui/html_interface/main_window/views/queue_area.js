class QueueAreaView extends EventDispatcher {
    constructor(queue_view, playlist_editor) {
        super()

        this.element = document.getElementById("queue-list")
        this.queue_view = queue_view
        this.playlist_editor = playlist_editor

        this.displayed = undefined


        // document.getElementById("edit-playlist-save").addEventListener("click", () => {
        //     this.controller.save_playlist_tracks(this.view_list_order, () => {
        //         this.hide_playlist_editor()
        //     })
        // })
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


    selected_element() {
        if (this.displayed != undefined) {
            return this.displayed.selected_element()
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
    }

    page_down() {
        if (this.displayed != undefined) {
            this.displayed.page_down()
        }
    }

    add_selection_to_queue() {

    }

    add_selection_to_shortlist() {

    }

    add_selection_to_unavailable() {

    }

    remove_selection_from_unavailable() {

    }

    move_selection_up() {
        if (this.displayed != undefined) {
            this.displayed.move_selection_up()
        }
    }

    move_selection_down() {
        if (this.displayed != undefined) {
            this.displayed.move_selection_down()
        }
    }

    move_selection_to_top() {
        if (this.displayed != undefined) {
            this.displayed.move_selection_to_top()
        }
    }
}
