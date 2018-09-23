class PlaylistsView extends EventDispatcher {
    constructor(dom_ids) {
        super()
        this.dom_id          = dom_ids.list
        this.controller      = undefined
        this.list_dom        = document.getElementById(dom_ids.list); 
        this.view_list_order = []
    }

    set_controller(controller) {
        this.controller = controller
        this.controller.addView(this)
        this.controller.on("content-changed", this.set_list.bind(this))
        this.controller.ready(this.set_list.bind(this))
    }

    on_drag_enter(evt) {
        evt.target.parentElement.classList.add("drop-here")
    }

    on_drag_leave(evt) {
        evt.target.parentElement.classList.remove("drop-here")
    }

    on_drag_over(evt) {
        if (evt.preventDefault) {
            evt.preventDefault();
          }
          evt.dataTransfer.dropEffect = 'move';
    }

    on_drag_end(evt) {
        console.log(evt.target)
    }

    on_drop(evt) {
        if (evt.stopPropagation) {
            evt.stopPropagation();
        }
        let playlist = evt.target.parentElement
        playlist.classList.remove("drop-here")
        let playlist_id = parseInt(playlist.attributes["data-playlist-id"].value)

        let d = evt.dataTransfer.getData("text/plain")
        let track = JSON.parse(d)
        let confirm = new Menu()
        confirm.append(new MenuItem({label: `Add '${track.title}' to '${playlist_id}'?`, click: () => { 
            this.controller.append_to_playlist(playlist_id, track.id)
        }}))
        confirm.append(new MenuItem({type:  'separator'}))
        confirm.append(new MenuItem({label: `Cancel`, click: () => {}}))
        confirm.popup({})
    }


    set_list(list) {
        this.view_list_order = []
        let list_rows = []  

        for(let i=0; i<list.length; i++) {
            let element = {
                id:   list[i].id,
                name: list[i].name,
            }
            list_rows.push(element)
        }
        
        jui.ready([ "grid.table" ], function(table) {
                table("#playlist-list-elements", {
                    data:   list_rows,
                    scroll: false,
                    resize: false
                });
            }
        )
        var drop_targets = document.querySelectorAll('.track-drop-target');
        [].forEach.call(drop_targets, (col) => {
            col.addEventListener('dragenter', this.on_drag_enter.bind(this), false);
            col.addEventListener('dragleave', this.on_drag_leave.bind(this), false);
            col.addEventListener('dragover',  this.on_drag_over.bind(this), false);
            col.addEventListener('dragend',   this.on_drag_end.bind(this), false);
            col.addEventListener('drop',      this.on_drop.bind(this), false);
        });

    }
}