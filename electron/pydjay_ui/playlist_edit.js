var display_list_fields = 'id, favorite, disabled as enabled, title, artist, album, genre, grouping, rating, bpm, stream_length, count(session_tracks.track_id) as play_count,  MAX(session_tracks.start_time) AS last_played';

function playlist_element_template(element) {
    var cover_source = null;
    if (element.cover == null) {
        cover_source = "../resources/images/default_album_cover.png"
    } else {
        cover_source = `file://${element.image_root}/${element.cover}`
    }
    return `<img style="float:left; padding-right:7px; padding-left:-3px" src="${cover_source}" height='${cover_size}' width='${cover_size}'></img>
            <div style="margin:0px; padding:0px; float:left; width:275px">
                <div class="queue_element_title"><b>${element.title}</b></div>
                <div class="queue_element_artist"><i>${element.artist}</i></div>
            </div>
            <div class="queue_element_bpm">${element.bpm} BPM</div>
            <div class="queue_element_duration">
                <b>${format_nanoseconds(element.stream_length)}</b>
            </div>`
}

var ID = function () {
    return '_' + Math.random().toString(36).substr(2, 9);
};

function PlaylistEditor(id) {
    var self = this

    self.playlist_id = id
    self.track_list = `playlist_track_list_${ID()}`
    self.track_list_filter = `playlist_track_list_filter_${ID()}`
    self.group_list = `playlist_group_list_${ID()}`
    self.track_count_label = `plylist_track_count_${ID()}`
    self.group_name_label = `plylist_name_${ID()}`

    self.database = new DataProvider()

    self.track_list_columns = [
        { id:"id",            header:"",  width:30, hidden:true, template:"<img src='../resources/images/precue.png' style='filter: invert(1);' height='20'>", checkValue:1, uncheckValue:0},
        { id:"favorite",      header:{text:"<b><span class='fa fa-heart' style='font-size: 12px'/></b>", height:25},  width:30, template:custom_checkbox, checkValue:1, uncheckValue:0, sort:'int'},
        { id:"title",         header:"<b style='font-size: 13px'>Title</b>",  fillspace:true, sort:'string'},
        { id:"artist",        header:"<b style='font-size: 13px'>Artist</b>", fillspace:true, sort:'string'},
        { id:"genre",         header:"<b style='font-size: 13px'>Genre</b>",  width:100, sort:'string'},
        { id:"grouping",      header:"<b style='font-size: 13px'>Grouping</b>",  width:80, sort:'string'},
        { id:"play_count",    header:{text:"<b><span class='fa fa-play'/></b>", css:{"text-align":'center'}},  width:30, template:"<div style='text-align: right'>#play_count#</div>", sort:'int'},
        { id:"last_played",   header:{text:"<b><span class='fa fa-calendar' style='font-size: 15px'/></b>", css:{"text-align":'right'}},  width:80, template: function(element) { return `${webix.Date.dateToStr("%Y-%m-%d")(element.last_played)}`}, sort:'int'},
        { id:"rating",        header:{text:"<b style='font-size: 13px'>Rating</b>", css:{"text-align":'center'}}, width:75, template:"<img src='../resources/images/rating#rating#.png' style='' height='10'>", css:{"text-align":'right'}, sort:'int'},
        { id:"bpm",           header:{text:"<b style='font-size: 13px'><span class='fa fa-heartbeat' style='font-size: 15px'/></b>", css:{"text-align":'center'}}, width:45, css:{"text-align":'right'}, sort:'int'},
        { id:"stream_length", header:{text:"<b style='font-size: 13px'>Time</b>", css:{"text-align":'center'}}, width:55, format:format_nanoseconds, css:{"text-align":'right'}},
    ]

    self.template = {
        view:"window",
        modal:true,
        position:"center",
        width:1500,
        height:1000,
        head: "EDIT PLAYLIST",
        body:{
            rows:[
                {height:10},
                {
                    height:75,
                    cols: [
                        {width:10},
                        {
                            rows: [
                                {
                                    id: self.group_name_label,
                                    view: 'label',
                                    label: "name of playlist",
                                    css: {'font-size':'30px'}
                                },
                                {
                                    id:self.track_count_label,
                                    view: 'label',
                                    label: "53 tracks - 1:35",
                                    css: {'font-size':'20px'}
                                }
                            ]
                        },
                        {width:10}
                    ]
                    
                },
                {height:10},                
                {
                    cols:[
                        {
                            css:{
                                border: '0px solid #3c3c3c'
                             },
                            rows: [
                                {
                                    id: 'playlist_edit_header_row',
                                    css:{
                                        'background-color':'#5c5c5c',
                                        'padding':'5px',
                                        border: '1px solid #3c3c3c'
                                     },
                        
                                    cols: [
                                        {width:5},
                                        {
                                            gravity:1,
                                            id: self.track_list_filter,
                                            view: 'search',
                                            placeholder:"Filter list...",
                                            keyPressTimeout:50,
                                            on: {
                                                onTimedKeyPress: function (){
                                                    $$(self.track_list).filterByAll();
                                                }
                                            }
                        
                                        },
                                        {width:10}
                                    ]
                                },
                                {
                                    view:"datatable",
                                    id:self.track_list,
                                    select:"row",
                                    resizeColumn:{headerOnly:true},
                                    rowHeight:25,
                                    css:{
                                        'background-color':'#303030',
                                        border: '0px solid #5c5c5c',
                                        "font-size":'13px'
                                     },
                                    columns:self.track_list_columns,
                                    scroll:"y"
                                },
                                {height:18}
                            ]
                        },
                        {width:12},
                        {
                            width:550,
                            css:{
                                border: '0px solid #3c3c3c'
                            },
                            rows:[
                                {
                                    id: 'playlist_edit_list_header_row',
                                    height:30,
                                    css:{
                                        'background-color':'#5c5c5c',
                                        border: '1px solid #3c3c3c'
                                     },
                                     rows: [
                                        {height:7},
                                        {
                                            view: 'label',
                                            label: '<b>TRACKS</b>',
                                            height: 20,
                                            css:{
                                                'padding-left':'10px',
                                             }
                                        },
                                        {height:5},
                                    ]
                        
                                },
                                {
                                    view:"list",
                                    id: self.group_list,
                                    itemHeight:15,
                                    css:{
                                        border: '1px solid #3c3c3c'
                                     },
                                    select:true,
                                    template: playlist_element_template,
                                    type: { height: cover_size  },
                                    scroll:"y"
                                }]
                        }
                    ]
                },
                {height:30},
                {
                    cols:[
                        {},
                        {
                            view: 'button',
                            label: 'SAVE',
                            click: function () {self.save_track_group()}
                        },
                        {},
                        {
                            view: 'button',
                            label: 'CANCEL',
                            click: () => {self.hide()}
                        },
                        {}
                    ]
                },
                {height:10}
            ]
        }
    }
    self.display_list_fields = 'id, favorite, disabled as enabled, title, artist, album, genre, grouping, rating, color, bpm, stream_length, count(session_tracks.track_id) as play_count,  MAX(session_tracks.start_time) AS last_played';

    self.save_track_group = function () {
        d = $$(self.group_list).data.serialize()
        playlist_data = []
        if (d.length > 0) {
            for (i=0; i<d.length; i++) {
                playlist_data.push(`(${self.playlist_id}, ${d[i].track_id})`)
            }
            delete_sql = `DELETE FROM playlist_tracks WHERE playlist_id=${self.playlist_id}`
            replace_sql = `INSERT INTO playlist_tracks (playlist_id, track_id) VALUES ${playlist_data.join(',')}`
            $QUERY(delete_sql,
                function () {
                    $QUERY(replace_sql, function () {self.hide();})
                }
            )
        }
    }

    self.display_all_tracks = function () {
        self.database.get_all_tracks(
            function (result) {
                $$(self.track_list).clearAll()
                $$(self.track_list).define("data", result)
                $$(self.track_list).refresh()                
            }
        )
    }

    self.display_playlist_tracks = function () {
        self.database.get_playlist_tracks(self.playlist_id,
            function (result) {
                $QUERY(
                    `SELECT name FROM playlists WHERE id=${id}`,
                    function (r) {
                        $$(self.group_list).clearAll()
                        $$(self.group_list).define("data", result)
                        $$(self.group_list).refresh()
                        self.update_track_count_label()
                    }
                );
                    
            }
        )
    }

    self.add_to_playlist = function () {
        var id = $$(self.track_list).getSelectedId().id;
        self.database.get_track_by_id(id,
            function(result) {
                $$(self.group_list).add(result[0]);
                $$(self.group_list).data.sort("#title#","asc","string")
                self.update_track_count_label()
            }                
        )
    }

    self.remove_from_playlist = function () {
        id = $$(self.group_list).getSelectedId();
        next = $$(self.group_list).getNextId(id);
        $$(self.group_list).remove(id);
        $$(self.group_list).select(next)
        self.update_track_count_label()    
    }

    self.filter_track_list = function () {
        var text = $$(self.track_list_filter).getValue()
        var i=0;
        search_tokens = text.split(' ')
        search_f = [];
        for (var i=0; i<search_tokens.length; i++) {
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
                            fields = [x.title, x.artist, x.genre, `@rat=${x.rating}`, '@bpm']
                            if (x.favorite) {
                                fields.push('@loved')
                            }
                            for (j=0; j<fields.length; j++) {
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
        $$(self.track_list).filter(
            function (obj) {
                for(i=0; i<search_f.length; i++) {
                    x = search_f[i](obj);
                    if (!x) {
                        return false;
                    }
                }
                return true;
            }
        )
    };
    
    self.update_track_count_label = function() {
        var count = $$(self.group_list).data.count();
        var length = 0;
        $$(self.group_list).data.each((row) => {length += row.stream_length})
        $$(self.track_count_label).define('label', `${count} tracks - ${format_seconds_long(length / 1000000000)}`);
        $$(self.track_count_label).refresh();
    }

    self.preview_selected = function () {
        var id = $$(self.track_list).getSelectedId().id;
        preview_track_id = id;
        preview_play_track_id(id);
    }

    self.preview_last_10_seconds = function () {
        var id = $$(self.track_list).getSelectedId().id;
        preview_track_id = id;
        preview_play_track_id(id, -10000000000);
    }

    self.preview_last_30_seconds = function () {
        var id = $$(self.track_list).getSelectedId().id;
        preview_track_id = id;
        preview_play_track_id(id, -30000000000);
    }

    self.group_preview_selected = function () {
        var id = $$(self.track_list).getSelectedId().id;
        preview_track_id = id;
        preview_play_track_id(id);
    }

    self.group_preview_last_10_seconds = function () {
        var id = $$(self.track_list).getSelectedId().id;
        preview_track_id = id;
        preview_play_track_id(id, -10000000000);
    }

    self.group_preview_last_30_seconds = function () {
        var id = $$(self.track_list).getSelectedId().id;
        preview_track_id = id;
        preview_play_track_id(id, -30000000000);
    }


    self.show = function () {
        $QUERY(
            `SELECT name FROM playlists WHERE id=${self.playlist_id}`,
            function (r) {
                name = r[0].name
                self._win = webix.ui(self.template)
                self._win.show()
                $$(self.track_list).filterByAll = self.filter_track_list
                self.display_all_tracks()
                self.display_playlist_tracks()
                $$(self.group_name_label).define('label', name);
                $$(self.group_name_label).refresh();        
                webix.UIManager.addHotKey("shift+a", self.add_to_playlist, $$(self.track_list));
                webix.UIManager.addHotKey("ctrl+shift+enter", self.preview_last_30_seconds, $$(self.track_list));
                webix.UIManager.addHotKey("shift+enter", self.preview_last_10_seconds, $$(self.track_list));
                webix.UIManager.addHotKey("enter", self.preview_selected, $$(self.track_list));
                webix.UIManager.addHotKey("ctrl+shift+enter", self.group_preview_last_30_seconds, $$(self.group_list));
                webix.UIManager.addHotKey("shift+enter", self.group_preview_last_10_seconds, $$(self.group_list));
                webix.UIManager.addHotKey("enter", self.group_preview_selected, $$(self.group_list));
                webix.UIManager.addHotKey("delete", self.remove_from_playlist, $$(self.group_list));
                webix.UIManager.addHotKey("backspace", self.remove_from_playlist, $$(self.group_list));        
            }
        )
    }
    self.hide = function () {
        self._win.hide()
        if (self.onHide != undefined) {
            self.onHide()
        }
    }

}


function NewPlaylist() {
    var self = this

    self.playlist_name = `new_playlist_name_${ID()}`
    self.playlist_desc = `new_playlist_desc_${ID()}`

    self.template = {
        view:"window",
        modal:true,
        position:"center",
        width:600,
        height:400,
        head: "NEW PLAYLIST",
        body:{
            rows:[
                {height:10},
                {
                    id:self.playlist_name,
                    view: "text",
                    value:'',
                    label:"Name:",
                    labelWidth:100
                },
                {height:30},
                {
                    cols:[
                        {},
                        {
                            view: 'button',
                            label: 'CREATE',
                            click: function () {
                                self.create_playlist(self.hide)
                            }
                        },
                        {},
                        {
                            view: 'button',
                            label: 'CANCEL',
                            click: () => {self.hide()}
                        },
                        {}
                    ]
                },
                {height:10}
            ]
        }
    }

    self.create_playlist = function (done) {
        name = $$(self.playlist_name).getValue()
        $QUERY(
        `SELECT id FROM playlists WHERE name='${name}'`,
        function (x) {
            if (x.length == 0) {
                current_time = webix.Date.dateToStr('%Y-%m-%d %H:%i:%s')(new Date());
                $QUERY(
                    `INSERT INTO playlists (name, created) VALUES ('${name}', '${current_time}')`,
                    function (x) {
                        webix.message({
                            text:`Created new playlist '${name}'`,
                            type:"info",
                            expire: 3000,
                            id:"message1"
                        });
                        done()
                    }
                )
            } else {
                webix.message({
                    text:`Playlist '${name}' could not be created.</br>The name already exists`,
                    type:"error",
                    expire: 3000,
                    id:"message1"
                });
                done()
    
            }
        }
    )
    }
    

    self.show = function () {
        self._win = webix.ui(self.template)
        self._win.show()
    }

    self.hide = function () {
        self._win.hide()
        if (self.onHide != undefined) {
            self.onHide()
        }
    }
}




function PlaylistDuplicator(id) {

    var self = this
    self.playlist_id = id
    self.playlist_name = `duplicate_playlist_name_${ID()}`
    self.playlist_desc = `duplicate_playlist_desc_${ID()}`

    self.template = {
        view:"window",
        modal:true,
        position:"center",
        width:600,
        height:400,
        head: "DUPLICATE PLAYLIST",
        body:{
            rows:[
                {height:10},
                {
                    id:self.playlist_name,
                    view: "text",
                    value:'',
                    label:"Name:",
                    labelWidth:75
                },
                {height:30},
                {
                    cols:[
                        {},
                        {
                            view: 'button',
                            label: 'DUPLICATE',
                            click: function () {
                                self.create_playlist(self.hide)
                                //self.hide();
                            }
                        },
                        {},
                        {
                            view: 'button',
                            label: 'CANCEL',
                            click: () => {self.hide()}
                        },
                        {}
                    ]
                },
                {height:10}
            ]
        }
    }

    self.create_playlist = function (done) {
        name = $$(self.playlist_name).getValue()
        $QUERY(
        `SELECT id FROM playlists WHERE name='${name}'`,
        function (x) {
            if (x.length == 0) {
                current_time = webix.Date.dateToStr('%Y-%m-%d %H:%i:%s')(new Date());
                $QUERY(
                    `INSERT INTO playlists (name, created) VALUES ('${name}',  '${current_time}')`,
                    function (x) {
                        new_playlist_id = x.insertId
                        $QUERY(
                            `SELECT track_id FROM playlist_tracks WHERE playlist_id=${self.playlist_id}`,
                            function (list) {
                                playlist_data = []
                                if (list.length > 0) {
                                    for (i=0; i<list.length; i++) {
                                        playlist_data.push(`(${new_playlist_id}, ${list[i].track_id})`)
                                    }
                                    replace_sql = `INSERT INTO playlist_tracks (playlist_id, track_id) VALUES ${playlist_data.join(',')}`
                                    $QUERY(replace_sql, function () {
                                        webix.message({
                                            text:`Created new playlist '${name}'`,
                                            type:"info",
                                            expire: 3000,
                                            id:"message1"
                                        });
                                        done();
                                    })
                                }
                            }
                        )
                    }
                )
            } else {
                webix.message({
                    text:`Playlist '${name}' could not be created.</br>The name already exists`,
                    type:"error",
                    expire: 3000,
                    id:"message1"
                });
                done();
            }
        }
    )
    }
    

    self.show = function () {
        self._win = webix.ui(self.template)
        self._win.show()
    }
    self.hide = function () {
        self._win.hide()
        if (self.onHide != undefined) {
            self.onHide()
        }

    }
}

function DeletePlaylist(id) {

    var self = this
    self.playlist_id = id
    self.playlist_name = `delete_playlist_name_${ID()}`
    self.playlist_desc = `delte_playlist_desc_${ID()}`

    self.template = {
        view:"window",
        modal:true,
        position:"center",
        width:600,
        height:400,
        head: "DELETE PLAYLIST",
        body:{
            rows:[
                {height:10},
                {
                    id:self.playlist_name,
                    view: "label",
                    label:'Delete playlist (name)? This cannot be undone',
                    labelWidth:75
                },
                {height:30},
                {
                    cols:[
                        {},
                        {
                            view: 'button',
                            label: 'DELETE',
                            click: function () {
                                self.delete_playlist(self.hide)
                            }
                        },
                        {},
                        {
                            view: 'button',
                            label: 'CANCEL',
                            click: () => {self.hide()}
                        },
                        {}
                    ]
                },
                {height:10}
            ]
        }
    }

    self.delete_playlist = function (done) {
        $QUERY(
            `DELETE FROM playlists WHERE id=${self.playlist_id}`,
            function (r) {
                $QUERY(
                    `DELETE FROM playlist_tracks WHERE playlist_id=${self.playlist_id}`,
                    function (r) {
                        done()
                    }
                )
            }
        )
    }
    
    self.show = function () {
        self._win = webix.ui(self.template)
        self._win.show()
    }

    self.hide = function () {
        self._win.hide()
        if (self.onHide != undefined) {
            self.onHide()
        }

    }
}

function SetAsShortlist(id) {
    var self = this
    self.playlist_id = id
    self.playlist_name = `set_as_shortlist_name_${ID()}`
    self.playlist_desc = `set_as_shortlist_desc_${ID()}`
    self.database = new DataProvider()
    self.template = {
        view:"window",
        modal:true,
        position:"center",
        width:600,
        height:400,
        head: "SET PLAYLIST AS SHORT LIST",
        body:{
            rows:[
                {height:10},
                {
                    id:self.playlist_name,
                    view: "label",
                    label:'Set playlist (name)? as the current short list? The current short list will be lost.',
                    labelWidth:75
                },
                {height:30},
                {
                    cols:[
                        {},
                        {
                            view: 'button',
                            label: 'SET AS SHORTLIST',
                            width:200,
                            click: function () {
                                self.set_as_shortlist(self.hide)
                            }
                        },
                        {},
                        {
                            view: 'button',
                            label: 'CANCEL',
                            click: () => {self.hide()}
                        },
                        {}
                    ]
                },
                {height:10}
            ]
        }
    }

    self.set_as_shortlist = function (done) {
        $QUERY("DELETE FROM short_listed_tracks",
            function () {
                self.database.get_playlist_tracks(self.playlist_id,
                    function (tracks) {
                         d = []
                         for(i=0; i<tracks.length; i++) {
                             d.push(`(${tracks[i].track_id})`)
                         }
                         $QUERY(
                             `INSERT IGNORE INTO short_listed_tracks VALUES ${d.join(',')}`,
                             function (r) {
                                webix.message({
                                    text:`Playlist set as short list`,
                                    type:"info",
                                    expire: 3000,
                                    id:"message1"
                                })
                                done();        
                             }
                        )
                    }
                )
            }
        )
    }
    
    self.show = function () {
        self._win = webix.ui(self.template)
        self._win.show()
    }
    self.hide = function () {
        self._win.hide()
        if (self.onHide != undefined) {
            self.onHide()
        }

    }
}


function SaveAsPlaylist() {

    var self = this
    //self.playlist_id = id
    self.playlist_name = `duplicate_playlist_name_${ID()}`
    self.playlist_desc = `duplicate_playlist_desc_${ID()}`

    self.template = {
        view:"window",
        modal:true,
        position:"center",
        width:600,
        height:400,
        head: "SAVE THE SHORTLISTED TRACKS",
        body:{
            rows:[
                {height:10},
                {
                    id:self.playlist_name,
                    view: "text",
                    value:'',
                    label:"Name:",
                    labelWidth:75
                },
                {height:30},
                {
                    cols:[
                        {},
                        {
                            view: 'button',
                            label: 'SAVE',
                            click: function () {
                                self.create_playlist(self.hide)
                            }
                        },
                        {},
                        {
                            view: 'button',
                            label: 'CANCEL',
                            click: () => {self.hide()}
                        },
                        {}
                    ]
                },
                {height:10}
            ]
        }
    }

    self.create_playlist = function (done) {
        name = $$(self.playlist_name).getValue()
        $QUERY(
        `SELECT id FROM playlists WHERE name='${name}'`,
        function (x) {
            if (x.length == 0) {
                current_time = webix.Date.dateToStr('%Y-%m-%d %H:%i:%s')(new Date());
                $QUERY(
                    `INSERT INTO playlists (name, created) VALUES ('${name}',  '${current_time}')`,
                    function (x) {
                        new_playlist_id = x.insertId
                        $QUERY(
                            `SELECT track_id FROM short_listed_tracks`,
                            function (list) {
                                playlist_data = []
                                if (list.length > 0) {
                                    for (i=0; i<list.length; i++) {
                                        playlist_data.push(`(${new_playlist_id}, ${list[i].track_id})`)
                                    }
                                    replace_sql = `INSERT INTO playlist_tracks (playlist_id, track_id) VALUES ${playlist_data.join(',')}`
                                    $QUERY(replace_sql, function () {
                                        webix.message({
                                            text:`Created new playlist '${name}'`,
                                            type:"info",
                                            expire: 3000,
                                            id:"message1"
                                        });
                                        done();
                                    })
                                }
                            }
                        )
                    }
                )
            } else {
                webix.message({
                    text:`Playlist '${name}' could not be created.</br>The name already exists`,
                    type:"error",
                    expire: 3000,
                    id:"message1"
                });
                done();
            }
        }
    )
    }
    

    self.show = function () {
        self._win = webix.ui(self.template)
        self._win.show()
    }
    self.hide = function () {
        self._win.hide()
        if (self.onHide != undefined) {
            self.onHide()
        }

    }
}
