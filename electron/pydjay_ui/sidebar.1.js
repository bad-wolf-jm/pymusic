

function display_track_list(list_name, list_elements) {
    $$('display_list').clearAll()
    if (list_elements.length > 0) {
        for(i=0; i<list_elements.length; i++){
            if (!list_elements[i].available){
                list_elements[i].$css = "unavailable_track";
            }
        }
    }
    $$('display_list').define('data', list_elements);
    $$('display_list').refresh();
    $$('playlist_name').define('label', list_name);
    $$('playlist_name').refresh();
    webix.UIManager.setFocus($$('display_list'));
    if (list_elements.length > 0) {
        $$('display_list').select($$('display_list').getFirstId());
    }
}

var display_list_fields = 'id, favorite, disabled as enabled, title, artist, album, genre, grouping, rating, bpm, stream_length, count(session_tracks.track_id) as play_count,  MAX(session_tracks.start_time) AS last_played';

function display_all_songs(){
   return function () {
       var sql =`SELECT availability.track_id IS NULL as available, ${display_list_fields} FROM tracks LEFT JOIN session_tracks
                 ON tracks.id = session_tracks.track_id LEFT JOIN ((select track_id from unavailable_tracks) UNION
                 (select track_id from session_queue)) availability ON availability.track_id=tracks.id GROUP BY id ORDER BY title`;
       db_connection.query(sql, function (err, result) {
           if (err) throw err;
           display_track_list('All Songs', result);
           $$('main_menu_popup').hide();
         });
   }
}


function display_short_listed_songs(){
    return function () {
       var sql =`SELECT availability.track_id IS NULL as available, ${display_list_fields}
                 FROM tracks LEFT JOIN session_tracks ON tracks.id = session_tracks.track_id
                 JOIN short_listed_tracks ON tracks.id=short_listed_tracks.track_id LEFT JOIN ((select track_id from unavailable_tracks) UNION
                 (select track_id from session_queue)) availability ON availability.track_id=tracks.id GROUP BY id ORDER BY title`;
       db_connection.query(sql, function (err, result) {
           if (err) throw err;
           display_track_list('Short List', result);
           $$('main_menu_popup').hide();
        }
    );}
}

function display_unavailable_songs(){
    return function () {
       var sql =`SELECT availability.track_id IS NULL as available, ${display_list_fields} FROM tracks LEFT JOIN session_tracks ON
                 tracks.id = session_tracks.track_id JOIN unavailable_tracks ON tracks.id=unavailable_tracks.track_id LEFT JOIN
                 (select track_id from session_queue) availability ON availability.track_id=tracks.id GROUP BY id ORDER BY title`;
       db_connection.query(sql, function (err, result) {
           if (err) throw err;
           display_track_list('Unavailable Tracks', result);
           $$('main_menu_popup').hide();
        }
    );}
}


function display_never_played_songs(){
    return function () {
       var sql =`SELECT * FROM (SELECT availability.track_id IS NULL as available, ${display_list_fields} FROM tracks LEFT JOIN session_tracks ON
                 tracks.id = session_tracks.track_id LEFT JOIN
                 (select track_id from session_queue) availability ON availability.track_id=tracks.id GROUP BY id ORDER BY title) q WHERE q.play_count = 0`;
       db_connection.query(sql, function (err, result) {
           if (err) throw err;
           display_track_list('NEVER PLAYED', result);
           $$('main_menu_popup').hide();
        }
    );}
}


function display_played_songs(){
    return function () {
       var sql =`SELECT * FROM (SELECT availability.track_id IS NULL as available, ${display_list_fields} FROM tracks LEFT JOIN session_tracks ON
                 tracks.id = session_tracks.track_id LEFT JOIN
                 (select track_id from session_queue) availability ON availability.track_id=tracks.id GROUP BY id ORDER BY title) q WHERE q.play_count != 0`;
       db_connection.query(sql, function (err, result) {
           if (err) throw err;
           display_track_list('PLAYED SONGS', result);
           $$('main_menu_popup').hide();
        }
    );}
}


function display_genre(name){
    return function () {
        var sql = `SELECT availability.track_id IS NULL as available, ${display_list_fields} FROM tracks LEFT JOIN session_tracks ON
                   tracks.id = session_tracks.track_id LEFT JOIN ((select track_id from unavailable_tracks) UNION
                   (select track_id from session_queue)) availability ON availability.track_id=tracks.id WHERE genre="${name}" GROUP BY id ORDER BY title`;
        db_connection.query(sql, function (err, result) {
            if (err) throw err;
            display_track_list(name, result);
            //$$('main_menu_popup').hide();
          });
    }
}


