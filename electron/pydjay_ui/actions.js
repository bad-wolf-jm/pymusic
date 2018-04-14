
var queue_actions = {
    move_selection_to_top: function () {
        selected_queue_element = $$('queue_list').getSelectedItem();
        selected_queue_element_position = $$('queue_list').getSelectedItem().position;
        move_queue_element(selected_queue_element_position, 1,
            function (new_position) {
                move_displayed_queue_element(selected_queue_element, selected_queue_element_position, new_position);
                $$('queue_list').moveTop(selected_queue_element.id)
            }
        )
    },

    move_selection_up: function () {
        selected_queue_element = $$('queue_list').getSelectedItem();
        selected_queue_element_position = $$('queue_list').getSelectedItem().position;
        move_queue_element(selected_queue_element_position, selected_queue_element_position-1,
            function (new_position) {
                move_displayed_queue_element(selected_queue_element, selected_queue_element_position, new_position);
                $$('queue_list').moveUp(selected_queue_element.id, 1)
            }
        )
    },

    move_selection_down: function () {
        selected_queue_element = $$('queue_list').getSelectedItem();
        selected_queue_element_position = $$('queue_list').getSelectedItem().position;
        move_queue_element(selected_queue_element_position, selected_queue_element_position+1,
            function (new_position) {
                move_displayed_queue_element(selected_queue_element, selected_queue_element_position, new_position);
                $$('queue_list').moveDown(selected_queue_element.id, 1)
            }
        )
    },

    remove_selection: function () {
        selected_queue_element = $$('queue_list').getSelectedItem();
        selected_queue_element_position = $$('queue_list').getSelectedItem().position;
        delete_queue_element(selected_queue_element_position,
            function () {
                var next_item = $$('queue_list').getNextId(selected_queue_element.id);
                if (next_item == undefined) {
                    next_item = $$('queue_list').getPrevId(selected_queue_element.id);
                }
                $$('queue_list').remove(selected_queue_element.id);
                $$('queue_list').data.each(
                    function (element) {
                        if (element.position > selected_queue_element_position) {
                            element.position--;
                        }
                    }
                );
                if (next_item != undefined) {
                    $$('queue_list').select(next_item)
                }
                $$('display_list').removeRowCss(selected_queue_element.track_id, 'unavailable_track');
                $$('display_list').getItem(selected_queue_element.track_id).$css="";
                $$('display_list').refresh();
                $$('suggestion_list').removeCss(selected_queue_element.track_id, 'unavailable_track');

                update_queue_labels();
                update_suggestions();
            }
        )
    },

    edit_track_data: function () {
        selected_queue_element = $$('queue_list').getSelectedItem();
        selected_queue_element_position = $$('queue_list').getSelectedItem().position;
        edit_track_data(selected_queue_element.track_id);
    },

    reload: function () {
        $QUERY(
            `SELECT tracks.id as track_id, session_queue.id as id, session_queue.position, tracks.title, tracks.artist, tracks.album,
             tracks.bpm, tracks.stream_length, settings.db_image_cache as image_root, tracks.cover_small as cover, session_queue.position as position
             FROM (tracks LEFT JOIN settings ON 1) LEFT JOIN session_queue ON tracks.id=session_queue.track_id WHERE session_queue.status='pending'
             ORDER BY session_queue.position`,
            function(queue_content) {
                $$('queue_list').clearAll();
                for(var i=0; i < queue_content.length; i++){
                    $$('queue_list').add(queue_content[i])
                }
            }
        )
    },

    preview_selection: function () {
        var id = $$('queue_list').getSelectedItem().track_id;
        preview_track_id = id;
        preview_play_track_id(id);
    },

    preview_last_10_seconds: function () {
        var id = $$('queue_list').getSelectedItem().track_id;
        preview_track_id = id;
        preview_play_track_id(id, -10000000000);
    },

    preview_last_30_seconds: function () {
        var id = $$('queue_list').getSelectedItem().track_id;
        preview_track_id = id;
        preview_play_track_id(id, -30000000000);
    }
}


