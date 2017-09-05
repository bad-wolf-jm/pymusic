genres_dropdown_collapsed = true;
genres_query = `SELECT DISTINCT genre FROM tracks ORDER BY genre`


function display_all_songs(){
   return function () {
       var sql =`SELECT id, favorite, disabled as enabled, title, artist,
                   album, genre, date_added, date_modified, rating, bpm, stream_length,
                   max(session_tracks.start_time) as last_played, count(session_tracks.track_id) as play_count
                  FROM tracks LEFT JOIN session_tracks ON tracks.id = session_tracks.track_id GROUP BY id`;
       db_connection.query(sql, function (err, result) {
           if (err) throw err;
           $$('display_list').clearAll()
           $$('playlist_name').define('label', 'All Songs');
           $$('playlist_name').refresh();
           $$('display_list').define('data', result);
           $$('display_list').refresh();
         });
   }
}



function display_short_listed_songs(){
   return function () {
       var sql =`SELECT id, favorite, disabled as enabled, title, artist,
                   album, genre, date_added, date_modified, rating, bpm, stream_length,
                   max(session_tracks.start_time) as last_played, count(session_tracks.track_id) as play_count
                  FROM tracks LEFT JOIN session_tracks ON tracks.id = session_tracks.track_id JOIN short_listed_tracks
                  ON tracks.id=short_listed_tracks.track_id GROUP BY id`;
       db_connection.query(sql, function (err, result) {
           if (err) throw err;
           $$('display_list').clearAll()
           $$('playlist_name').define('label', 'Short List');
           $$('playlist_name').refresh();
           $$('display_list').define('data', result);
           $$('display_list').refresh();
         });
   }
}


function display_genre(name){
    return function () {
        var sql = `SELECT id, favorite, disabled as enabled, title, artist,
                   album, genre, date_added, date_modified, rating, bpm, stream_length,
                   max(session_tracks.start_time) as last_played, count(session_tracks.track_id) as play_count
                   FROM tracks LEFT JOIN session_tracks ON tracks.id = session_tracks.track_id
                   WHERE genre="${name}" GROUP BY id`;
        db_connection.query(sql, function (err, result) {
            if (err) throw err;
            $$('display_list').clearAll()
            $$('display_list').define('data', result);
            $$('display_list').refresh();
            $$('playlist_name').define('label', name);
            $$('playlist_name').refresh();
          });
    }
}



function display_session(id){
    return function () {
        var sql = `SELECT id, favorite, disabled as enabled, title, artist,
                   album, genre, rating, bpm, stream_length, foo.play_count
FROM session_tracks JOIN
(SELECT * FROM tracks JOIN (SELECT
  id as id_2, count(session_tracks.track_id) as play_count
FROM tracks JOIN session_tracks ON tracks.id = session_tracks.track_id
GROUP BY id) play_counts ON tracks.id=play_counts.id_2) foo
ON session_tracks.track_id=foo.id WHERE session_tracks.session_id=${id}`;
        db_connection.query(sql, function (err, result) {
            if (err) throw err;
            db_connection.query(
                `SELECT event_name FROM sessions WHERE id=${id}`,
                function (e, r) {
                    $$('display_list').clearAll();
                    $$('display_list').define('data', result);
                    $$('display_list').refresh();
                    $$('playlist_name').define('label', r[0].event_name);
                    $$('playlist_name').refresh();
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
                <div class='ui right floated grey label' style="height:22px; font_size:12px; white-space:nowrap; overflow: hidden; text-overflow: ellipsis; width:20%; text-align:right">${element.count}</div>
                </div>`
    }

var genres_list_popup = //webix.ui(
    {
        view:"popup",
        id:"genres_list_popup",
        relative:'right',
        height:500,
        width:300,
        body:{
            rows:[
                {
                    template:"<b>GENRES</b>",
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
            <div class 'ui right floated grey label' style="margin:0px; padding:0px; height:22px; font_size:10px; white-space:nowrap; overflow: hidden; text-overflow: ellipsis; width:20%; text-align:right">${element.count}</div>`
    }

var sessions_list_popup = //webix.ui(
    {
        view:"popup",
        id:"sessions_list_popup",
        relative:'right',
        height:500,
        width:400,
        body:{
            rows:[
                {
                    template:"<b>SESSIONS</b>",
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
            <div style="margin:0px; padding:0px; height:22px; font_size:10px; white-space:nowrap; overflow: hidden; text-overflow: ellipsis">${element.name}</div>
            <div class 'ui right floated grey label' style="margin:0px; padding:0px; height:22px; font_size:10px; white-space:nowrap; overflow: hidden; text-overflow: ellipsis" width=150>${element.count}</div>`
    }

var track_list_popup = //webix.ui(
    {
        view:"popup",
        id:"track_list_popup",
        relative:'right',
        height:500,
        width:300,
        body:{
            rows:[
                {
                    template:"<b>LISTS</b>",
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
    css:{'background-color':'#EEEEEE',
         'padding':'0px',
         'margin':'0px'},
    width:125,
    rows: [
        {id: 'show_all_songs', view:'button', label:'<b>ALL SONGS</b>',  type:'icon', icon:'database', click:display_all_songs()},
        {id: 'show_short_list', view:'button', label:'<b>SHORT LIST</b>', type:'icon', icon:'calendar', click:display_short_listed_songs(), hotkey:'ctrl+shift+s'},
        {id: 'show_remations', view:'button', label:'<b>RELATIONS</b>',  type:'icon', icon:'cog'},
        {id: 'show_genres', view:'button', label:'<b>GENRES</b>',     type:'icon', icon:'folder', popup:'genres_list_popup', hotkey:'ctrl+g'}, //genres_dropdown,
        {id: 'show_lists', view:'button', label:'<b>LISTS</b>',      type:'icon', icon:'folder', popup:'track_list_popup', hotkey:'ctrl+l'},
        {id: 'show_sessions', view:'button', label:'<b>SESSIONS</b>',   type:'icon', icon:'folder', popup:'sessions_list_popup', hotkey:'ctrl+s'},
        {}
    ]
}
