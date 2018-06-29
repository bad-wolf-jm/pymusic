class MusicDatabase extends EventDispatcher {
    constructor () {
        super()
        this.display_list_fields = `
            id, favorite, disabled as enabled, title, artist, album, genre, grouping, rating, bpm, stream_length, 
            color, count(session_tracks.track_id) as play_count,  MAX(session_tracks.start_time) AS last_played
        `;
        this.db_connection = mysql.createConnection({
            host: "localhost",
            user: "root",
            password: "root",
            database:'pymusic'
          });
        this.db_connection.connect(
            function(err) {
              if (err) throw err;
              console.log("Connected!");
          });
          
    
    }

    $QUERY(sql, with_result) {
        db_connection.query(
            sql,
            function (error, result) {
                if (error) {
                    console.log(error)
                    throw error;
                } else {
                    with_result(result);
                }
            }
        )
    }
    
    
    get_track_by_id (id, k) {
        this.$QUERY(`SELECT availability.track_id IS NULL as available, tracks.id as id, tracks.id as track_id, tracks.favorite, tracks.disabled as enabled, tracks.title, tracks.artist, tracks.file_name as file_name,
        tracks.stream_start as stream_start, tracks.stream_end as stream_end, tracks.track_length as track_length, tracks.grouping, tracks.year, tracks.color as color,
        tracks.album, tracks.genre, tracks.rating, tracks.bpm, tracks.stream_length, foo.play_count, tracks.cover_small as cover, settings.db_image_cache as image_root, settings.db_music_cache as music_root,
        max_play_times.time as last_played FROM tracks JOIN (SELECT * FROM tracks JOIN (SELECT id as id_2, count(session_tracks.track_id) as play_count
        FROM tracks LEFT JOIN session_tracks ON tracks.id = session_tracks.track_id GROUP BY id) play_counts ON tracks.id=play_counts.id_2) foo ON tracks.id=foo.id LEFT JOIN
        ((select track_id from unavailable_tracks) UNION (select track_id from session_queue)) availability ON availability.track_id=tracks.id LEFT JOIN 
        (SELECT track_id, MAX(start_time) AS time FROM session_tracks GROUP BY track_id) max_play_times ON tracks.id = max_play_times.track_id LEFT JOIN settings on 1 
        WHERE tracks.id=${id} ORDER BY title`, k)
    }

    get_all_tracks (k) {
        var sql =`SELECT availability.track_id IS NULL as available, ${this.display_list_fields} FROM tracks LEFT JOIN session_tracks
        ON tracks.id = session_tracks.track_id LEFT JOIN ((select track_id from unavailable_tracks) UNION
        (select track_id from session_queue)) availability ON availability.track_id=tracks.id GROUP BY id ORDER BY title`;
        this.$QUERY(sql, k);
    }

    get_playlist_tracks (id, k) {
        var sql = `SELECT availability.track_id IS NULL as available, playlist_tracks.track_id, playlist_tracks.track_id as id, favorite, disabled as enabled, 
        title, artist, album, genre, rating, bpm, stream_length, foo.play_count, cover_small as cover, color,
        settings.db_image_cache as image_root, max_play_times.time as last_played FROM playlist_tracks JOIN
        (SELECT * FROM tracks JOIN (SELECT id as id_2, count(session_tracks.track_id) as play_count
        FROM tracks LEFT JOIN session_tracks ON tracks.id = session_tracks.track_id GROUP BY id) play_counts
        ON tracks.id=play_counts.id_2) foo ON playlist_tracks.track_id=foo.id LEFT JOIN
        ((select track_id from unavailable_tracks) UNION (select track_id from session_queue)) availability
        ON availability.track_id=playlist_tracks.track_id LEFT JOIN (SELECT track_id, MAX(start_time) AS time
        FROM session_tracks GROUP BY track_id) max_play_times ON playlist_tracks.track_id = max_play_times.track_id
        LEFT JOIN settings on 1 WHERE playlist_tracks.playlist_id=${id} ORDER BY title`;
        this.$QUERY(sql, k)        
    }

    get_session_tracks (id, k) {
        var sql = `SELECT availability.track_id IS NULL as available,  id, favorite, disabled as enabled, title, artist,
        album, genre, rating, bpm, stream_length, foo.play_count, max_play_times.time as last_played, color
        FROM session_tracks JOIN
        (SELECT * FROM tracks JOIN (SELECT id as id_2, count(session_tracks.track_id) as play_count
        FROM tracks JOIN session_tracks ON tracks.id = session_tracks.track_id GROUP BY id) play_counts ON
        tracks.id=play_counts.id_2) foo ON session_tracks.track_id=foo.id LEFT JOIN
        ((select track_id from unavailable_tracks) UNION (select track_id from session_queue)) availability ON
        availability.track_id=session_tracks.track_id LEFT JOIN (SELECT track_id, MAX(start_time) AS time
        FROM session_tracks GROUP BY track_id) max_play_times ON id = max_play_times.track_id
        WHERE session_tracks.session_id=${id}`;
        this.$QUERY(sql, k)
    }

    get_never_played_tracks (k) {
        var sql =`SELECT * FROM (SELECT availability.track_id IS NULL as available, ${this.display_list_fields} FROM tracks LEFT JOIN session_tracks ON
        tracks.id = session_tracks.track_id LEFT JOIN
        (select track_id from session_queue) availability ON availability.track_id=tracks.id GROUP BY id ORDER BY title) q WHERE q.play_count = 0`;
        this.$QUERY(sql, k)
    }

    get_played_tracks (k) {
        var sql =`SELECT * FROM (SELECT availability.track_id IS NULL as available, ${this.display_list_fields} FROM tracks LEFT JOIN session_tracks ON
        tracks.id = session_tracks.track_id LEFT JOIN
        (select track_id from session_queue) availability ON availability.track_id=tracks.id GROUP BY id ORDER BY title) q WHERE q.play_count != 0`;
        this.$QUERY(sql, k)
    }

    get_shortlisted_tracks (k) {
        var sql =`SELECT availability.track_id IS NULL as available, ${this.display_list_fields}
        FROM tracks LEFT JOIN session_tracks ON tracks.id = session_tracks.track_id
        JOIN short_listed_tracks ON tracks.id=short_listed_tracks.track_id LEFT JOIN ((select track_id from unavailable_tracks) UNION
        (select track_id from session_queue)) availability ON availability.track_id=tracks.id GROUP BY id ORDER BY title`;
        this.$QUERY(sql, k)
    }

    get_unavailable_tracks (k) {
        var sql = `SELECT availability.track_id IS NULL as available, ${this.display_list_fields} FROM tracks LEFT JOIN session_tracks ON
        tracks.id = session_tracks.track_id JOIN unavailable_tracks ON tracks.id=unavailable_tracks.track_id LEFT JOIN
        (select track_id from session_queue) availability ON availability.track_id=tracks.id GROUP BY id ORDER BY title`
        this.$QUERY(sql, k)
    }

    get_sessions_list (k) {
        this.$QUERY(`SELECT id, event_name as name, date(start_date) as date, counts.count as count FROM sessions 
        JOIN (select session_id, count(track_id) as count FROM session_tracks GROUP BY session_id) counts 
        ON sessions.id=counts.session_id ORDER BY date ASC`, k)
    }

    get_group_list (k) {
        this.$QUERY(`SELECT playlists.id as id , playlists.name, IFNULL(counts.count, 0) as count FROM
        playlists LEFT JOIN (SELECT playlist_id, count(track_id) as count FROM playlist_tracks GROUP BY playlist_id) counts
        ON playlists.id=counts.playlist_id ORDER BY name`, k)
    }
 
    get_queue_elements (k) {
        this.$QUERY(`SELECT tracks.id as track_id, session_queue.id as id, session_queue.position, tracks.title, tracks.artist, tracks.album, tracks.color as color,
        tracks.bpm, tracks.stream_length, settings.db_image_cache as image_root, tracks.cover_small as cover, session_queue.position as position
        FROM (tracks LEFT JOIN settings ON 1) LEFT JOIN session_queue ON tracks.id=session_queue.track_id WHERE session_queue.status='pending'
        ORDER BY session_queue.position`, k)
    }

    get_queue_track = function(id, k) {
        this.$QUERY(`SELECT tracks.id as track_id, session_queue.position, tracks.title, tracks.artist, tracks.album, tracks.bpm,
        tracks.stream_length, settings.db_image_cache as image_root, tracks.cover_small as cover, session_queue.position as position
        FROM (tracks LEFT JOIN settings ON 1) LEFT JOIN session_queue ON tracks.id=session_queue.track_id
        WHERE session_queue.status='pending' AND session_queue.track_id=${id} ORDER BY session_queue.position`, k)
    }

    get_suggested_tracks (k) {
        this.$QUERY(`SELECT 
            availability.track_id IS NULL as available, 
            tracks.id, 
            tracks.favorite, 
            tracks.disabled AS enabled, 
            tracks.title, 
            tracks.artist, 
            tracks.album, 
            tracks.genre, 
            tracks.rating, 
            tracks.bpm, 
            tracks.stream_length, 
            foo.play_count, 
            tracks.cover_small AS cover, 
            tracks.color,
            settings.db_image_cache AS image_root, 
            max_play_times.time AS last_played 
            FROM tracks JOIN
            (SELECT * FROM tracks JOIN 
                (SELECT 
                    id as id_2, 
                    count(session_tracks.track_id) as play_count 
                FROM tracks LEFT JOIN session_tracks ON tracks.id = session_tracks.track_id GROUP BY id
                ) play_counts
            ON tracks.id=play_counts.id_2) foo ON tracks.id=foo.id 
            LEFT JOIN ((SELECT track_id FROM unavailable_tracks) UNION (SELECT track_id FROM session_queue)) availability
            ON availability.track_id=tracks.id 
            LEFT JOIN 
                (SELECT track_id, MAX(start_time) AS time 
                FROM session_tracks GROUP BY track_id) max_play_times 
            ON tracks.id = max_play_times.track_id
            LEFT JOIN settings on 1 
            WHERE tracks.id IN (SELECT DISTINCT related_track_id FROM track_relations WHERE track_id IN (SELECT track_id FROM session_queue WHERE status='pending')) 
            ORDER BY title ASC`, k)
    }

    get_queue_duration (k) {
        this.$QUERY(`SELECT SUM(duration) as duration, COUNT(id) as count, AVG(wait_time) as wait_time FROM
        (SELECT 1 as id, tracks.stream_length as duration, session_queue.id as count, settings.wait_time as wait_time
        FROM tracks JOIN session_queue ON tracks.id=session_queue.track_id LEFT JOIN settings on 1
        WHERE session_queue.status='pending' OR session_queue.status='playing') dummy GROUP BY id`, k)
    }

    add_track (track_info, k) {
        sql = `INSERT INTO tracks (
        id, title, artist, album, year, genre, bpm, rating, favorite, comments, waveform, cover_medium,
        cover_small, cover_large, cover_original, track_length, stream_start, stream_end, stream_length,
        date_added, date_modified, bitrate, samplerate, file_name, file_size, hash, category, description,
        disabled, original_file_name, grouping)
        VALUES (${track_info.id},${track_info.title}, ${track_info.artist}, ${track_info.album}, ${track_info.year},
        ${track_info.genre}, ${track_info.bpm}, ${track_info.rating}, ${track_info.favorite}, ${track_info.comments},
        ${track_info.waveform}, ${track_info.cover_medium}, ${track_info.cover_small}, ${track_info.cover_large},
        ${track_info.cover_original}, ${track_info.track_length}, ${track_info.stream_start}, ${track_info.stream_end},
        ${track_info.stream_length}, ${track_info.date_added}, ${track_info.date_modified}, ${track_info.bitrate},
        ${track_info.samplerate}, ${track_info.file_name}, ${track_info.file_size}, ${track_info.hash}, ${track_info.category},
        ${track_info.description}, ${track_info.disabled}, ${track_info.original_file_name}, ${track_info.grouping})`
        this.$QUERY(sql, k)
    }

    update_track_data (id, track_info, k) {
        let sql = "UPDATE tracks SET "
        let fields = Object.keys(track_info);
        sql += fields.indexOf("title") != -1 ? `title=${STRING(addslashes(track_info.title))},\n` : '' 
        sql += fields.indexOf("artist") != -1 ? `artist=${STRING(addslashes(track_info.artist))},\n` : '' 
        sql += fields.indexOf("album") != -1 ? `album=${STRING(addslashes(track_info.album))},\n` : '';
        sql += fields.indexOf("year") != -1 ? `year=${track_info.year},\n` : '' 
        sql += fields.indexOf("genre") != -1 ? `genre=${STRING(addslashes(track_info.genre))},\n` : '' 
        sql += fields.indexOf("bpm") != -1 ? `bpm=${track_info.bpm},\n` : '' 
        sql += fields.indexOf("rating") != -1 ? `rating=${track_info.rating},\n` : '' 
        sql += fields.indexOf("favorite") != -1 ? `favorite=${track_info.favorite},\n` : '' 
        sql += fields.indexOf("color") != -1 ? `color=${STRING(track_info.color)},\n` : '' 
        sql += fields.indexOf("comments") != -1 ? `comments=${STRING(addslashes(track_info.comments))},\n` : '' 
        sql += fields.indexOf("cover_medium") != -1 ? `cover_medium=${STRING(addslashes(track_info.cover_medium))},\n` : ''
        sql += fields.indexOf("cover_small") != -1 ? `cover_small=${STRING(addslashes(track_info.cover_small))},\n` : '' 
        sql += fields.indexOf("cover_large") != -1 ? `cover_large=${STRING(addslashes(track_info.cover_large))},\n` : '' 
        sql += fields.indexOf("cover_original") != -1 ? `cover_original=${STRING(addslashes(track_info.cover_original))},\n` : '' 
        sql += fields.indexOf("stream_start") != -1 ? `stream_start=${track_info.stream_start},\n` : '' 
        sql += fields.indexOf("stream_end") != -1 ? `stream_end=${track_info.stream_end},\n` : '' 
        sql += fields.indexOf("stream_length") != -1 ? `stream_length=${track_info.sttream_length},\n` : ''
        sql += fields.indexOf("disabled") != -1 ? `disabled=${track_info.disabled},\n` : '' 
        sql += fields.indexOf("grouping") != -1 ? `grouping=${STRING(addslashes(track_info.grouping))}\n` : ''
        sql += `date_modified=${DATE(new Date())},\n` 
        sql += `WHERE id=${id}`
        this.$QUERY(sql, () => {
            this.dispatch('track_data_updated', id, track_info)
        })
    }


    get_queue_boundary_positions (cont){
        sql = "SELECT min(position) as min, max(position) as max FROM session_queue WHERE status='pending'"
        this.$QUERY(sql, function(result){
            cont(result[0].min, result[0].max)
        })
    }


    // add_selection_to_queue: function () {
    //     var id = $$('display_list').getSelectedId().id;
    //     add_id_to_queue(id,
    //         function () {
    //             DB.get_queue_track(id,
    //                 function (result) {
    //                     $$('queue_list').add(result[0]);
    //                     $$('display_list').addRowCss(id, 'unavailable_track');
    //                     //$$('suggestion_list').addCss(id, 'unavailable_track');
    //                     update_queue_labels();
    //                     //u pdate_suggestions();                        
    //                 }
    //             )
    //         }
    //     )
    // },

    add_id_to_short_list(id) {
        //var id = $$('display_list').getSelectedId().id;
        sql = `SELECT 1 FROM short_listed_tracks WHERE track_id=${id} LIMIT 1`;
        this.$QUERY(sql,
            function (err, result){
                if (result.length == 0){
                    insert_sql = `INSERT INTO short_listed_tracks (track_id) VALUES (${id})`;
                    this.$QUERY(insert_sql, 
                        (result) => {
                            this.dispatch("track-added-to-short-list-success")
                        // if (error) throw error;
                        // console.log('FOO')
                        // webix.message({
                        //     text:"Added track to the short list",
                        //     type:"info",
                        //     expire: 3000,
                        //     id:"message1"
                        // });

                    });
                } else {
                    this.dispatch("track-added-to-short-list-error", "Track already in the short list")
                //     webix.message({
                //         text:"Track is already in the short list",
                //         type:"info",
                //         expire: 3000,
                //         id:"message1"
                //     });
                }
            }
        )
    }

    add_id_to_unavailable (id) {
        // var id = $$('display_list').getSelectedId().id;
        this.$QUERY(
            `SELECT 1 FROM unavailable_tracks WHERE track_id=${id} LIMIT 1`,
            function (result) {
                //if (error) throw error;
                if (result.length == 0) {
                    this.$QUERY(
                        `INSERT INTO unavailable_tracks (track_id) VALUES (${id})`,
                        () => {
                            this.dispatch("track-id-unavailable", id)
                        }
                        // function (result) {
                        //     //if (error) throw error;
                        //     $$('display_list').addRowCss(id, 'unavailable_track');
                        //     //$$('suggestion_list').addCss(id, 'unavailable_track');

                        // }
                    )
                }
            }
        )
    }

    remove_id_from_unavailable (id) {
        // var id = $$('display_list').getSelectedId().id;
        // console.log(`DELETE FROM unavailable_tracks WHERE track_id=${id}`)
        this.$QUERY(
            `SELECT 1 FROM unavailable_tracks WHERE track_id=${id} LIMIT 1`,
            function (result) {
                // if (error) throw error;
                if (result.length > 0) {
                    this.$QUERY(
                        `DELETE FROM unavailable_tracks WHERE track_id=${id}`,
                        () => {
                            this.dispatch("track-id-available", id)
                        }

                        // function (result) {
                        //     // if (error) throw error;
                        //     $$('display_list').removeRowCss(id, 'unavailable_track');
                        //     $$('display_list').getItem(id).$css="";
                        //     $$('display_list').refresh();
                        //     //$$('suggestion_list').removeCss(id, 'unavailable_track');

                        // }
                    )
                }
            }
        )
    }

    
    move_queue_element (from_position, to_position, when_done) {
        this.get_queue_boundary_positions(
            function (min, max) {
                new_position = Math.min(Math.max(to_position, min), max);
                if (new_position != from_position) {
                    this.$QUERY(
                        `UPDATE session_queue SET position=0 WHERE position=${from_position}`,
                        function(result) {
                            // if (err) throw err;
                            this.$QUERY(
                                `UPDATE session_queue SET position=position-1 WHERE position>${from_position}`,
                                function (result) {
                                    // if (err) throw err;
                                    this.$QUERY(
                                        `UPDATE session_queue SET position=position+1 WHERE position>=${new_position}`,
                                        function (result) {
                                            // if (err) throw err;
                                            this.$QUERY(
                                                `UPDATE session_queue SET position=${new_position} WHERE position=0`,
                                                () => {
                                                    this.dispatch("queue-element-moved", from_position, to_position)
                                                }
                                                // function (result) {
                                                //     // if (err) throw err;
                                                //     when_done(new_position);
                                                // }
                                            )
                                        }
                                    )
                                }
                            )
                        }
                    )
                }
            }
        )
    }
    //////////////////////////////////////////////////////////////////




    delete_queue_element (position, when_done) {
        this.$QUERY(
            `UPDATE session_queue SET position=0 WHERE position=${position}`,
            function(result) {
                this.$QUERY(
                    `UPDATE session_queue SET position=position-1 WHERE position>${position}`,
                    function (result) {
                        //if (err) throw err;
                        this.$QUERY(
                            `DELETE FROM session_queue WHERE position=0`,
                            () => {
                                this.dispatch("queue-element-deleted", position)
                            }
    
                            // function (result) {

                            //     // if (err) throw err;
                            //     when_done()
                            // }
                        )
                    }
                )
            }
        )
    }
    
    add_id_to_queue (track_id, when_done) {
        this.$QUERY(`SELECT 1 FROM session_queue WHERE track_id=${track_id} LIMIT 1`,
            function (result){
                if (result.length == 0){
                    this.$QUERY('SELECT max(id) + 1 as new_id, max(position)+1 as new_position FROM session_queue',
                        function (result) {
                            // if (!err){
                                var new_id = result[0].new_id ? result[0].new_id :1;
                                var new_position = result[0].new_id ? result[0].new_position :1;
                                this.$QUERY(`INSERT INTO session_queue (id, track_id, status, position)
                                            VALUES (${new_id}, ${track_id}, 'pending', ${new_position})`,
                                    () => {
                                        this.dispatch("queue-element-added", new_position)
                                    }
                                    // function (result) {
                                    //     // if (err) throw err;
                                    //     when_done();
                                    // }
                                );
                            //}
                        }
                    )
                }
            }
        );
    }
    
    //////////////////////////////////////////////////////////////
    //////////////////////////////////////////////////////////////
    //////////////////////////////////////////////////////////////


    save_session (name, location, address) {
        this.$QUERY(
            `SELECT track_id, start_time, end_time FROM session_queue WHERE status='played' ORDER BY position`,
            function (played_tracks) {
                //if (error) throw error;
                if (played_tracks.length > 0) {
                    this.$QUERY(
                        `SELECT max(id) + 1 AS new_session_id FROM sessions`,
                        function (result) {
                            //if (error) throw error;
                            new_session_id = result[0].new_session_id;
                            this.$QUERY(
                                `SELECT min(start_time) AS start, max(end_time) AS end FROM session_queue WHERE status='played'`,
                                function (start_end_time) {
                                    //if (error) throw error;
                                    format = webix.Date.dateToStr("%Y-%m-%d %H:%i:%s");
                                    start_date = format(start_end_time[0].start);
                                    end_date = format(start_end_time[0].end);
                                    this.$QUERY(
                                        `INSERT INTO sessions (id, event_name, start_date, end_date, location, address)
                                         VALUES (${new_session_id}, "${name}", '${start_date}', '${end_date}', "${location}", "${address}")`,
                                         function (x){
                                             //if (error) throw error;
                                             session_data = [];
                                             relation_data = [];
    
                                             for(var i =0; i<played_tracks.length; i++){
                                                 start_time = format(played_tracks[i].start_time);
                                                 end_time = format(played_tracks[i].start_time);
                                                 session_data.push(`(${new_session_id}, ${played_tracks[i].track_id}, '${start_time}', '${end_time}', ${i+1})`)
                                                 if (i+1 < played_tracks.length) {
                                                     relation_time = format(played_tracks[i+1].start_time);
                                                     relation_data.push(`(${played_tracks[i].track_id}, ${played_tracks[i+1].track_id}, 'PLAYED_IN_SET', 1, '${relation_time}')`)
                                                 }
                                             }
                                             this.$QUERY(`INSERT INTO session_tracks (session_id, track_id, start_time, end_time, position) VALUES ${session_data.join(',')}`,
                                                 function (r) {
                                                     //if (error) throw error;
                                                     this.$QUERY(`INSERT INTO track_relations (track_id, related_track_id, reason, count, date) VALUES ${relation_data.join(',')} ON DUPLICATE KEY UPDATE count=count+1`,
                                                         function (r) {
                                                             //if (error) throw error;
                                                             this.$QUERY(`DELETE FROM session_queue WHERE status='played'`,
                                                                 function (r) {
                                                                     //if (error) throw error;
                                                                     this.$QUERY(`SELECT min(position) as first FROM session_queue`,
                                                                        function (result) {
                                                                            //if (error) throw error;
                                                                            this.$QUERY(`UPDATE session_queue SET status='pending', start_time=NULL, end_time=NULL, position=position-(${result[0].first}-1)`,
                                                                                () => {
                                                                                    this.dispatch("session-saved", name, location, address)
                                                                                }
                                                                            // function (r) {
                                                                                //     //if (error) throw error;
                                                                                // }
                                                                            )
                                                                        }
                                                                     )
                                                                 }
                                                             )
                                                         }
                                                     )
                                                 }
                                             )
                                         }
                                    )
                                }
                            )
                        }
                    )
                }
            }
        )
    }
    
    mark_as_played(queue_position, continuation) {
        current_time = webix.Date.dateToStr('%Y-%m-%d %H:%i:%s')(new Date());
        this.$QUERY(
            `UPDATE session_queue SET status='played', end_time='${current_time}' WHERE position=${queue_position}`,
            function (result) {
                this.$QUERY(
                    `SELECT wait_time FROM settings`,
                    function (result) {
                        if (resule.length == 0) {
                            next_track_delay = 5;
                        } else {
                            next_track_delay = result[0].wait_time;
                        }
                        if (continuation) {
                            continuation(next_track_delay);
                        }
                    }
                )
            }
        )
    }
    
    get_next_track() {
        this.$QUERY(
            `SELECT min(position) as next_position FROM session_queue WHERE status='pending' GROUP BY status`,
            function (result) {
                //if (error) throw error;
                position = result[0].next_position;
                current_time = webix.Date.dateToStr('%Y-%m-%d %H:%i:%s')(new Date());
                this.$QUERY(
                    `UPDATE session_queue SET status='playing', start_time='${current_time}' WHERE position=${position}`,
                    function (result) {
                        //if (error) throw error;
                        this.$QUERY(
                            `SELECT track_id FROM session_queue WHERE position=${position}`,
                            function (result) {
                                //if (error) throw error;
                                track_id = result[0].track_id;
                                this.$QUERY(
                                    `SELECT title, artist, album, bpm, file_name, cover_small, stream_start, stream_end, settings.db_music_cache as music_root,
                                     settings.db_image_cache as image_root FROM tracks left join settings on 1 WHERE tracks.id=${track_id} LIMIT 1`,
                                    function (result) {
                                        //if (error) throw error;
                                        result = result[0];
                                        file_name = path.join(result.music_root, result.file_name);
                                        stream_length = (result.stream_end-result.stream_start) / 1000000000;
                                        $$('main-title').define('label', result.title)
                                        $$('main-title').refresh()
                                        $$('main-artist').define('label', `${result.artist} - ${result.album}`)
                                        $$('main-artist').refresh()
                                        if (result.cover_small == null) {
                                            cover_source = "../resources/images/default_album_cover.png"
                                        } else {
                                            cover_source = `file://${result.image_root}/${result.cover_small}`;
                                        }
                                        var cover_image = `<img style="margin:0px; padding:0px;" src="${cover_source}" height='58' width='58'></img>`
                                        $$('main-cover-image').define('template', cover_image);
                                        $$('main-cover-image').refresh();
                                        current_queue_position = position;
                                        $$('queue_list').remove($$('queue_list').getFirstId())
                                        update_queue_labels();
                                        main_play(file_name, result.stream_start, result.stream_end)
    
                                    }
                                )
                            }
                        )
                    }
                )
            }
        )
    }
    




}