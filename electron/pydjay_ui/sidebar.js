DB = new DataProvider()


function display_track_list(list_name, list_elements) {
    // $$('display_list').clearAll()
    // if (list_elements.length > 0) {
    //     for(i=0; i<list_elements.length; i++){
    //         if (!list_elements[i].available){
    //             list_elements[i].$css = "unavailable_track";
    //         }
    //     }
    // }
    main_track_table.set_track_list(list_name, list_elements)
    // $$('display_list').define('data', list_elements);
    // $$('display_list').refresh();
    // $$('playlist_name').define('label', list_name);
    // $$('playlist_name').refresh();
    webix.UIManager.setFocus($$(main_track_table.track_list));
    if (list_elements.length > 0) {
        $$(main_track_table.track_list).select($$(main_track_table.track_list).getFirstId());
    }
}

function display_all_songs(){
    return function () {
        DB.get_all_tracks(
            function (result) {
                display_track_list('All Songs', result);
            }
        );
    }
}

function display_short_listed_songs(){
    return function () {
        DB.get_shortlisted_tracks(
            function (result) {
                display_track_list('Short List', result);
            }
        )
    }
}

function display_unavailable_songs(){
    return function () {
        DB.get_unavailable_tracks(
            function (result) {
                display_track_list('Unavailable Tracks', result);
            }
        )
    }
}

function display_never_played_songs(){
    return function () {
        DB.get_never_played_tracks(
            function (result) {
                display_track_list('Never Played Tracks', result);
            }
        )
    }
}

function display_suggestions(){
    return function () {
        DB.get_suggested_tracks(
            function (result) {
                display_track_list('Suggested Tracks', result);
            }
        )
    }
}


function display_played_songs(){
    return function () {
        DB.get_played_tracks(
            function (result) {
                display_track_list('Played Tracks', result);
            }
        )
    }
}

function display_session(id){
    return function () {
        DB.get_session_tracks(id, 
            function (result) {
                $QUERY(
                    `SELECT event_name, start_date FROM sessions WHERE id=${id}`,
                    function (r) {
                        display_track_list(`${r[0].event_name} - ${webix.Date.dateToStr("%Y-%m-%d")(r[0].start_date)}`, result);
                    }
                );    
            }
        )
    }
}

function display_tag(id){
    return function () {
        DB.get_playlist_tracks(id,
            function (result) {
                //console.log(result)
                $QUERY(
                    `SELECT name FROM playlists WHERE id=${id}`,
                    function (r) {
                        display_track_list(`${r[0].name}`, result);
                    }
                );                    
            }
        )
    }
}

function genre_template(element) {
    var cover_source = null;
    if (element.cover == null) {
        cover_source = "../resources/images/default_album_cover.png"
    } else {
        cover_source = `${element.image_root}/${element.cover}`
    }
    return `<div>
                <i class="ui left floated list icon"></i>
                <div class="genre_element_name">${element.id}</div>
                <div class="genre_element_count">${element.count}</div>
            </div>`
}

function session_template(element) {
    var cover_source = null;
    if (element.cover == null) {
        cover_source = "../resources/images/default_album_cover.png"
    } else {
        cover_source = `${element.image_root}/${element.cover}`
    }
    return `<div class="webix_icon fa-list" style='float:left;transform: translateY(40%); font-size:13px'></div>
            <div class="session_element_name">${element.name}</div>
            <div class="session_element_date">${webix.Date.dateToStr("%Y-%m-%d")(element.date)}</div>
            <div class="session_element_count">${element.count}</div>`
}

function track_list_template(element) {
    var cover_source = null;
    if (element.cover == null) {
        cover_source = "../resources/images/default_album_cover.png"
    } else {
        cover_source = `${element.image_root}/${element.cover}`
    }
    return `<div class="webix_icon fa-list" style='float:left;transform: translateY(40%); font-size:13px'></div>
            <div class="tag_element_name">${element.name}</div>
            <div class="tag_element_count">${element.count}</div>
            <!-- <div style="float:right; position:relative; top:0%; transform: translateY(-80%); height:15px; width:20px; background-color:${element.color}"> -->
            </div>`
}

