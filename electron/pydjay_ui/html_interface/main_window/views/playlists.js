class PlaylistsView extends EventDispatcher {
    constructor(dom_ids) {
        super()
        this.dom_id          = dom_ids.list
        this.controller      = undefined
        this.add_row         = 
        this.view_list_order = []

        this.menu = new Menu()
        this.menu.append(new MenuItem({label: 'Edit...', click: async () => {
            let T = this.context_menu_element
            let p = await this.controller.get_playlist_by_id(T) //this.controller.get_playlist_by_id(T, (p) => {
            let L = new TrackSetModel(MDB, MDB.playlists, T)
            PE_controller.set_model(p, L)
            Q.show_playlist_editor()
            //})

        }}))
        this.menu.append(new MenuItem({type: 'separator'}))
        this.menu.append(new MenuItem({label: 'Rename', click: () => {
            let T = this.context_menu_element
            let old_value = this.context_menu_cell.innerHTML
            this.context_menu_cell.innerHTML = `<input id="new-playlist-name-${T}" type="text" class="new-playlist" value="${old_value}">`
            let X = document.getElementById(`new-playlist-name-${T}`)
            X.focus()
            X.addEventListener("keyup", async (e) => {
                if (e.key == "Escape") {
                    this.context_menu_cell.innerHTML = old_value
                } else if (e.key == "Enter") {
                    let new_name = X.value
                    if (await this.controller.checkNameAvailability(new_name)) {
                        this.controller.rename_playlist(T, new_name)
                    } else {
                        X.style.color = "#dd0000"
                    }
                } else {
                    let new_name = X.value
                    if (await this.controller.checkNameAvailability(new_name)) {
                        X.style.color = null
                    } else {
                        X.style.color = "#dd0000"
                    }
                }
            })
        }}))
        this.menu.append(new MenuItem({label: 'Duplicate', click: () => {
            let T = this.context_menu_element
            this.controller.duplicate_playlist(T)
        }}))
        this.menu.append(new MenuItem({type: 'separator'}))
        this.menu.append(new MenuItem({label: 'Delete', click: async () => {
            let T = this.context_menu_element
            let playlist = await this.controller.get_playlist_by_id(T)
            let dialog = new Question({
                title: "Delete playlist",
                question: `Delete <i><b>'${playlist.name}'</b></i>? This operation cannot be undone`,
                confirmText: "yes",
                dismissText: 'no',
                confirmAction: async () => {
                    await this.controller.delete_playlist(this.context_menu_element)
                    this.context_menu_element = undefined
                    dialog.close()
                },
                dismissAction: () => {
                    this.context_menu_element = undefined
                    dialog.close()
                },
            })
            dialog.open()    
        }}))
    }

    begin_add() {
        document.getElementById("new-playlist").style.display = null
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
        //console.log(evt.target)
    }

    async on_drop(evt) {
        if (evt.stopPropagation) {
            evt.stopPropagation();
        }
        let playlist = evt.target.parentElement
        playlist.classList.remove("drop-here")
        let playlist_id = (playlist.attributes["data-playlist-id"].value)

        let d = evt.dataTransfer.getData("text/plain")
        playlist = await MDB.playlists.getObjectById(playlist_id)
        let track = await MDB.tracks.getObjectById(d) 
        let confirm = new Menu()
        confirm.append(new MenuItem({label: `Add '${track.title}' to '${playlist.name}'?`, click: async () => { 
            await this.controller.append_to_playlist(playlist_id, track)
        }}))
        confirm.append(new MenuItem({type:  'separator'}))
        confirm.append(new MenuItem({label: `Cancel`, click: () => {}}))
        confirm.popup({})
    }


    set_list(list) {
        this.view_list_order = []
        let list_rows = [{_id: null}]  

        list.sort((a, b) => {return a.name.localeCompare(b.name)})

        for(let i=0; i<list.length; i++) {
            let element = {
                _id:   list[i]._id,
                name: list[i].name,
            }
            list_rows.push(element)
        }
        
        jui.ready([ "grid.table" ], (table) => {
                table("#playlist-list-elements", {
                    data:   list_rows,
                    scroll: false,
                    resize: false
                });

                let X = document.getElementById("new-playlist-name")
                X.addEventListener("keyup", (e) => {
                    if (e.key == "Escape") {
                        document.getElementById("new-playlist").style.display="none"
                    } else if (e.key == "Enter") {
                        let new_name = X.value
                        this.controller.create_playlist(new_name)
                    }
                })
        
                var drop_targets = document.querySelectorAll('.track-drop-target');
                [].forEach.call(drop_targets, (col) => {
                    col.addEventListener('dragenter', this.on_drag_enter.bind(this), false);
                    col.addEventListener('dragleave', this.on_drag_leave.bind(this), false);
                    col.addEventListener('dragover', this.on_drag_over.bind(this), false);
                    col.addEventListener('dragend', this.on_drag_end.bind(this), false);
                    col.addEventListener('drop', this.on_drop.bind(this), false);
                    col.addEventListener('click', (e) => {
                        let x = e.target.closest(".track-drop-target")
                        let playlist_id = (x.attributes["data-playlist-id"].value)
                        display_playlist(playlist_id)
                    }, false);
        
                    col.addEventListener('contextmenu', (e) => {
                        e.preventDefault()
                        let x = e.target.closest(".track-drop-target")
                        let playlist_id = (x.attributes["data-playlist-id"].value)
                        this.context_menu_element = playlist_id
                        this.context_menu_cell = document.getElementById(`playlist-element-${playlist_id}`)
                        this.menu.popup({window: remote.getCurrentWindow()})
                      }, false)
        
                });
        

            }
        )


    }
}