var main_list_actions = {
    add_selection_to_queue: function () {
        var id = $$('display_list').getSelectedId().id;
        add_id_to_queue(id,
            function () {
                sql = `SELECT tracks.id as track_id, session_queue.position, tracks.title, tracks.artist, tracks.album, tracks.bpm,
                       tracks.stream_length, settings.db_image_cache as image_root, tracks.cover_small as cover, session_queue.position as position
                       FROM (tracks LEFT JOIN settings ON 1) LEFT JOIN session_queue ON tracks.id=session_queue.track_id
                       WHERE session_queue.status='pending' AND session_queue.track_id=${id} ORDER BY session_queue.position`;
                db_connection.query(sql,
                    function (err, result) {
                        if (err) throw err;
                        $$('queue_list').add(result[0]);
                        $$('display_list').addRowCss(id, 'unavailable_track');
                        $$('suggestion_list').addCss(id, 'unavailable_track');
                        update_queue_labels();
                        update_suggestions();
                    }
                );
            }
        )
    },

    add_selection_to_short_list: function () {
        var id = $$('display_list').getSelectedId().id;
        sql = `SELECT 1 FROM short_listed_tracks WHERE track_id=${id} LIMIT 1`;
        db_connection.query(sql,
            function (err, result){
                if (result.length == 0){
                    insert_sql = `INSERT INTO short_listed_tracks (track_id) VALUES (${id})`;
                    db_connection.query(insert_sql, function(error, result){
                        if (error) throw error;
                        console.log('FOO')
                        webix.message({
                            text:"Added track to the short list",
                            type:"info",
                            expire: 3000,
                            id:"message1"
                        });

                    });
                } else {
                    webix.message({
                        text:"Track is already in the short list",
                        type:"info",
                        expire: 3000,
                        id:"message1"
                    });
                }
            }
        )
    },

    add_selection_to_unavailable: function () {
        var id = $$('display_list').getSelectedId().id;
        db_connection.query(
            `SELECT 1 FROM unavailable_tracks WHERE track_id=${id} LIMIT 1`,
            function (error, result) {
                if (error) throw error;
                if (result.length == 0) {
                    db_connection.query(
                        `INSERT INTO unavailable_tracks (track_id) VALUES (${id})`,
                        function (error, result) {
                            if (error) throw error;
                            $$('display_list').addRowCss(id, 'unavailable_track');
                            $$('suggestion_list').addCss(id, 'unavailable_track');

                        }
                    )
                }
            }
        )
    },

    remove_selection_from_unavailable: function () {
        var id = $$('display_list').getSelectedId().id;
        console.log(`DELETE FROM unavailable_tracks WHERE track_id=${id}`)
        db_connection.query(
            `SELECT 1 FROM unavailable_tracks WHERE track_id=${id} LIMIT 1`,
            function (error, result) {
                if (error) throw error;
                if (result.length > 0) {
                    db_connection.query(
                        `DELETE FROM unavailable_tracks WHERE track_id=${id}`,
                        function (error, result) {
                            if (error) throw error;
                            $$('display_list').removeRowCss(id, 'unavailable_track');
                            $$('display_list').getItem(id).$css="";
                            $$('display_list').refresh();
                            $$('suggestion_list').removeCss(id, 'unavailable_track');

                        }
                    )
                }
            }
        )
    },

    edit_track_data: function () {
        var id = $$('display_list').getSelectedId().id;
        edit_track_data(id);
    },

    display_all_songs: () => {display_all_songs()},

    filter_list: function () {
        webix.UIManager.setFocus($$('display_list'));
    },

    preview_selected: function () {
        var id = $$('display_list').getSelectedId().id;
        preview_track_id = id;
        preview_play_track_id(id);
    },

    preview_last_10_seconds: function () {
        var id = $$('display_list').getSelectedId().id;
        preview_track_id = id;
        preview_play_track_id(id, -10000000000);
    },

    preview_last_30_seconds: function () {
        var id = $$('display_list').getSelectedId().id;
        preview_track_id = id;
        preview_play_track_id(id, -30000000000);
    }
}

