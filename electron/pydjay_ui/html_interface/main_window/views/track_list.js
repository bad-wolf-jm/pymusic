class TrackListView extends ClusteredListView {
    constructor(dom_ids, queue_controller, shortlist_controller, unavailable_controller) {
        super(document.getElementById("main-list"), document.getElementById("main-track-list-scroller"))

        this.dom_id = dom_ids.list

        this.prevWidth = [];

        document.getElementById("main-track-list-scroller").addEventListener("scroll", (e) => {
            if (this.color_chooser != undefined) {
                this.color_chooser.close()
                this.color_chooser = undefined
            }
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
                    [].forEach.call(elements, (e) => {
                        let track_id = e.attributes["data-track-id"].value
                        this.table_rows[track_id] = e
                    });
                    this.fitHeaderColumns()
                    this.setDimmedRows(this._dimmed.getList())

                    elements = document.querySelectorAll('.show-color-picker');
                    [].forEach.call(elements, (e) => {
                        e.addEventListener("click", (ev) => {
                            let track_id = e.attributes['data-track-id'].value
                            let cp = document.getElementById("main-track-list-color-chooser")
                            let button_rect = e.getBoundingClientRect()
                            let scroller = document.getElementById("main-track-list-scroller")
                            let scroller_rect = scroller.getBoundingClientRect()
                            let button_offset = (button_rect.top - scroller_rect.top)

                            if (this.color_chooser != undefined) {
                                this.color_chooser.close()
                                this.color_chooser = undefined
                            } else {
                                this.color_chooser = new ColorPicker(document.getElementsByTagName("body")[0], {
                                    cancel: () => {
                                        this.color_chooser.close()
                                        this.color_chooser = undefined
                                    },
                                    chooseColor: async (color) => {
                                        let track = await this.controller.getElementById(track_id)
                                        this.controller.setTrackMetadata(track, {'metadata.color': color})                                
                                        this.color_chooser.close()
                                        this.color_chooser = undefined
                                    }
                                })

                                if (button_offset + 150 > scroller_rect.height) {
                                    this.color_chooser.open(e, "above")
                                } else {
                                    this.color_chooser.open(e)
                                }
                                ev.preventDefault()
                            }
                        })
                    })
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

        $('#main-track-list-body').on('contextmenu', async (e) => {
            e.preventDefault()
            this.select_row(e)
            let x = e.target.closest(".track-entry")
            let track_id = (x.attributes["data-track-id"].value)
            let track_element = await this.controller.getElementById(track_id)
            this.context_menu_element = track_element
            this.menu.popup({window: remote.getCurrentWindow()})
        });

        document.getElementById("track-list-header").innerHTML = this.render_header({
            id:          "NONE",
            loved:       "<b><i class='fa fa-heart' style='font-size: 12px'/></b>",
            title:       "Title",
            artist:      "Artist",
            album:       "Album",
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
            pc.stop()
            view.set_track(this.context_menu_element)
            document.getElementById("track-edit-dialog").showModal()
        }}))
        this.menu.append(new MenuItem({type: 'separator'}))
        this.menu.append(new MenuItem({label: 'Shortlist', click: () => {
            let T = this.context_menu_element
            this.shortlist_controller.append(T)

        }}))

        this.menu.append(new MenuItem({label: 'Marked as played', click: () => {
            let T = this.context_menu_element
            this.unavailable_controller.append(T)
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
            <${element} id='track-title-${track.id}' style="max-width:110px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${track.title}</${element}>
            <${element} id='track-artist-${track.id}' style="max-width:90px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${track.artist}</${element}>
            <${element} id='track-album-${track.id}'style="max-width:90px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${track.album}</${element}>
            <${element} id='track-genre-${track.id}' style="max-width:40px;  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${track.genre}</${element}>
            <${element} id='track-play-count-${track.id}' style="text-align:right; width:25px; padding-right:9px">${track.play_count}</${element}>
            <${element} id='track-last-played-${track.id}' style="width:75px">${track.last_played}</${element}>
            <${element} id='track-rating-${track.id}' style="width:25px">${track.rating}</${element}>
            <${element} id='track-bpm-${track.id}' style="width:30px; text-align:right; padding-right:5px">${track.bpm}</${element}>
            <${element} id='track-duration-${track.id}'style="width:45px; text-align:right">${track.duration}</${element}>
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

    _get_loved(track_object) {
        return `<i id='main-track-loved-${track_object.id}' title='${track_object.id}' class='fa ${(track_object.loved ? "fa-heart" : "fa-heart-o")}'></i>`
    }

    _get_rating(track_object) {
        let html = "";
        for (let j=1; j<6; j++) {
            html += `<i id='main-track-rating-${track_object.id}-${j}' class='fa ${( j <= track_object.rating ? "fa-star" : "fa-star-o")}' style='font-size:8pt; margin-left:3px'></i>`;
        }
        return html
    }

    update(name, list, length, duration) {
        this.name_dom.innerHTML = `${name}`
        this.num_tracks_dom.innerHTML = `${length} tracks`
        this.duration_dom.innerHTML = `${format_seconds_long(duration / 1000)}`
    }

    update_view(list) {
        this.queue_rows = list.map((e) => {
            e.rating = this._get_rating(e)
            e.loved = this._get_loved(e)
            e.duration = format_nanoseconds(e.duration)
            return this.render_row(e)
        })
        this.list_cluster.update(this.queue_rows)
    }

    handle_drag_start(e) {
        let x = e.target.closest("tr")
        let track_id = x.attributes["data-track-id"].value
        let track_element = track_id 
        e.dataTransfer.setData("text/plain", track_element)
    }

    async handle_double_click(e) {
        let x = e.target.closest("tr")
        let track_id = x.attributes["data-track-id"].value
        let track_element = await this.controller.getElementById(track_id)
        // console.log(track_element)
        pc.play(track_element)
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

    delete_selection() {

    }

    _make_edit_input_field(name, id, old_value) {
        return `<input id="main-track-list-edit-${name}-${id}" type="text" class="new-playlist" value="${old_value}">`
    }

    cancel_edit() {
        this.edit_mode = false
        let r = this.edit_row
        document.getElementById(`track-title-${r._id}`).innerHTML = this.edit_row.metadata.title
        document.getElementById(`track-artist-${r._id}`).innerHTML = this.edit_row.metadata.artist 
        document.getElementById(`track-album-${r._id}`).innerHTML = this.edit_row.metadata.album 
        document.getElementById(`track-genre-${r._id}`).innerHTML = this.edit_row.metadata.genre
        document.getElementById(`track-bpm-${r._id}`).innerHTML = this.edit_row.track.bpm
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
            this.edit_bpm = new BPM()
            document.getElementById(`track-title-${r._id}`).innerHTML = this._make_edit_input_field("title", r._id, r.metadata.title)
            document.getElementById(`main-track-list-edit-title-${r._id}`).addEventListener("keyup", (e) => {
                this._keypress(e)
            })

            document.getElementById(`track-artist-${r._id}`).innerHTML = this._make_edit_input_field("artist", r._id, r.metadata.artist)
            document.getElementById(`main-track-list-edit-artist-${r._id}`).addEventListener("keyup", (e) => {
                this._keypress(e)
            })

            document.getElementById(`track-album-${r._id}`).innerHTML = this._make_edit_input_field("album", r._id, r.metadata.album)
            document.getElementById(`main-track-list-edit-album-${r._id}`).addEventListener("keyup", (e) => {
                this._keypress(e)
            })


            document.getElementById(`track-genre-${r._id}`).innerHTML = this._make_edit_input_field("genre", r._id, r.metadata.genre)
            document.getElementById(`main-track-list-edit-genre-${r._id}`).addEventListener("keyup", (e) => {
                this._keypress(e)
            })

            document.getElementById(`track-bpm-${r._id}`).innerHTML = this._make_edit_input_field("bpm", r._id, r.track.bpm)
            document.getElementById(`main-track-list-edit-bpm-${r._id}`).addEventListener("keyup", (e) => {
                this._keypress(e)
            })

            document.getElementById(`main-track-list-edit-title-${r._id}`).focus()
        }
    }

    save_edit() {
        if (this._selected_row != undefined) {
            if (this.edit_mode) {
                this.edit_mode = false
                let r = this._selected_row[0]
                let title = document.getElementById(`main-track-list-edit-title-${r._id}`).value
                let artist = document.getElementById(`main-track-list-edit-artist-${r._id}`).value
                let album = document.getElementById(`main-track-list-edit-album-${r._id}`).value
                let genre = document.getElementById(`main-track-list-edit-genre-${r._id}`).value
                let bpm = document.getElementById(`main-track-list-edit-bpm-${r._id}`).value
                this.controller.setTrackMetadata(r, {
                    "metadata.title":title,
                    "metadata.artist":artist,
                    "metadata.album":album,
                    "metadata.genre":genre,
                    "stats.bpm":bpm
                })
            }
        }
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

    add_selection_to_queue() {
        if (this._selected_row != undefined) {
            let r = this._selected_row[0]
            Q.add_element(r)
        }
    }

    add_selection_to_shortlist() {
        this._selected_row.forEach((x) => {
            this.shortlist_controller.append(x)
        })
    }

    add_selection_to_unavailable() {
        this._selected_row.forEach((x) => {
            this.unavailable_controller.append(x)
        })
    }

    remove_selection_from_unavailable() {
        this._selected_row.forEach((x) => {
            this.unavailable_controller.remove(x)
        })
    }

    updateCell(id, new_value) {
        let cell = document.getElementById(id)
        if (cell) {
            cell.innerHTML = new_value
        } 
    }

    updateCellStyle(id, style, new_value) {
        let cell = document.getElementById(id)
        if (cell) {
            cell.style[style] = new_value
        } 
    }

    update_element(x) {
        let row = this.table_rows[x._id]
        x = this.convert_track(x)
        this.updateCell(`track-rating-${x.id}`, this._get_rating(x))
        this.updateCell(`track-loved-${x.id}`, this._get_loved(x))
        this.updateCell(`track-title-${x.id}`, x.title)
        this.updateCell(`track-artist-${x.id}`, x.artist)
        this.updateCell(`track-genre-${x.id}`, x.genre)
        this.updateCell(`track-bpm-${x.id}`, x.bpm)
        this.updateCell(`track-play-count-${x.id}`, x.play_count)
        this.updateCell(`track-last-played-${x.id}`, x.last_played)
        this.updateCell(`track-duration-${x.id}`, `${format_nanoseconds(x.duration)}`)
        this.updateCellStyle(`track-color-${x.id}`, 'backgroundColor', x.color)
        this.updateCellStyle(`track-row-${x.id}`, 'color', x.color)
    }

    getTrackTableElement(trackId) {
        return this.table_rows[trackId]
    }

    async filter_list (text) {
        this.list_cluster.update(await super.filter_list(text))
    };
}