function display_session(id){
    return function () {
        var sql = `SELECT availability.track_id IS NULL as available,  id, favorite, disabled as enabled, title, artist,
                   album, genre, rating, bpm, stream_length, foo.play_count, max_play_times.time as last_played
                   FROM session_tracks JOIN
                   (SELECT * FROM tracks JOIN (SELECT id as id_2, count(session_tracks.track_id) as play_count
                   FROM tracks JOIN session_tracks ON tracks.id = session_tracks.track_id GROUP BY id) play_counts ON
                   tracks.id=play_counts.id_2) foo ON session_tracks.track_id=foo.id LEFT JOIN
                   ((select track_id from unavailable_tracks) UNION (select track_id from session_queue)) availability ON
                   availability.track_id=session_tracks.track_id LEFT JOIN (SELECT track_id, MAX(start_time) AS time
                   FROM session_tracks GROUP BY track_id) max_play_times ON id = max_play_times.track_id
                   WHERE session_tracks.session_id=${id}`;
        db_connection.query(sql, function (err, result) {
            if (err) throw err;
            db_connection.query(
                `SELECT event_name, start_date FROM sessions WHERE id=${id}`,
                function (e, r) {
                    display_track_list(`${r[0].event_name} - ${webix.Date.dateToStr("%Y-%m-%d")(r[0].start_date)}`, result);
                    //$$('main_menu_popup').hide();
                }
            );
          });
    }
}

function display_tag(id){
    return function () {
        var sql = `SELECT availability.track_id IS NULL as available, id, favorite, disabled as enabled, title, artist,
                   album, genre, rating, bpm, stream_length, foo.play_count, max_play_times.time as last_played FROM playlist_tracks JOIN
                   (SELECT * FROM tracks JOIN (SELECT id as id_2, count(session_tracks.track_id) as play_count
                   FROM tracks LEFT JOIN session_tracks ON tracks.id = session_tracks.track_id GROUP BY id) play_counts
                   ON tracks.id=play_counts.id_2) foo ON playlist_tracks.track_id=foo.id LEFT JOIN
                   ((select track_id from unavailable_tracks) UNION (select track_id from session_queue)) availability
                   ON availability.track_id=playlist_tracks.track_id LEFT JOIN (SELECT track_id, MAX(start_time) AS time
                   FROM session_tracks GROUP BY track_id) max_play_times ON playlist_tracks.track_id = max_play_times.track_id
                   WHERE playlist_tracks.playlist_id=${id} ORDER BY title`;
        db_connection.query(sql, function (err, result) {
            if (err) throw err;
            db_connection.query(
                `SELECT name FROM playlists WHERE id=${id}`,
                function (e, r) {
                    display_track_list(`${r[0].name}`, result);
                }
            );
        });
    }
}


