var ID = function () {
    return '_' + Math.random().toString(36).substr(2, 9);
};

function PlaylistEditor(id) {
    var self = this

    self.playlist_id = id
    self.group_list = `playlist_group_list_${ID()}`
    self.track_count_label = `playlist_track_count_${ID()}`
    self.group_name_label = `playlist_name_${ID()}`
    self.player_cover_label = `playlist_cover_image_${ID()}`
    self.player_title_label = `playlist_title_name_${ID()}`
    self.player_artist_label = `playlist_artist_name_${ID()}`
    self.player_position_label = `playlist_position_name_${ID()}`
    self.player_duration_label = `playlist_duration_name_${ID()}`
    self.player_play_button = `playlist_duration_name_${ID()}`
    self.player_progress = `playlist_progress_${ID()}`

    self.database = new DataProvider()

    self.audio_player = new PrecuePlayer()
    if (self.audio_player.audio_context.audio_ctx.destination.maxChannelCount == 6) {
        self.audio_player.connectOutputs(pl_channel_config)    
    } else {
        self.audio_player.connectOutputs(pl_channel_config2)    
    }
    
    self.track_table = new TrackTable()
    self.track_list = new TrackList()

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
                                this.track_table.create_layout(),          
                                //{height:18}
                            ]
                        },
                        {width:1},
                        {
                            width:550,
                            css:{
                                border: '0px solid #3c3c3c'
                            },
                            rows:[
                                self.track_list.create_layout(),
                                self.audio_player.create_layout(),
                            ]
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
        d = $$(self.track_list.list_id).data.serialize()
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
                self.track_table.set_track_list("ALL TRACKS", result)
            }
        )
    }

    self.display_playlist_tracks = function () {
        self.database.get_playlist_tracks(self.playlist_id,
            function (result) {
                $QUERY(
                    `SELECT name FROM playlists WHERE id=${id}`,
                    function (r) {
                        self.track_list.set_track_list(result)
                        self.update_track_count_label()
                    }
                );
                    
            }
        )
    }

    self.add_to_playlist = function () {
        var id = self.track_table.get_selected_item().id 
        self.database.get_track_by_id(id,
            function(result) {
                self.track_list.add(result[0])
                self.track_list.sort("#title#","asc","string")
                self.update_track_count_label()
            }                
        )
    }

    self.remove_from_playlist = function () {
        x = self.track_list.get_selected() 
        self.track_list.remove(x) 
        self.update_track_count_label()    
    }
    
    self.update_track_count_label = function() {
        var count = $$(self.track_list.list_id).data.count();
        var length = 0;
        $$(self.track_list.list_id).data.each((row) => {length += row.stream_length})
        $$(self.track_count_label).define('label', `${count} tracks - ${format_seconds_long(length / 1000000000)}`);
        $$(self.track_count_label).refresh();
    }

    self.preview_play_track_id = function (id, stream_start, stream_end) {
        DB.get_track_by_id(id, (result) => {
            self.audio_player.play(result[0], stream_start, stream_end)
        })
    }

    self.preview_selected = function () {
        var id = self.track_table.get_selected_item().id 
        self.preview_play_track_id(id);
    }

    self.preview_last_10_seconds = function () {
        var id = self.track_table.get_selected_item().id 
        self.preview_play_track_id(id, -10000000000);
    }

    self.preview_last_30_seconds = function () {
        var id = self.track_table.get_selected_item().id 
        self.preview_play_track_id(id, -30000000000);
    }

    self.group_preview_selected = function () {
        var id = self.track_list.get_selected().id 
        self.preview_play_track_id(id);
    }

    self.group_preview_last_10_seconds = function () {
        var id = self.track_list.get_selected().id 
        self.preview_play_track_id(id, -10000000000);
    }

    self.group_preview_last_30_seconds = function () {
        var id = self.track_list.get_selected().id 
        self.preview_play_track_id(id, -30000000000);
    }


    self.show = function () {
        $QUERY(
            `SELECT name FROM playlists WHERE id=${self.playlist_id}`,
            function (r) {
                name = r[0].name
                self._win = webix.ui(self.template)
                self._win.show()
                self.audio_player.init_progress()
                self.track_table.init()
                self.display_all_tracks()
                self.display_playlist_tracks()
                $$(self.group_name_label).define('label', name);
                $$(self.group_name_label).refresh();        
                webix.UIManager.addHotKey("space",       () => self.audio_player.togglePause(),   $$(self.track_table.track_list));        
                webix.UIManager.addHotKey("shift+space", () => self.audio_player.stop(),          $$(self.track_table.track_list));        
                webix.UIManager.addHotKey("space",       () => self.audio_player.togglePause(),   $$(self.track_list.list_id));        
                webix.UIManager.addHotKey("shift+space", () => self.audio_player.stop(),          $$(self.track_list.list_id));        
                webix.UIManager.addHotKey("shift+a",     self.add_to_playlist,                    $$(self.track_table.track_list));
                webix.UIManager.addHotKey("ctrl+shift+enter", self.preview_last_30_seconds,       $$(self.track_table.track_list));
                webix.UIManager.addHotKey("shift+enter",      self.preview_last_10_seconds,       $$(self.track_table.track_list));
                webix.UIManager.addHotKey("enter",            self.preview_selected,              $$(self.track_table.track_list));
                webix.UIManager.addHotKey("ctrl+shift+enter", self.group_preview_last_30_seconds, $$(self.track_list.list_id));
                webix.UIManager.addHotKey("shift+enter",      self.group_preview_last_10_seconds, $$(self.track_list.list_id));
                webix.UIManager.addHotKey("enter",            self.group_preview_selected,        $$(self.track_list.list_id));
                webix.UIManager.addHotKey("delete",           self.remove_from_playlist,          $$(self.track_list.list_id));
                webix.UIManager.addHotKey("backspace",        self.remove_from_playlist,          $$(self.track_list.list_id));        
            }
        )
    }
    self.hide = function () {
        self._win.hide()
        self.audio_player.stop()
        if (self.onHide != undefined) {

            self.onHide()
        }
    }

}