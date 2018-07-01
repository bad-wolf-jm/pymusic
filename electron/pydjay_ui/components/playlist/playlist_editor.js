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

    self.audio_player = new PydjayAudioFilePlayer()
    if (self.audio_player.audio_context.audio_ctx.destination.maxChannelCount == 6) {
        self.audio_player.connectOutputs(pl_channel_config)    
    } else {
        self.audio_player.connectOutputs(pl_channel_config2)    
    }
    self.audio_player.on("stream-position", function (pos) {
        $$(self.player_position_label).define('label', `${format_nanoseconds(pos*1000000)}`)
        $$(self.player_position_label).refresh()
        $$(self.player_duration_label).define('label', format_nanoseconds(self.audio_player.source.duration*1000000000))
        $$(self.player_duration_label).refresh();
        self.preview_seek.animate(pos / (1000*self.audio_player.source.duration));
        self.preview_track_position = pos;
    })
    
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
                                self.track_list.create_layout(),
                                {
                                    height:95,
                                    css:{
                                        'background-color':'#6c6c6c',
                                        'padding':'1px',
                                        border: '1px solid #3c3c3c'
                                     },
                                    cols:[
                                        {
                                            id:self.player_cover_label,
                                            view: 'template',
                                            width:95,
                                            height:95,
                                            template: ""
                                        },
                                        {width:10},
                                        {
                                            cols: [
                                                {
                                
                                                    rows: [
                                                        {},
                                                        {
                                                            cols: [
                                                                {
                                                                    rows: [
                                                                        {
                                                                            id: self.player_title_label,
                                                                            view: 'label',
                                                                            label: "<b>NO TRACK</b>",
                                                                            height:20
                                                                        },
                                                                        {
                                                                            id: self.player_artist_label,
                                                                            view: 'label',
                                                                            label: "NO ARTIST",
                                                                            height:20
                                                                        },                
                                                                    ]
                                                                },
                                                                {width:5},
                                                                {
                                                                    id:self.player_play_button,
                                                                    view:'button',
                                                                    type: 'icon',
                                                                    icon: 'headphones',
                                                                    width:30,
                                                                    popup: "preview_popup_menu"
                                                                },
                                
                                
                                                            ]
                                                        },
                                                        {},
                                                        {
                                                            cols: [
                                                                {
                                                                    rows: [
                                                                        {
                                                                            height:18,
                                                                            template:`<div id="${self.player_progress}" style="margin:0px; padding:0px; width:100%; height:100%; position:relative; top:0%; left:0%;"></div>`
                                                                        },
                                                                        {height: 7},
                                                                        {cols:[
                                                                            {
                                                                                id:self.player_position_label,
                                                                                view: 'label',
                                                                                css:{
                                                                                    'text-align':'left',
                                                                                    'text-transform':'uppercase'
                                                                                },
                                                                                label: '0:00',
                                                                                height:15
                                                                            },
                                                                            {},
                                                                            {
                                                                                id:self.player_duration_label,
                                                                                view: 'label',
                                                                                css:{'text-align':'right'},
                                                                                label: '0:00',
                                                                                height:15
                                                                            }
                                                        
                                                                        ]},                
                                                                    ]
                                                                },
                                                            ]
                                                        },
                                                        {}
                                                    ]
                                        
                                                },
                                                {width:10}
                                            ]
                                        }
                                    ]
                                }
                                                            
                            
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
        db_connection.query(
            `SELECT title, artist, album, bpm, file_name, cover_small, track_length, genre, stream_start, year, stream_end, settings.db_music_cache as music_root,
             settings.db_image_cache as image_root FROM tracks left join settings on 1 WHERE tracks.id=${id} LIMIT 1`,
            function(error, result) {
                if (error) throw error;
                result = result[0];
                file_name = path.join(result.music_root, result.file_name);
                cover_file_name = `${result.image_root}/${result.cover_small}`;
                stream_length = (result.stream_end-result.stream_start) / 1000000000;
                preview_play_id = result.id
                $$(self.player_title_label).define('label', result.title)
                $$(self.player_title_label).refresh()
                $$(self.player_artist_label).define('label', `${result.artist}`)
                $$(self.player_artist_label).refresh()
                if (result.cover_small == null) {
                    cover_source = "../resources/images/default_album_cover.png"
                } else {
                    cover_source = `file://${result.image_root}/${result.cover_small}`;
                }
                var cover_image = `<img style="margin:0px; padding:0px;" src="${cover_source}" height='95' width='95'></img>`
                $$(self.player_cover_label).define('template', cover_image);
                $$(self.player_cover_label).refresh();
    
                if (stream_start == undefined) {
                    stream_start = result.stream_start 
                    stream_end = result.stream_end
                } else if (stream_end == undefined) {
                    stream_end = end = result.stream_end
                    if (stream_start < 0) {
                        stream_start = stream_end + stream_start;
                    }
                }
                self.audio_player.play(file_name, stream_start / 1000000, stream_end / 1000000)
            }
        )    
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

                self.preview_seek = new ProgressBar.Line(`#${self.player_progress}`,
                    {
                        strokeWidth: 1,
                        duration: 5,
                        color: '#5a5a5a',
                        trailColor: '#eee',
                        trailWidth: 1,
                        svgStyle: {width: '100%', height: '100%'}
                    }
                )
                self.preview_seek.animate(0)

                self.track_table.init()
                self.display_all_tracks()
                self.display_playlist_tracks()
                $$(self.group_name_label).define('label', name);
                $$(self.group_name_label).refresh();        
                webix.UIManager.addHotKey("space", () => self.audio_player.togglePause(), $$(self.track_table.track_list));        
                webix.UIManager.addHotKey("shift+space", () => self.audio_player.stop(), $$(self.track_table.track_list));        
                webix.UIManager.addHotKey("space", () => self.audio_player.togglePause(), $$(self.track_list.list_id));        
                webix.UIManager.addHotKey("shift+space", () => self.audio_player.stop(), $$(self.track_list.list_id));        

                webix.UIManager.addHotKey("shift+a", self.add_to_playlist, $$(self.track_table.track_list));
                webix.UIManager.addHotKey("ctrl+shift+enter", self.preview_last_30_seconds, $$(self.track_table.track_list));
                webix.UIManager.addHotKey("shift+enter", self.preview_last_10_seconds, $$(self.track_table.track_list));
                webix.UIManager.addHotKey("enter", self.preview_selected, $$(self.track_table.track_list));
                webix.UIManager.addHotKey("ctrl+shift+enter", self.group_preview_last_30_seconds, $$(self.track_list.list_id));
                webix.UIManager.addHotKey("shift+enter", self.group_preview_last_10_seconds, $$(self.track_list.list_id));
                webix.UIManager.addHotKey("enter", self.group_preview_selected, $$(self.track_list.list_id));
                webix.UIManager.addHotKey("delete", self.remove_from_playlist, $$(self.track_list.list_id));
                webix.UIManager.addHotKey("backspace", self.remove_from_playlist, $$(self.track_list.list_id));        
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