var sidebar_template = {
    width:350,
    css: {
        'background-color':'#3f3f3f',
        'padding':'0px',
        'margin':'0px',
        "height":"100% !important"
    },
    rows: [
        {
            view: 'label',
            label: '<b>LIBRARY</b>',
            height:30,
            css:{
                'background-color': '#303030',
                "padding-left": "10px"
            }
        },

        { 
            gravity:1,

            rows: [
                {
                    id: 'show_all_songs',
                    view:'button',
                    label:'<b style="font-size:12px">ALL SONGS</b>',
                    type:'icon',
                    icon:'database',
                    click:display_all_songs()
                },
                {
                    id: 'show_suggestions',
                    view:'button',
                    label:'<b style="font-size:12px">SUGGESTIONS</b>',
                    type:'icon',
                    icon:'calendar',
                    click:display_suggestions(),
                    //hotkey:'ctrl+shift+s'
                },
                {
                    id: 'show_short_list',
                    view:'button',
                    label:'<b style="font-size:12px">SHORT LIST</b>',
                    type:'icon',
                    icon:'calendar',
                    click:display_short_listed_songs(),
                    hotkey:'ctrl+shift+s'
                },
                {
                    id: 'show_played',
                    view:'button',
                    label:'<b style="font-size:12px">PLAYED SONGS</b>',
                    type:'icon',
                    icon:'calendar',
                    click:display_played_songs(),
                    hotkey:'ctrl+shift+p'
                },
                {
                    id: 'show_never_played',
                    view:'button',
                    label:'<b style="font-size:12px">NEVER PLAYED</b>',
                    type:'icon',
                    icon:'calendar',
                    click:display_never_played_songs(),
                    hotkey:'ctrl+shift+n'
                },
                {
                    id: 'show_unavailable',
                    view:'button',
                    label:'<b style="font-size:12px">UNAVAILABLE</b>',
                    type:'icon',
                    icon:'close',
                    click:display_unavailable_songs(),
                    hotkey:'ctrl+shift+u'
                }
            ]
        },
        {
            view: 'label',
            label: '<b>GROUPS</b>',
            height:30,
            css:{
                'background-color': '#303030',
                "padding-left": "10px"
            }
        },
        {
            gravity:1,
            rows:[
                {
                    id:"playlist-list",
                    view:"list",
                    template: track_list_template,
                    select:true,
                    scroll:"y",
                    type: {
                        height:25
                    },

                    on: {
                        onItemClick: function(id, e, node){
                            display_tag(id)();
                        }
        
                    }
                },
                {
                    cols:[
                        {
                            view:'button',
                            type:'icon',
                            icon: 'plus',
                            width:40,
                            click: function () {
                                win = new NewPlaylist()
                                win.onHide = function () {
                                    let list_id = "playlist-list"
                                    DB.get_group_list(
                                        function (result_list) {
                                            $$(list_id).clearAll()
                                            $$(list_id).define('data', result_list);
                                            $$(list_id).refresh() 
                                        }
                                    )
                                }
                                win.show()
                            }
                        },
                        {},
                        {
                            view:'button',
                            type:'icon',
                            icon: 'list',
                            width:40,
                            click: function () {
                                let selected_id = $$("playlist-list").getSelectedItem().id
                                win = new SetAsShortlist(selected_id) 
                                win.show()
                            }
                        },
                        {
                            view:'button',
                            type:'icon',
                            icon: 'edit',
                            width:40,
                            click: function () {
                                let selected_id = $$("playlist-list").getSelectedItem().id
                                win = new PlaylistEditor(selected_id) 
                                win.onHide = function () {
                                    i = $$("playlist-list").getItem(selected_id)
                                    let list_id = "playlist-list"
                                    DB.get_group_list(
                                        function (result_list) {
                                            for (i=0; i<result_list.length; i++) {
                                                j = $$(list_id).getItem(i)
                                                i.count = result_list[i].count
                                                $$(list_id).updateItem(i, j)                                                                
                                            }
                                        }
                                    )
                                }
                                win.show()
                            }
                        },
                        {
                            view:'button',
                            type:'icon',
                            icon: 'copy',
                            width:40,
                            click: function () {
                                win = new PlaylistDuplicator($$("playlist-list").getSelectedItem().id)
                                win.onHide = function () {
                                    let list_id = "playlist-list"
                                    DB.get_group_list(
                                        function (result_list) {
                                            $$(list_id).clearAll()
                                            $$(list_id).define('data', result_list);
                                            $$(list_id).refresh() 
                                        }
                                    )
                                }
                                win.show()
                            }
                        },
                        {
                            view:'button',
                            type:'icon',
                            icon: 'minus',
                            width:40,
                            click: function () {
                                win = new DeletePlaylist($$("playlist-list").getSelectedItem().id)
                                win.onHide = function () {
                                    let list_id = "playlist-list"
                                    DB.get_group_list(
                                        function (result_list) {
                                            $$(list_id).clearAll()
                                            $$(list_id).define('data', result_list);
                                            $$(list_id).refresh() 
                                        }
                                    )
                                }
                                win.show()
                            }
                        }

                    ]
                }
            ]
        },
        {
            view: 'label',
            label: '<b>SESSIONS</b>',
            height:30,
            css:{
                'background-color': '#303030',
                "padding-left": "10px"
            }

        },

        { 
            id: "sessions_item",
            view:'list',
            id:"sessions-list",
            select:true,
            template: session_template,
            type: {
                height:25,
            },
            on: {
                onItemClick: function(id, e, node){
                    display_session(id)();
                }

            }
        }
    ]
}