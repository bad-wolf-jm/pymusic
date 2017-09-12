

function display_track_list(list_name, list_elements) {
    $$('display_list').clearAll()
    for(i=0; i<list_elements.length; i++){
        if (!list_elements[i].available){
            list_elements[i].$css = "unavailable_track";
        }
    }
    $$('display_list').define('data', list_elements);
    $$('display_list').refresh();
    $$('playlist_name').define('label', list_name);
    $$('playlist_name').refresh();
    webix.UIManager.setFocus($$('display_list'));
}

var display_list_fields = 'id, favorite, disabled as enabled, title, artist, album, genre, rating, bpm, stream_length, count(session_tracks.track_id) as play_count';

function display_all_songs(){
   return function () {
       var sql =`SELECT availability.track_id IS NULL as available, ${display_list_fields}
                 FROM tracks LEFT JOIN session_tracks ON tracks.id = session_tracks.track_id
                 LEFT JOIN ((select track_id from unavailable_tracks) union (select track_id from session_queue)) availability ON availability.track_id=tracks.id
                 GROUP BY id`;
       db_connection.query(sql, function (err, result) {
           if (err) throw err;
           display_track_list('All Songs', result);
         });
   }
}


function display_short_listed_songs(){
    return function () {
       var sql =`SELECT availability.track_id IS NULL as available, ${display_list_fields}
                 FROM tracks LEFT JOIN session_tracks ON tracks.id = session_tracks.track_id
                 JOIN short_listed_tracks ON tracks.id=short_listed_tracks.track_id
                 LEFT JOIN ((select track_id from unavailable_tracks) union (select track_id from session_queue)) availability ON availability.track_id=tracks.id
                 GROUP BY id`;
       db_connection.query(sql, function (err, result) {
           if (err) throw err;
           display_track_list('Short List', result);
        }
    );}
}

function display_unavailable_songs(){
    return function () {
       var sql =`SELECT availability.track_id IS NULL as available, ${display_list_fields}
                 FROM tracks LEFT JOIN session_tracks ON tracks.id = session_tracks.track_id
                 JOIN unavailable_tracks ON tracks.id=unavailable_tracks.track_id
                 LEFT JOIN (select track_id from session_queue) availability ON availability.track_id=tracks.id
                 GROUP BY id`;
       db_connection.query(sql, function (err, result) {
           if (err) throw err;
           display_track_list('Short List', result);
        }
    );}
}


function display_genre(name){
    return function () {
        var sql = `SELECT availability.track_id IS NULL as available, ${display_list_fields}
                   FROM tracks LEFT JOIN session_tracks ON tracks.id = session_tracks.track_id
                   LEFT JOIN ((select track_id from unavailable_tracks) union (select track_id from session_queue)) availability ON availability.track_id=tracks.id
                   WHERE genre="${name}" GROUP BY id`;
        db_connection.query(sql, function (err, result) {
            if (err) throw err;
            display_track_list(name, result);
          });
    }
}


function display_session(id){
    return function () {
        var sql = `SELECT availability.track_id IS NULL as available,  id, favorite, disabled as enabled, title, artist,
                   album, genre, rating, bpm, stream_length, foo.play_count
FROM session_tracks JOIN
(SELECT * FROM tracks JOIN (SELECT
  id as id_2, count(session_tracks.track_id) as play_count
FROM tracks JOIN session_tracks ON tracks.id = session_tracks.track_id
GROUP BY id) play_counts ON tracks.id=play_counts.id_2) foo
ON session_tracks.track_id=foo.id
LEFT JOIN ((select track_id from unavailable_tracks) union (select track_id from session_queue)) availability ON availability.track_id=session_tracks.track_id
WHERE session_tracks.session_id=${id}`;
        db_connection.query(sql, function (err, result) {
            if (err) throw err;
            db_connection.query(
                `SELECT event_name, start_date FROM sessions WHERE id=${id}`,
                function (e, r) {
                    display_track_list(`${r[0].event_name} - ${webix.Date.dateToStr("%Y-%m-%d")(r[0].start_date)}`, result);
                }
            );
          });
    }
}

