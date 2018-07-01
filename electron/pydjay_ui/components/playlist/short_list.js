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
