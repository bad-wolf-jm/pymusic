const { ipcRenderer } = require('electron');
const Clusterize = require("clusterize.js")

function rgb2hex(rgb) {
    rgb = rgb.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);
    function hex(x) {
        return ("0" + parseInt(x).toString(16)).slice(-2);
    }
    return "#" + hex(rgb[1]) + hex(rgb[2]) + hex(rgb[3]);
}
class BaseTrackListView extends EventDispatcher {
    constructor(element, list_scroller) {
        super()
        this.element = element
        this.scroller = list_scroller
        this.controller = undefined
        this.table = undefined
        this.queue_rows = undefined
        this.ignore_unavailable = false
        this.model_order = false
        this._dimmed = {}
        this.rowHeight = 30
    }

    async getEventTrackElement(e) {
        let x = e.target.closest("tr")
        let track_id = x.attributes["data-track-id"].value
        return await this.controller.getElementById(track_id)
    }

    getEventTrackId(e) {
        let x = e.target.closest("tr")
        return x.attributes["data-track-id"].value
    }

    convert_track(track_element) {
        let { metadata, stats, track } = track_element
        return {
            id: track_element._id,
            color: metadata.color,
            title: metadata.title,
            artist: metadata.artist,
            album: metadata.album,
            genre: metadata.genre,
            last_played: (stats.last_played != null) ? moment(stats.last_played).format('MM-DD-YYYY') : "",
            play_count: (stats.play_count != undefined) ? stats.play_count : "",
            duration: track.stream_end - track.stream_start,
            bpm: track.bpm,
            loved: stats.loved,
            rating: stats.rating
        }
    }

    async set_list(name, list_elements) {
        if (list_elements == undefined) {
            list_elements = []
        }

        if (!this.model_order) {
            list_elements.sort(this.compare_tracks)
        }

        this.view_list_order = list_elements.map((e) => {return this.convert_track(e)})
        this.view_list_id_order = list_elements.map((e) => {return e._id})
        this.update_view(this.view_list_order)
        this.update(name, this.view_list_order, await this.controller.q_length(), await this.controller.duration())
    }

    set_controller(controller) {
        this.controller = controller
        this.controller.addView(this)
        this.controller.on("content-changed", this.set_list.bind(this))
        this.controller.on("selection-changed", this.update_selection.bind(this))
        this.controller.on("element-updated", this.update_element.bind(this))
        this.controller.on("metadata-changed", this.update_element.bind(this))
    }

    setDimmedRows(track_id_list) {
        if (this.ignore_unavailable) {
            return;
        }
        let track_set = {}
        track_id_list.forEach((t) => {track_set[t] = true})
        Object.keys(this._dimmed).forEach((t) => {
            let r = this.getTrackTableElement(t)
            r && r.classList.remove("unavailable")
        })
        Object.keys(track_set).forEach((t) => {
            let r = this.getTrackTableElement(t)
            r && r.classList.add("unavailable")
        })
        this._dimmed = track_set
    }

    compare_tracks(a, b) {
        let x = a.metadata.title.toLowerCase();
        let y = b.metadata.title.toLowerCase();
        if (x < y) {return -1;}
        if (x > y) {return 1;}
        return 0;        
    }    

    handle_drag_start(e) {
        let track_id = this.getEventTrackId(e)
        e.dataTransfer.setData("text/plain", track_id)
    }

    async handle_double_click(e) {
        let track_element = await this.getEventTrackElement(e)
        this.dispatch("prelisten-request", track_element)
    }

    handle_click(e) {
        let id = e.target.attributes["id"]
        if (id != undefined) {
            let rating_regex = /main-track-rating-([a-zA-Z0-9]+)-(\d+)/g
            let matches = rating_regex.exec(id.value)
            if (matches != undefined) {
                let track_id = matches[1]
                let rating_value = parseInt(matches[2])
                this.set_rating(track_id, rating_value)
                e.preventDefault()
                return;
            }
            let loved_regex = /main-track-loved-([a-zA-Z0-9]+)/g
            matches = loved_regex.exec(id.value)
            if (matches != undefined) {
                let track_id = matches[1]
                this.toggle_loved(track_id)
                e.preventDefault()
                return;
            }
        }
        this.select_row(e)
        focusWindow(this)
    }


    async set_rating(id, value) {
        let track = await this.controller.getElementById(id)
        if (value == 1 && track.rating == 1) {
            this.controller.setTrackMetadata(track, {"stats.rating": 0})
        } else {
            this.controller.setTrackMetadata(track, {"stats.rating": value})
        }
    }

    async toggle_loved(id) {
        let track = await this.controller.getElementById(id)
        this.controller.setTrackMetadata(track, {"stats.loved": !(track.stats.loved)})
    }

    select_row(e) {
        this.controller.select_element(this.getEventTrackId(e))
    }

    focus() {
        this.element.classList.add("focus")
    }

    blur() {
        if (this.edit_mode) {
            this.cancel_edit()
        }
        this.element.classList.remove("focus")
    }

    selected_element() {
        return this.controller.selection[0]
    }


    delete_selection() {

    }

