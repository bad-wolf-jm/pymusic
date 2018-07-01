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