function display_tag(id){
    return function () {
        var sql = `SELECT availability.track_id IS NULL as available, id, favorite, disabled as enabled, title, artist,
                   album, genre, rating, bpm, stream_length, foo.play_count
FROM playlist_tracks JOIN
(SELECT * FROM tracks JOIN (SELECT
  id as id_2, count(session_tracks.track_id) as play_count
FROM tracks LEFT JOIN session_tracks ON tracks.id = session_tracks.track_id
GROUP BY id) play_counts ON tracks.id=play_counts.id_2) foo
ON playlist_tracks.track_id=foo.id
LEFT JOIN ((select track_id from unavailable_tracks) union (select track_id from session_queue)) availability ON availability.track_id=playlist_tracks.track_id
WHERE playlist_tracks.playlist_id=${id}`;
//console.log(sql);
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


function genre_template(element) {
    var cover_source = null;
    if (element.cover == null) {
        cover_source = "../resources/images/default_album_cover.png"
    } else {
        cover_source = `${element.image_root}/${element.cover}`
    }
    return `<div>
            <i class="ui left floated list icon"></i>
            <div style="float:left; margin:0px; padding:0px; height:22px; font_size:10px; white-space:nowrap; overflow: hidden; text-overflow: ellipsis; width:70%">${element.name}</div>
            <div style="height:22px; font_size:12px; white-space:nowrap; overflow: hidden; text-overflow: ellipsis; width:20%; text-align:right">${element.count}</div>
            </div>`
    }

var genres_list_popup =
    {
        view:"popup",
        id:"genres_list_popup",
        relative:'right',
        height:700,
        width:300,
        body:{
            rows:[
                {
                    view: 'label',
                    label:"<b>GENRES</b>",
                    height:30
                },
                {
                    view:'list',
                    id:'genres_list_view',
                    select:true,
                    template: genre_template,
                }
            ]
        }
}



function session_template(element) {
    var cover_source = null;
    if (element.cover == null) {
        cover_source = "../resources/images/default_album_cover.png"
    } else {
        cover_source = `${element.image_root}/${element.cover}`
    }
    return `<i class="ui left floated list icon"></i>
            <div style="float:left; margin:0px; padding:0px; height:22px; font_size:10px; white-space:nowrap; overflow: hidden; text-overflow: ellipsis; width:35%">${element.name}</div>
            <div style="float:left; margin:0px; padding:0px; height:22px; font_size:10px; white-space:nowrap; overflow: hidden; text-overflow: ellipsis; width:35%; text-align:right">${webix.Date.dateToStr("%Y-%m-%d")(element.date)}</div>
            <div style="margin:0px; padding:0px; height:22px; font_size:10px; white-space:nowrap; overflow: hidden; text-overflow: ellipsis; width:20%; text-align:right">${element.count}</div>`
    }

var sessions_list_popup = //webix.ui(
    {
        view:"popup",
        id:"sessions_list_popup",
        relative:'right',
        height:700,
        width:450,
        body:{
            rows:[
                {
                    view: 'label',
                    label:"<b>SESSIONS</b>",
                    height:30
                },
                {
                    view:'list',
                    id:'sessions_list_view',
                    template: session_template,
                }
            ]
        }
}



function track_list_template(element) {
    var cover_source = null;
    if (element.cover == null) {
        cover_source = "../resources/images/default_album_cover.png"
    } else {
        cover_source = `${element.image_root}/${element.cover}`
    }
    return `<i class="ui left floated list icon"></i>
            <div style="float:left; margin:0px; padding:0px; height:22px; font_size:10px; white-space:nowrap; overflow: hidden; text-overflow: ellipsis; width:70%">${element.name}</div>
            <div style="margin:0px; padding:0px; height:22px; font_size:10px; white-space:nowrap; overflow: hidden; text-overflow: ellipsis; width:15%; text-align:right">${element.count}</div>`
    }

var track_list_popup =
    {
        view:"popup",
        id:"track_list_popup",
        relative:'right',
        height:700,
        width:350,
        body:{
            rows:[
                {
                    view:'label',
                    label:"<b>TAGS</b>",
                    height:30
                },
                {
                    view:'list',
                    id:'track_list_view',
                    template: track_list_template,
                }
            ]
        }
}

var sidebar_template = {
    css: {
        'background-color':'#3f3f3f',
        'padding':'0px',
        'margin':'0px',
        //'color':'#232323'
    },
    width:125,
    rows: [
        {
            id: 'show_all_songs',
            view:'button',
            label:'<b>ALL SONGS</b>',
            type:'icon',
            icon:'database',
            click:display_all_songs()
        },
        {
            id: 'show_short_list',
            view:'button',
            label:'<b>SHORT LIST</b>',
            type:'icon',
            icon:'calendar',
            click:display_short_listed_songs(),
            hotkey:'ctrl+shift+s'
        },
        {
            id: 'show_unavailable',
            view:'button',
            label:'<b>UNAVAILABLE</b>',
            type:'icon',
            icon:'close',
            click:display_unavailable_songs(),
            hotkey:'ctrl+shift+u'
        },
        {
            id: 'show_remations',
            view:'button',
            label:'<b>RELATIONS</b>',
            type:'icon',
            icon:'cog'
        },
        {
            id: 'show_genres',
            view:'button',
            label:'<b>GENRES</b>',
            type:'icon',
            icon:'folder',
            popup:'genres_list_popup',
            hotkey:'ctrl+g'
        },
        {
            id: 'show_lists',
            view:'button',
            label:'<b>TAGS</b>',
            type:'icon',
            icon:'folder',
            popup:'track_list_popup',
            hotkey:'ctrl+l'
        },
        {
            id: 'show_sessions',
            view:'button',
            label:'<b>SESSIONS</b>',
            type:'icon',
            icon:'folder',
            popup:'sessions_list_popup',
            hotkey:'ctrl+s'
        },
        {}
    ]
}
