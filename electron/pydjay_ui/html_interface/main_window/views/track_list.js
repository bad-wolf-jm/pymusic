const { ipcRenderer } = require('electron');
const Clusterize = require("clusterize.js")
class TrackListView extends EventDispatcher {
    constructor(dom_ids, queue_controller, shortlist_controller, unavailable_controller) {
        super()

        this.element = document.getElementById("main-list")

        this.dom_id     = dom_ids.list
        this.controller = undefined
        this.table      = undefined
        this.queue_rows = undefined

        this.prevWidth = [];

        let cp = document.getElementById("main-track-list-color-chooser")
        this.hueb = (new Huebee(cp, {
            notation: "hex",
            saturations: 1,
            // staticOpen:true
        }))
        this.hueb.on( 'change', ( color, hue, sat, lum ) => {
            let track = this.controller.get_id(this.color_picker_track_id)
            this.controller.set_metadata(track, {color: color})
            let cp = document.getElementById("main-track-list-color-chooser")
            cp.classList.remove("show")
            this.color_picker_track_id = undefined
            this.hueb.close()
        })


        this.list_cluster = new Clusterize({
            rows: [],
            scrollId: 'main-track-list-scroller',
            contentId: 'main-track-list-body',
            callbacks: {
                clusterWillChange: () => {
                    this.table_rows = {}
                },
                clusterChanged: () => {
                    let elements = document.querySelectorAll('.track-entry');
                    let unavailable;
                    if  (this.controller != undefined) {
                        unavailable = this.controller.unavailable.get_all_track_ids();
                    } else {
                        unavailable = {}
                    }
                    [].forEach.call(elements, (e) => {
                        let track_id = parseInt(e.attributes["data-track-id"].value)
                        this.table_rows[track_id] = e
                        if (unavailable[track_id] != undefined) {
                            e.classList.add("unavailable")
                        }
                    });
                    this.fitHeaderColumns()

                    elements = document.querySelectorAll('.show-color-picker');
                    [].forEach.call(elements, (e) => {
                        e.addEventListener("click", () => {
                            this.hueb.open()
                            let track_id = parseInt(e.attributes['data-track-id'].value)
                            //let scroller = document.getElementById("main-track-list-scroller")
                            //let cp = document.getElementById("main-track-list-color-chooser")
                            //let button_rect = e.getBoundingClientRect()
                            //let scrollerRect = scroller.getBoundingClientRect()
                            //cp.style.top = (button_rect.bottom - scrollerRect.top)+"px"
                            //cp.style.left = (button_rect.right)+"px"
                            //cp.classList.toggle("show")
                            this.color_picker_track_id = track_id
                    })})
                },
                scrollingProgress: (progress) => {}
            }
          });

        $('#main-track-list-body').on('click', (e) => {
            this.handle_click(e)
        });

        $('#main-track-list-body').on('dblclick', (e) => {
            this.handle_double_click(e)
        });

        document.getElementById('main-track-list-body').addEventListener('dragstart', (e) => {
            this.handle_drag_start(e)
        }, false);

        $('#main-track-list-body').on('contextmenu', (e) => {
            e.preventDefault()
            this.select_row(e)
            let x = e.target.closest(".track-entry")
            let track_id = parseInt(x.attributes["data-track-id"].value)
            let track_element = this.controller.get_id(track_id)
            this.context_menu_element = track_element
            this.menu.popup({window: remote.getCurrentWindow()})
        });

        document.getElementById("track-list-header").innerHTML = this.render_header({
            id:          "NONE",
            loved:       "<b><i class='fa fa-heart' style='font-size: 12px'/></b>",
            title:       "Title",
            artist:      "Artist",
            genre:       "Genre",
            last_played: "<b><span class='fa fa-calendar' style='font-size: 15px'/></b>",
            play_count:  "<b><span class='fa fa-play'/></b>",
            rating:      "Rating",
            bpm:         "<b style='font-size: 13px'><span class='fa fa-heartbeat' style='font-size: 15px'/></b>",
            duration:    "Time",

        });

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
            pc.stop()
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

    render_row_internal(track, element) {
        return `<tr  id='track-row-${track.id}' class="list-group-item row track-entry" style="color:${track.color}" draggable=true data-track-id=${track.id}>
            <${element} style="width:25px; text-align:center">                         
                <input id='track-color-value-${track.id}' type="hidden" value="" class="main-list-color-value" data-track-id=${track.id}/>                                  
                <button id='track-color-${track.id}' class="main-list color-chooser show-color-picker" style="background-color:${track.color}" data-track-id=${track.id}></button>
            </${element}>
            <${element} id='track-loved-${track.id}' style="width:25px; padding:5px 3px 5px 3px; text-align:center; font-size:8pt">${track.loved}</${element}>
            <${element} style="max-width:125px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${track.title}</${element}>
            <${element} style="max-width:115px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${track.artist}</${element}>
            <${element} style="max-width:40px;  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${track.genre}</${element}>
            <${element} style="text-align:right; width:25px; padding-right:9px">${track.play_count}</${element}>
            <${element} style="width:75px">${track.last_played}</${element}>
            <${element} id='track-rating-${track.id}' style="width:25px">${track.rating}</${element}>
            <${element} style="width:30px; text-align:right; padding-right:5px">${track.bpm}</${element}>
            <${element} style="width:45px; text-align:right">${track.duration}</${element}>
            <${element} style="width:15px"></${element}>
        </tr>`

    }

    fitHeaderColumns() {
        let $headers = $("#track-list-elements-header")
        let $firstRow = $("#main-track-list-table").find('tr:not(.clusterize-extra-row):first');
        let columnsWidth = [];
        $firstRow.children().each(function () {
            columnsWidth.push($(this).width());
        });
        if (columnsWidth.toString() == this.prevWidth.toString()) return;
        $headers.find('tr').children().each(function(i) {
            $(this).width(columnsWidth[i]);
        });
        this.prevWidth = columnsWidth;
    }

    render_row(track) {
        return this.render_row_internal(track, "td")
    }

    render_header(track) {
        return this.render_row_internal(track, "th")
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

    _get_loved(track_object) {
        return `<i id='main-track-loved-${track_object.id}' title='${track_object.id}' class='fa ${(track_object.favorite ? "fa-heart" : "fa-heart-o")}'></i>`
    }

    _get_rating(track_object) {
        let html = "";
        for (let j=1; j<6; j++) {
            html += `<i id='main-track-rating-${track_object.id}-${j}' class='fa ${( j <= track_object.rating ? "fa-star" : "fa-star-o")}' style='font-size:8pt; margin-left:3px'></i>`;
        }
        return html
    }

    set_list(name, queue) {
        this.view_list_order = []
        this.view_list_id_order = []
        this.queue_rows = []
        this.table_rows = {}
        if (queue == undefined) {
            queue = []
        }
        for(let i=0; i<queue.length; i++) {
            let element = {
                id:          queue[i].id,
                available:   queue[i].available,
                color:       queue[i].color,
                loved:       this._get_loved(queue[i]), 
                title:       queue[i].title,
                artist:      queue[i].artist,
                genre:       queue[i].genre,
                last_played: (queue[i].last_played != null) ? moment(queue[i].last_played).format('MM-DD-YYYY') : "",
                play_count:  queue[i].play_count,
                rating:      this._get_rating(queue[i]),
                bpm:         queue[i].bpm,
                duration:    format_nanoseconds(queue[i].stream_length),
            }
            this.queue_rows.push(this.render_row(element))
            this.view_list_order.push(element)
            this.view_list_id_order.push(element.id)
        }
        this.name_dom.innerHTML       = `${name}`
        this.num_tracks_dom.innerHTML = `${this.controller.q_length()} tracks`
        this.duration_dom.innerHTML   = `${format_seconds_long(Math.round(this.controller.duration() / 1000000000))}`
        this.list_cluster.update(this.queue_rows)
    }

    handle_drag_start(e) {
        let x = e.target.closest("tr")
        let track_id = parseInt(x.attributes["data-track-id"].value)
        let track_element = this.controller.get_id(track_id)
        e.dataTransfer.setData("text/plain", JSON.stringify(track_element))
    }

    handle_double_click(e) {
        let x = e.target.closest("tr")
        let track_id = parseInt(x.attributes["data-track-id"].value)
        let track_element = this.controller.get_id(track_id)
        pc.play(track_element)
    }

    handle_click(e) {
        let id = e.target.attributes["id"]
        if (id != undefined) {
            let rating_regex = /main-track-rating-(\d+)-(\d+)/g
            let matches = rating_regex.exec(id.value)
            if (matches != undefined) {
                let track_id = parseInt(matches[1])
                let rating_value = parseInt(matches[2])
                this.set_rating(track_id, rating_value)
                e.preventDefault()
                return;                    
            }
            let loved_regex = /main-track-loved-(\d+)/g
            matches = loved_regex.exec(id.value)
            if (matches != undefined) {
                let track_id = parseInt(matches[1])
                this.toggle_loved(track_id)
                e.preventDefault()
                return;                    
            }
        }
        this.select_row(e)
        focusWindow(this)    
    }


    set_rating(id, value) {
        let track = this.controller.get_id(id)
        if (value == 1 && track.rating == 1) {
            this.controller.set_metadata(track, {rating:0})
        } else {
            this.controller.set_metadata(track, {rating: value})
        }
    }

    toggle_loved(id) {
        let track = this.controller.get_id(id)
        this.controller.set_metadata(track, {favorite: !(track.favorite)})
    }

    select_row(e) {
        let x = e.target.closest("tr")
        let id = parseInt(x.attributes["data-track-id"].value)
        this.controller.select_element(id)
    }


    focus() {
        this.element.classList.add("focus")
    }

    blur() {
        this.element.classList.remove("focus")
    }

    selected_element() {
        return this.controller.selection[0]
    }


    delete_selection() {

    }


    move_down() {
        if (this._selected_row != undefined) {
            let r = this._selected_row[0]
            let i = this.view_list_id_order.indexOf(r.id)
            let n
            if (i != -1) {
                n = (i+1) < this.view_list_id_order.length ? i+1 : this.view_list_id_order.length - 1
            } else {
                n = 0
            }
            this.controller.select_element(this.view_list_id_order[n])
        } else {
            this.controller.select_element(this.view_list_id_order[0])
        }
    }

    move_up() {
        if (this._selected_row != undefined) {
            let r = this._selected_row[0]
            let i = this.view_list_id_order.indexOf(r.id)
            let n
            if (i != -1) {
                n = (i-1) >= 0 ? i-1 : 0
            } else {
                n = 0
            }
            this.controller.select_element(this.view_list_id_order[n])
        } else {
            this.controller.select_element(this.view_list_id_order[this.view_list_id_order.length-1])
        }
    }


    move_last() {
        let e = this.view_list_id_order[this.view_list_id_order.length-1]
        this.ensure_row_visible(e)
        this.controller.select_element(e)
    }


    move_first() {
        let e = this.view_list_id_order[0]
        this.ensure_row_visible(e)
        this.controller.select_element(e)
    }


    move_selection_up() {

    }

    move_selection_down() {

    }

    move_selection_to_top() {

    }


    page_up() {
        let scroller = document.getElementById("main-track-list-scroller")
        let y = scroller.getBoundingClientRect()
        scroller.scrollTop -= y.height
    }

    page_down() {
        let scroller = document.getElementById("main-track-list-scroller")
        let y = scroller.getBoundingClientRect()
        scroller.scrollTop += y.height
    }

    add_selection_to_queue() {
        if (this._selected_row != undefined) {
            let r = this._selected_row[0]
            this.queue_controller.append(r)
        }
    }

    add_selection_to_shortlist() {
        this._selected_row.forEach((x) => {
            this.shortlist_controller.add(x)
        })
    }

    add_selection_to_unavailable() {
        this._selected_row.forEach((x) => {
            this.unavailable_controller.add(x)
        })
    }

    remove_selection_from_unavailable() {

    }

    update_element(x) {
        let row = this.table_rows[x.id]
        let rating_cell = document.getElementById(`track-rating-${x.id}`)
        rating_cell.innerHTML = this._get_rating(x)
        let loved_cell = document.getElementById(`track-loved-${x.id}`)
        loved_cell.innerHTML = this._get_loved(x)
        let color_cell = document.getElementById(`track-color-${x.id}`)
        color_cell.style.backgroundColor = x.color
        let row_dom = document.getElementById(`track-row-${x.id}`)
        row_dom.style.color = x.color
    }


    ensure_row_visible(x) {
        let row = this.table_rows[x.id]
        let scroller = document.getElementById("main-track-list-scroller")
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

    update_selection(selection) {
        if (this._selected_row != undefined) {
            this._selected_row.forEach((x) => {
                if (this.table_rows[x.id]) {
                    this.table_rows[x.id].classList.remove("selected")}
                })
        }
        this._selected_row = selection
        this._selected_row.forEach((x) => {
            this.ensure_row_visible(x)
            if (this.table_rows[x.id] != undefined) {
                this.table_rows[x.id].classList.add("selected")
            }
        })
    }


    filter_list (text) {
        let i = 0;
        let search_tokens = text.split(' ')
        let search_f = [];
        for (i=0; i<search_tokens.length; i++) {
            let token = search_tokens[i].toLowerCase();
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
        let queue_rows = []
        this.view_list_id_order = []
        this.view_list_order.forEach((k) => {
            if (filter[k.id]) {
                queue_rows.push(this.render_row(k))
                this.view_list_id_order.push(k.id)

            }
        })

        this.list_cluster.update(queue_rows)
    };
}