    _make_edit_input_field(name, id, old_value) {
        return `<input id="main-track-list-edit-${name}-${id}" type="text" class="new-playlist" value="${old_value}">`
    }

    cancel_edit() {
        this.edit_mode = false
        this.rowEditCancelRequest(r)
        this.edit_row = undefined
    }

    _keypress (e) {
        if (e.key == "Escape") {
            this.cancel_edit()
        } else if (e.key == "Enter") {
            this.save_edit()
        } else if (e.key == "Alt") {
            if (this.edit_bpm != undefined) {
                let t = this.edit_bpm.tap()
                let bpm = Math.round(t.avg)
                if (!isNaN(bpm)) {
                    document.getElementById(`main-track-list-edit-bpm-${this.edit_row._id}`).value = bpm
                }
            }
        } else {

        }
    }

    begin_edit() {
        if (this._selected_row != undefined) {
            this.edit_mode = true
            let r = this._selected_row[0]
            this.edit_row = r
            this.rowEditRequest()
        }
    }

    save_edit() {
        if ((this._selected_row != undefined) && this.edit_mode) {
            // if (this.edit_mode) {
            this.edit_mode = false
            let r = this._selected_row[0]
            let new_values = this.rowEditGSetValues(r)
            if (new_values != undefined) {W
                this.controller.setTrackMetadata(r, {
                    "metadata.title": new_values.title,
                    "metadata.artist": new_values.artist,
                    "metadata.album": new_values.album,
                    "metadata.genre": new_values.genre,
                    "stats.bpm": new_values.bpm
                })
            }
            // }
        }
    }


    move_selection(amount) {
        //console.log(abount)
        if (this.edit_mode) {
            this.cancel_edit()
        }
        this.d = 1
        if (this._selected_row != undefined) {
            let r = this._selected_row[0]
            let i = this.view_list_id_order.indexOf(r._id)
            let n
            if (i != -1) {
                n = i + amount
                n = Math.max(n, 0)
                n = Math.min(n, this.view_list_id_order.length - 1)
            } else {
                n = 0
            }
            this.controller.select_element(this.view_list_id_order[n])
        } else {
            this.controller.select_element(this.view_list_id_order[0])
        }

    }

    move_down() {
        this.move_selection(1)
    }

    move_up() {
        this.move_selection(-1)
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

    set_selected_rating(rating) {
        if (this._selected_row != undefined) {
            let r = this._selected_row[0]
            this.controller.set_metadata(r, {rating:rating})
        }
    }

    toggle_selected_loved() {
        if (this._selected_row != undefined) {
            let r = this._selected_row[0]
            this.controller.set_metadata(r, {favorite: !(r.favorite)})
        }
    }


    move_selection_up() {

    }

    move_selection_down() {

    }

    move_selection_to_top() {

    }


    page_up() {
        let y = this.scroller.getBoundingClientRect()
        scroller.scrollTop -= y.height
    }

    page_down() {
        let y = this.scroller.getBoundingClientRect()
        scroller.scrollTop += y.height
    }

    add_selection_to_queue() {
        if (this._selected_row != undefined) {
            let r = this._selected_row[0]
            Q.add_element(r)
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

    getTrackTableElement(trackId) {
        console.log(trackId)
    }


    selectTrackTableElement(track) {
        let e = this.getTrackTableElement(track._id)      
        if (e != undefined) {
            e.classList.add("selected")
        }
    }

    unselectTrackTableElement(track) {
        let e = this.getTrackTableElement(track._id)      
        if (e != undefined) {
            e.classList.remove("selected")
        }
    }

    ensure_row_visible(x, direction) {
        let row = this.getTrackTableElement(x._id)
        let scrollerRect = this.scroller.getBoundingClientRect()
        if (row == undefined) {
            this.scroller.scrollTop += (this.d * this.rowHeight)
        } else {
            let rowRect = row.getBoundingClientRect()
            let offsetTop = (rowRect.y - scrollerRect.y)
            let offsetBottom = offsetTop + rowRect.height
            let y = this.scroller.getBoundingClientRect()
            if (offsetBottom >= y.height) {
                this.scroller.scrollTop += (offsetBottom - y.height)
            } else if (offsetTop < 0) {
                this.scroller.scrollTop += (offsetTop)
            }
        }
    }

    update_selection(selection) {
        if (this._selected_row != undefined) {
            this._selected_row.forEach((x) => {
                this.unselectTrackTableElement(x)
            })
        }
        this._selected_row = selection
        this._selected_row.forEach((x) => {
            this.ensure_row_visible(x)
            this.selectTrackTableElement(x)
        })
    }


    async filter_list (text) {
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
                                return (obj.stats.bpm >= x);
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
                                return (obj.stats.bpm < x*1.2) && (obj.stats.bpm > x*0.9) ;
                            }
                        )
                    } else {
                        search_f.push( (x) => {return true} )
                    }
                } else {
                    search_f.push(
                        function (x) {
                            let fields = [x.metadata.title, x.metadata.artist, x.metadata.genre, `@rat=${x.stats.rating}`, '@bpm']
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
        let filter = await this.controller.filter_ids((obj) => {
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

        return queue_rows

        //this.list_cluster.update(queue_rows)
    };
}