var playback_actions = {
    preview_pause: function () {
        !filtering ? preview_pause(): undefined;
    },

    preview_stop: function () {
        !filtering ? preview_stop(): undefined;
    },

    increase_main_player_volume: function () {
        increase_main_player_volume()
    },

    decrease_main_player_volume: function () {
        decrease_main_player_volume()
    },

    increase_precue_player_volume: function () {
        increase_precue_player_volume()
    },

    decrease_precue_player_volume: function () {
        decrease_precue_player_volume()
    },

    increase_monitor_volume: function () {
        increase_monitor_volume()
    },

    decrease_monitor_volume: function () {
        decrease_monitor_volume()
    },

    preview_forward_seek_short: function () {
        preview_seek_relative(5)
    },

    preview_forward_seek_long: function () {
        preview_seek_relative(20)
    },

    preview_backward_seek_short: function () {
        preview_seek_relative(-5)
    },

    preview_backward_seek_long: function () {
        preview_seek_relative(-20)
    }
}


var track_edit_actions = {
    close_track_editor: function () {
        preview_stop();
        track_data_edit_window.hide()
    },

    play_last_30_seconds: function () {
        preview_play_track_id(track_edited.id, -30000000000, stream_end_edit);
    },

    play_last_10_seconds: function () {
        preview_play_track_id(track_edited.id, -10000000000, stream_end_edit);
    },

    play_track: function () {
        preview_play_track_id(track_edited.id, stream_start_edit, stream_end_edit);
    },

    set_start_marker: function () {
        set_start_marker_to_current_time();
    },

    set_end_marker: function () {
        set_end_marker_to_current_time();
    },

    move_start_marker_forward_short: function () {
        set_start_marker(stream_start_edit + 100000000);
    },

    move_start_marker_forward_long: function () {
        set_start_marker(stream_start_edit + 1000000000);
    },

    move_end_marker_forward_short: function () {
        set_end_marker(stream_end_edit + 100000000);
    },

    move_end_marker_forward_long: function () {
        set_end_marker(stream_end_edit + 1000000000);
    },

    move_start_marker_backward_short: function () {
        set_start_marker(stream_start_edit - 100000000);
    },

    move_start_marker_backward_long: function () {
        set_start_marker(stream_start_edit - 1000000000);
    },

    move_end_marker_backward_short:function () {
        set_end_marker(stream_end_edit - 100000000);
    },

    move_end_marker_backward_long:function () {
        set_end_marker(stream_end_edit - 1000000000);
    },

    reset_waveform_zoom: function () {
        track_edit_waveform.xAxis[0].setExtremes(0, track_length_edit, true, false);
        webix.UIManager.setFocus($$('track_edit_window'));
    },

    zoom_waveform_first_10_seconds: function () {
        track_edit_waveform.xAxis[0].setExtremes(0, 10000000000, true, false);
        webix.UIManager.setFocus($$('track_edit_window'));
    },

    zoom_waveform_first_30_seconds: function () {
        track_edit_waveform.xAxis[0].setExtremes(0, 30000000000, true, false);
        webix.UIManager.setFocus($$('track_edit_window'));
    },

    zoom_waveform_last_10_seconds: function () {
        track_edit_waveform.xAxis[0].setExtremes(track_length_edit - 10000000000, track_length_edit, true, false);
        webix.UIManager.setFocus($$('track_edit_window'));
    },

    zoom_waveform_last_30_seconds: function () {
        track_edit_waveform.xAxis[0].setExtremes(track_length_edit - 30000000000, track_length_edit, true, false);
        webix.UIManager.setFocus($$('track_edit_window'));
    }
}


