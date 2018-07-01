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
