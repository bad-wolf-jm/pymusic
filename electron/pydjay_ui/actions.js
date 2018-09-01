
var queue_actions = {
    move_selection_to_top: function () {
        selected_queue_element = $$('queue_list').getSelectedItem();
        selected_queue_element_position = $$('queue_list').getSelectedItem().position;
        DB.move_queue_element(selected_queue_element_position, 1,
            function (new_position) {
                move_displayed_queue_element(selected_queue_element, selected_queue_element_position, new_position);
                $$('queue_list').moveTop(selected_queue_element.id)
            }
        )
    },

    move_selection_up: function () {
        selected_queue_element = $$('queue_list').getSelectedItem();
        selected_queue_element_position = $$('queue_list').getSelectedItem().position;
        DB.move_queue_element(selected_queue_element_position, selected_queue_element_position-1,
            function (new_position) {
                move_displayed_queue_element(selected_queue_element, selected_queue_element_position, new_position);
                $$('queue_list').moveUp(selected_queue_element.id, 1)
            }
        )
    },

    move_selection_down: function () {
        selected_queue_element = $$('queue_list').getSelectedItem();
        selected_queue_element_position = $$('queue_list').getSelectedItem().position;
        DB.move_queue_element(selected_queue_element_position, selected_queue_element_position+1,
            function (new_position) {
                move_displayed_queue_element(selected_queue_element, selected_queue_element_position, new_position);
                $$('queue_list').moveDown(selected_queue_element.id, 1)
            }
        )
    },

    remove_selection: function () {
        selected_queue_element = $$('queue_list').getSelectedItem();
        selected_queue_element_position = $$('queue_list').getSelectedItem().position;
        DB.delete_queue_element(selected_queue_element_position,
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
                $$(main_track_table.track_list).removeRowCss(selected_queue_element.track_id, 'unavailable_track');
                $$(main_track_table.track_list).getItem(selected_queue_element.track_id).$css="";
                $$(main_track_table.track_list).refresh();
                // $$('suggestion_list').removeCss(selected_queue_element.track_id, 'unavailable_track');

                update_queue_labels();
                //u pdate_suggestions();
            }
        )
    },

    edit_track_data: function () {
        selected_queue_element = $$('queue_list').getSelectedItem();
        selected_queue_element_position = $$('queue_list').getSelectedItem().position;
        edit_track_data(selected_queue_element.track_id);
    },

    reload: function () {
        DB.get_queue_elements(
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
        var id = $$(main_track_table.track_list).getSelectedId().id;
        DB.add_id_to_queue(id,
            function () {
                DB.get_queue_track(id,
                    function (result) {
                        $$('queue_list').add(result[0]);
                        $$(main_track_table.track_list).addRowCss(id, 'unavailable_track');
                        update_queue_labels();
                    }
                )
            }
        )
    },

    add_selection_to_short_list: function () {
        var id = $$(main_track_table.track_list).getSelectedId().id;
        sql = `SELECT 1 FROM short_listed_tracks WHERE track_id=${id} LIMIT 1`;
        db_connection.query(sql,
            function (err, result){
                if (result.length == 0){
                    insert_sql = `INSERT INTO short_listed_tracks (track_id) VALUES (${id})`;
                    db_connection.query(insert_sql, function(error, result){
                        if (error) throw error;
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
        var id = $$(main_track_table.track_list).getSelectedId().id;
        db_connection.query(
            `SELECT 1 FROM unavailable_tracks WHERE track_id=${id} LIMIT 1`,
            function (error, result) {
                if (error) throw error;
                if (result.length == 0) {
                    db_connection.query(
                        `INSERT INTO unavailable_tracks (track_id) VALUES (${id})`,
                        function (error, result) {
                            if (error) throw error;
                            $$(main_track_table.track_list).addRowCss(id, 'unavailable_track');

                        }
                    )
                }
            }
        )
    },

    remove_selection_from_unavailable: function () {
        var id = $$(main_track_table.track_list).getSelectedId().id;
        console.log(`DELETE FROM unavailable_tracks WHERE track_id=${id}`)
        db_connection.query(`SELECT 1 FROM unavailable_tracks WHERE track_id=${id} LIMIT 1`,
            function (error, result) {
                if (error) throw error;
                if (result.length > 0) {
                    db_connection.query(
                        `DELETE FROM unavailable_tracks WHERE track_id=${id}`,
                        function (error, result) {
                            if (error) throw error;
                            $$(main_track_table.track_list).removeRowCss(id, 'unavailable_track');
                            $$(main_track_table.track_list).getItem(id).$css="";
                            $$(main_track_table.track_list).refresh();
                        }
                    )
                }
            }
        )
    },

    save_shortlist_as_playlist: function () {
        var win = new SaveAsPlaylist()
        win.show()
    },

    edit_track_data: function () {
        var id = $$(main_track_table.track_list).getSelectedId().id;
        edit_track_data(id);
    },

    display_all_songs: () => {display_all_songs()},

    filter_list: function () {
        webix.UIManager.setFocus($$(main_track_table.track_list));
    },

    preview_selected: function () {
        var id = $$(main_track_table.track_list).getSelectedId().id;
        preview_track_id = id;
        preview_play_track_id(id);
    },

    preview_last_10_seconds: function () {
        var id = $$(main_track_table.track_list).getSelectedId().id;
        preview_track_id = id;
        preview_play_track_id(id, -10000000000);
    },

    preview_last_30_seconds: function () {
        var id = $$(main_track_table.track_list).getSelectedId().id;
        preview_track_id = id;
        preview_play_track_id(id, -30000000000);
    }
}

var playback_actions = {
    preview_pause: function () {
        !main_track_table.filtering ? preview_pause(): undefined;
    },

    preview_stop: function () {
        !main_track_table.filtering ? preview_stop(): undefined;
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