var suggestion_list_actions = {
    add_selection_to_queue: function () {
        var id = $$('suggestion_list').getSelectedItem().id;
        add_id_to_queue(id,
            function () {
                sql = `SELECT tracks.id as track_id, session_queue.position, tracks.title, tracks.artist, tracks.album, tracks.bpm,
                       tracks.stream_length, settings.db_image_cache as image_root, tracks.cover_small as cover, session_queue.position as position
                       FROM (tracks LEFT JOIN settings ON 1) LEFT JOIN session_queue ON tracks.id=session_queue.track_id
                       WHERE session_queue.status='pending' AND session_queue.track_id=${id} ORDER BY session_queue.position`;
                db_connection.query(sql,
                    function (err, result) {
                        if (err) throw err;
                        $$('queue_list').add(result[0]);
                        $$('display_list').addRowCss(id, 'unavailable_track');
                        $$('suggestion_list').addCss(id, 'unavailable_track');
                        update_queue_labels();
                        update_suggestions();
                    }
                );
            }
        )
    },

    add_selection_to_short_list: function () {
        var id = $$('suggestion_list').getSelectedItem().id;
        sql = `SELECT 1 FROM short_listed_tracks WHERE track_id=${id} LIMIT 1`;
        db_connection.query(sql,
            function (err, result){
                if (result.length == 0){
                    insert_sql = `INSERT INTO short_listed_tracks (track_id) VALUES (${id})`;
                    db_connection.query(insert_sql, function(error, result){
                        if (error) throw error;
                        console.log('FOO')
                        webix.message({
                            text:"Added track to the short list",
                            type:"info",
                            expire: 3000,
                            id:"message1"
                        });

                    });
                } else {
                    webix.message({
                        text:"Track is already in the short list",
                        type:"info",
                        expire: 3000,
                        id:"message1"
                    });
                }
            }
        )
    },

    add_selection_to_unavailable: function () {
        var id = $$('suggestion_list').getSelectedItem().id;
        db_connection.query(
            `SELECT 1 FROM unavailable_tracks WHERE track_id=${id} LIMIT 1`,
            function (error, result) {
                if (error) throw error;
                if (result.length == 0) {
                    db_connection.query(
                        `INSERT INTO unavailable_tracks (track_id) VALUES (${id})`,
                        function (error, result) {
                            if (error) throw error;
                            $$('display_list').addRowCss(id, 'unavailable_track');
                            $$('suggestion_list').addCss(id, 'unavailable_track');
                        }
                    )
                }
            }
        )
    },

    remove_selection_from_unavailable: function () {
        var id = $$('suggestion_list').getSelectedItem().id;
        console.log(`DELETE FROM unavailable_tracks WHERE track_id=${id}`)
        db_connection.query(
            `SELECT 1 FROM unavailable_tracks WHERE track_id=${id} LIMIT 1`,
            function (error, result) {
                if (error) throw error;
                if (result.length > 0) {
                    db_connection.query(
                        `DELETE FROM unavailable_tracks WHERE track_id=${id}`,
                        function (error, result) {
                            if (error) throw error;
                            $$('display_list').removeRowCss(id, 'unavailable_track');
                            $$('display_list').getItem(id).$css="";
                            $$('display_list').refresh();
                            $$('suggestion_list').removeCss(id, 'unavailable_track');
                            $$('suggestion_list').refresh();


                        }
                    )
                }
            }
        )
    },

    edit_track_data: function () {
        var id = $$('suggestion_list').getSelectedItem().id;
        edit_track_data(id);
    },

    preview_selected: function () {
        var id = $$('suggestion_list').getSelectedItem().id;
        preview_track_id = id;
        preview_play_track_id(id);
    },

    preview_last_10_seconds: function () {
        var id = $$('suggestion_list').getSelectedItem().id;
        preview_track_id = id;
        preview_play_track_id(id, -10000000000);
    },

    preview_last_30_seconds: function () {
        var id = $$('suggestion_list').getSelectedItem().id;
        preview_track_id = id;
        preview_play_track_id(id, -30000000000);
    }
}
