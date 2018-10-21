const { ipcRenderer } = require('electron');

class TrackListView extends EventDispatcher {
    constructor(dom_ids, queue_controller, shortlist_controller, unavailable_controller) {
        super()
        this.dom_id         = dom_ids.list
        this.controller     = undefined
        this.table          = undefined
        this.name_dom       = document.getElementById(dom_ids.name); 
        this.num_tracks_dom = document.getElementById(dom_ids.num_tracks); 
        this.duration_dom   = document.getElementById(dom_ids.duration);
        this.filter_dom      = document.getElementById(dom_ids.filter); 

        this.shortlist_controller = shortlist_controller        
        this.queue_controller = queue_controller
        this.unavailable_controller = unavailable_controller

        this.menu = new Menu()
        this.menu.append(new MenuItem({label: 'Track info', click: () => { 
            let window = new BrowserWindow({width: 1250, height: 750})
            window.on('closed', () => {
                window = null
            })
            window.webContents.once("did-finish-load", () => {
                window.webContents.send("track-id", this.context_menu_element)
            })
            window.loadURL('file://' + __dirname + '/../track_edit/layout.html')
        }}))
        this.menu.append(new MenuItem({type: 'separator'}))
        this.menu.append(new MenuItem({label: 'Shortlist', click: () => {
            let T = this.context_menu_element
            this.shortlist_controller.add(T)            

        }}))
        
        this.menu.append(new MenuItem({label: 'Marked as played', click: () => {
            let T = this.context_menu_element
            this.unavailable_controller.add(T)            
        }}))
        this.menu.append(new MenuItem({label: 'Add to queue', click: () => {
            let T = this.context_menu_element
            this.queue_controller.append(T)
        }}))
        this.menu.append(new MenuItem({type:  'separator'}))
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
        
        this.menu.on("menu-will-show", (e) => {})
        this.menu.on("menu-will-close", (e) => {})

        this.filter_dom.oninput = (e) => {
            this.filter_list(this.filter_dom.value)
        }

    }

    set_controller(controller) {
        this.controller = controller
        this.controller.addView(this)
        this.controller.on("content-changed", this.set_list.bind(this))
        this.controller.on("selection-changed", this.update_selection.bind(this))
        this.controller.on("element-updated", this.update_element.bind(this))
        this.controller.on("track-unavailable", (tr) => {
            if (tr != undefined) {
                if (this.table_rows[tr.id] != undefined) {
                    this.table_rows[tr.id].classList.add("unavailable")
                }
            }
        })
        this.controller.on("track-available", (tr) => {
            if (tr != undefined) {
                if (this.table_rows[tr.id] != undefined) {
                    this.table_rows[tr.id].classList.remove("unavailable")
                }
            }
        })
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
        if (queue == undefined) {
            queue = []
        }
        for(let i=0; i<queue.length; i++) {
            let element = {
                id:          queue[i].id,
                available:   queue[i].available,
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
            if (this.table != undefined) {
                this.table.reset()
            }
            this.table = table("#track-list-elements", {
                data:   queue_rows,
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
            this._selected_row = undefined
        })
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
        let id = parseInt(x.attributes["data-track-id"].value)
        this.controller.select_element(id)
    }

    update_element(x) {
        let row = this.table_rows[x.id]
        if (row != undefined) {
            if (x.available) {
                row.classList.remove("unavailable")
            } else {
                row.classList.add("unavailable")
            }
        }
    }

    update_selection(selection) {
        if (this._selected_row != undefined) {
            this._selected_row.forEach((x) => {this.table_rows[x.id].classList.remove("selected")})
        }
        this._selected_row = selection
        this._selected_row.forEach((x) => {this.table_rows[x.id].classList.add("selected")})
    }


    connect_drag() {
        let elements = document.querySelectorAll('.track-entry');
        [].forEach.call(elements, (e) => {
            e.addEventListener('dragstart', this.handle_drag_start.bind(this), false);
            e.addEventListener('dblclick', this.handle_double_click.bind(this), false);
            e.addEventListener("click", this.select_row.bind(this))
            e.addEventListener('contextmenu', (e) => {
                e.preventDefault()
                this.select_row(e)
                let x = e.target.closest(".track-entry")
                let track_id = parseInt(x.attributes["data-track-id"].value)
                let track_element = this.controller.get_id(track_id)
                this.context_menu_element = track_element
                this.menu.popup({window: remote.getCurrentWindow()})
              }, false)

        });
    }

    filter_list (text) {
        let i = 0;
        let search_tokens = text.split(' ')
        let search_f = [];
        for (i=0; i<search_tokens.length; i++) {
            let token = search_tokens[i];
            if (token.length > 0) {
                if (search_tokens[i].startsWith('@bpm<')) {
                    let x = parseInt(search_tokens[i].split('<')[1]);
                    if (!isNaN(x)) {
                        search_f.push(
                            function (obj) {
                                return obj.bpm <= x;
                            }
                        )
                    } else {
                        search_f.push( (x) => {return true} )
                    }
                } else if (search_tokens[i].startsWith('@bpm>')) {
                    let x = parseInt(search_tokens[i].split('>')[1]);
                    if (!isNaN(x)) {
                        search_f.push(
                            function (obj) {
                                return (obj.bpm >= x);
                            }
                        )
                    } else {
                        search_f.push( (x) => {return true} )
                    }
                } else if (search_tokens[i].startsWith('@bpm~')) {
                    let x = parseInt(search_tokens[i].split('~')[1]);
                    if (!isNaN(x)) {
                        search_f.push(
                            function (obj) {
                                return (obj.bpm < x*1.2) && (obj.bpm > x*0.9) ;
                            }
                        )
                    } else {
                        search_f.push( (x) => {return true} )
                    }
                } else {
                    search_f.push(
                        function (x) {
                            let fields = [x.title, x.artist, x.genre, `@rat=${x.rating}`, '@bpm']
                            if (x.favorite) {
                                fields.push('@loved')
                            }
                            for (let j=0; j<fields.length; j++) {
                                if (fields[j] != null) {
                                    if ((fields[j].toLowerCase().search(token) != -1)) {
                                        return true;
                                    }
                                }
                            }
                            return false;
                        }
                    )
                }
            }
        }
        let filter = this.controller.filter_ids((obj) => {
            for(i=0; i<search_f.length; i++) {
                let x = search_f[i](obj);
                if (!x) {
                    return false;
                }
            }
            return true;
        })
        Object.keys(this.table_rows).forEach((k) => {
            filter[k] ? this.table_rows[k].classList.remove("filtered") : this.table_rows[k].classList.add("filtered")
        })
    };



}