function SidebarPopup(id_prefix, width, height, title, template, on_item_click, populator_query) {
    var list_id = `${id_prefix}_view`;
    var popup_id = `${id_prefix}_popup`;
    var obj = {
        view: 'popup',
        id: popup_id,
        width: width,
        height: height,
        relative: 'right',
        body: {
            rows:[
                {
                    view: 'label',
                    label:`<b>${title}</b>`,
                    height:30
                },
                {
                    view:'list',
                    id:list_id,
                    select:true,
                    template: template,
                }
            ]
        }
    };
    webix.ready(
        function () {
            obj = webix.ui(obj);
            obj.hide();
            $$(list_id).attachEvent("onItemClick",
                function(id, e, node){
                    var item = this.getItem(id);
                    on_item_click(item.id)();
                    $$(popup_id).hide()
                    $$('main_menu_popup').hide();
                }
            );
            $$(popup_id).attachEvent('onShow',
            function () {
                $QUERY(
                    populator_query,
                    function (result_list) {
                        $$(list_id).clearAll()
                        $$(list_id).define('data', result_list);
                        $$(list_id).refresh()
                        webix.UIManager.setFocus($$(list_id));
                    }
                )
            });
            $$(popup_id).attachEvent('onHide',
            function () {
                webix.UIManager.setFocus($$('display_list'));
            });
            webix.UIManager.addHotKey("enter", function () {
                var g = $$(list_id).getSelectedItem();
                on_item_click(g.id)();
                $$(popup_id).hide();
                $$('main_menu_popup').hide();
                webix.UIManager.setFocus($$('display_list'));
            }, $$(list_id));
        }
    )
    return obj;
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
    return `<i class="ui left floated list icon"></i>
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
    return `<div class="webix_icon fa-list" style='float:left;transform: translateY(60%); font-size:13px'></div>
            <div class="tag_element_name">${element.name}</div>
            <div class="tag_element_count">${element.count}</div>
            <!-- <div style="float:right; position:relative; top:0%; transform: translateY(-80%); height:15px; width:20px; background-color:${element.color}"> -->
            </div>`
}

var genres_list_popup = SidebarPopup('genres_list', 300, 700, 'GENRES', genre_template, display_genre,
    `SELECT DISTINCT genre as id, COUNT(id) as count FROM tracks GROUP BY genre ORDER BY genre`
);

var sessions_list_popup = SidebarPopup('sessions_list', 450, 700, 'SESSIONS', session_template, display_session,
    `SELECT id, event_name as name, date(start_date) as date, counts.count as count
     FROM sessions JOIN (select session_id, count(track_id) as count FROM session_tracks
     GROUP BY session_id) counts ON sessions.id=counts.session_id ORDER BY date ASC`
);

var track_list_popup = SidebarPopup('track_list', 400, 700, 'TAGS', track_list_template, display_tag,
    `SELECT playlists.id as id , playlists.name, counts.count as count, playlist_categories.color AS color FROM
     playlists JOIN (SELECT playlist_id, count(track_id) as count FROM playlist_tracks GROUP BY playlist_id) counts
     ON playlists.id=counts.playlist_id JOIN playlist_categories ON playlists.category=playlist_categories.id ORDER BY category`
);



var sidebar_template = {
    css: {
        'background-color':'#3f3f3f',
        'padding':'0px',
        'margin':'0px',
        //'height': "100% !important"
    },
    width:350,
    //rows: [
    //    {
    multi:"mixed",
    id:"sidebar-accordions",
    view:"accordion",
    rows:[
        { 
            header:"Library",   
            body:{
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
            }
        },
        { 
            id: "playlists_item",
            collapsed:false, 
            header:"Groups",
            autoheight:true,
            body:{
                rows:[
                    {
                        id:"playlist-list",
                        view:"list",
                        template: track_list_template,
                        select:true,
                        scroll:"y",
                        itemHeight:15,
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
                                    win.show()
                                }
                            },
                            {},
                            {
                                view:'button',
                                type:'icon',
                                icon: 'edit',
                                width:40,
                                click: function () {
                                    win = new PlaylistEditor($$("playlist-list").getSelectedItem().id)
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
                                    win.show()
                                }
                            }

                        ]
                    }
                ]
            }
        },
        { 
            id: "sessions_item",
            header:"Sessions", 
            body: {
                view:'list',
                id:"sessions-list",
                select:true,
                template: session_template,
                on: {
                    onItemClick: function(id, e, node){
                        display_session(id)();
                    }
    
                }
            }, 
        }
    ],
    on: {
        onAfterExpand: function(i) {
            if (i == "sessions_item") {
                let list_id = "sessions-list"
                $QUERY(
                    `SELECT id, event_name as name, date(start_date) as date, counts.count as count
                    FROM sessions JOIN (select session_id, count(track_id) as count FROM session_tracks
                    GROUP BY session_id) counts ON sessions.id=counts.session_id ORDER BY date ASC`,
                    function (result_list) {
                        $$(list_id).clearAll()
                        $$(list_id).define('data', result_list);
                        $$(list_id).refresh()
                    }
                )

            } else if (i == "playlists_item") {
                let list_id = "playlist-list"
                $QUERY(
                    `SELECT playlists.id as id , playlists.name, IFNULL(counts.count, 0) as count FROM
                        playlists LEFT JOIN (SELECT playlist_id, count(track_id) as count FROM playlist_tracks GROUP BY playlist_id) counts
                        ON playlists.id=counts.playlist_id ORDER BY name`,
                    function (result_list) {
                        $$(list_id).clearAll()
                        $$(list_id).define('data', result_list);
                        $$(list_id).refresh()
                    }
                )

            }
        }
    }
       // },
   // ]
}
