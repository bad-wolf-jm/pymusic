
function addslashes(s) {
    if (s == null) return null;
    o = ""
    d = {'"': '\\"',
         "'": "\\'",
         "\0":"\\\0",
         "\\": "\\\\"}

    for (var i=0; i<s.length; i++) {
        if (s[i] in d) {
            o += d[s[i]]
        } else {
            o += s[i]
        }
    }
    return o
}

function none_to_null(v) {
    return  (v == null) ? null : v
}

function none_to_zero(v) {
    return  (v == null) ? 0 : v
}

function bool_to_int(b) {
    return b ? 1 : 0
}

function STRING(s) {
    return (s != null) ? `'${s}'` : 'NULL'
}

function DATE(s) {
    pad = function(num) {
        var norm = Math.floor(Math.abs(num));
        return (norm < 10 ? '0' : '') + norm;
    };
    d = `${s.getFullYear()}-${pad(s.getMonth()+1)}-${pad(s.getDate())}T${pad(s.getHours())}:${pad(s.getMinutes())}:${pad(s.getSeconds())}`
    return `'${d}'`
}

function DataProvider() {
    var self = this

    self.base_track_view_sql = function () {
        return `SELECT availability.track_id IS NULL AS available, 
                    tracks.id                     AS id, 
                    tracks.id                     AS track_id, 
                    tracks.favorite               AS favorite, 
                    tracks.disabled               AS enabled, 
                    tracks.title                  AS title, 
                    tracks.artist                 AS artist, 
                    tracks.file_name               AS file_name, 
                    tracks.stream_start           AS stream_start, 
                    tracks.stream_end             AS stream_end, 
                    tracks.track_length           AS track_length, 
                    tracks.grouping               AS grouping, 
                    tracks.year                   AS year, 
                    tracks.color                  AS color, 
                    tracks.album                  AS album, 
                    tracks.genre                  AS genre, 
                    tracks.rating                 AS rating, 
                    tracks.bpm                    AS bpm, 
                    tracks.stream_length          AS stream_length, 
                    foo.play_count                AS play_count, 
                    tracks.cover_small            AS cover, 
                    settings.db_image_cache       AS image_root, 
                    settings.db_music_cache       AS music_root, 
                    max_play_times.time           AS last_played 
            FROM    tracks 
                    JOIN (SELECT * 
                        FROM   tracks 
                                JOIN (SELECT id                            AS id_2, 
                                            COUNT(session_tracks.track_id) AS play_count 
                                    FROM   tracks 
                                            LEFT JOIN session_tracks 
                                                    ON tracks.id = session_tracks.track_id 
                                    GROUP  BY id) play_counts 
                                ON tracks.id = play_counts.id_2) foo 
                    ON tracks.id = foo.id 
                    LEFT JOIN ((SELECT track_id FROM   unavailable_tracks) 
                                UNION 
                                (SELECT track_id FROM   session_queue)) availability 
                    ON availability.track_id = tracks.id 
                    LEFT JOIN (SELECT track_id, 
                                    MAX(start_time) AS time 
                            FROM   session_tracks 
                            GROUP  BY track_id) max_play_times 
                        ON tracks.id = max_play_times.track_id 
                    LEFT JOIN settings 
                        ON 1 `
    }
    
    self.get_track_by_id = function (id, k) {
        sql = self.base_track_view_sql()
        sql += ` WHERE tracks.id=${id}`
        $QUERY(sql, k)
    }

    self.get_all_tracks = function (k) {
        let sql = self.base_track_view_sql()
        sql += ` ORDER BY title`
        $QUERY(sql, k);
    }

    self.get_playlist_tracks = function (id, k) {
        var tracks_sql = `(${self.base_track_view_sql()}) tracks_view`
        var sql = `SELECT \`tracks_view\`.* 
                    FROM playlist_tracks 
                    JOIN ${tracks_sql} 
                    ON playlist_tracks.track_id=tracks_view.id 
                    WHERE playlist_tracks.playlist_id=${id} ORDER BY title`
        $QUERY(sql, k)        
    }



    self.get_session_tracks = function (id, k) {
        var tracks_sql = `(${self.base_track_view_sql()}) tracks_view`
        var sql = `SELECT \`tracks_view\`.* 
                    FROM session_tracks 
                    JOIN ${tracks_sql} 
                    ON session_tracks.track_id=tracks_view.id 
                    WHERE session_tracks.session_id=${id} 
                    ORDER BY session_tracks.position`
        $QUERY(sql, k)
    }

    self.get_never_played_tracks = function(k) {
        var tracks_sql = `(${self.base_track_view_sql()}) tracks_view`
        var sql = `SELECT \`tracks_view\`.* 
                    FROM ${tracks_sql} 
                    WHERE tracks_view.play_count = 0 
                    ORDER BY tracks_view.title`
        $QUERY(sql, k)
    }

    self.get_played_tracks = function(k) {
        var tracks_sql = `(${self.base_track_view_sql()}) tracks_view`
        var sql = `SELECT \`tracks_view\`.* 
                    FROM ${tracks_sql} 
                    WHERE tracks_view.play_count != 0 
                    ORDER BY tracks_view.title`
        $QUERY(sql, k)
    }

    self.get_shortlisted_tracks = function (k) {
        var tracks_sql = `(${self.base_track_view_sql()}) tracks_view`
        var sql = `SELECT \`tracks_view\`.* 
                    FROM short_listed_tracks 
                    JOIN ${tracks_sql} 
                    ON tracks_view.id=short_listed_tracks.track_id 
                    ORDER BY tracks_view.title`
        $QUERY(sql, k)
    }

    self.get_unavailable_tracks = function (k) {
        var tracks_sql = `(${self.base_track_view_sql()}) tracks_view`
        var sql = `SELECT \`tracks_view\`.* 
                    FROM unavailable_tracks 
                    JOIN ${tracks_sql} 
                    ON tracks_view.id = unavailable_tracks.track_id 
                    ORDER BY tracks_view.title`
         $QUERY(sql, k)
    }

    self.get_session_info = function (id, k) {
        $QUERY(`SELECT id, event_name as name, date(start_date) as date, counts.count as count FROM sessions 
        JOIN (select session_id, count(track_id) as count FROM session_tracks GROUP BY session_id) counts 
        ON sessions.id=counts.session_id WHERE sessions.id=${id}`, 
        (list) => {
            return k(list[0])
        })
    }


    self.get_sessions_list = function (k) {
        $QUERY(`SELECT id, event_name as name, date(start_date) as date, counts.count as count FROM sessions 
        JOIN (select session_id, count(track_id) as count FROM session_tracks GROUP BY session_id) counts 
        ON sessions.id=counts.session_id ORDER BY date ASC`, k)
    }

    self.get_group_info = function (id, k) {
        $QUERY(`SELECT playlists.id as id , playlists.name, IFNULL(counts.count, 0) as count FROM
        playlists LEFT JOIN (SELECT playlist_id, count(track_id) as count FROM playlist_tracks GROUP BY playlist_id) counts
        ON playlists.id=counts.playlist_id WHERE playlists.id=${id}`, 
        (list) => {
            return k(list[0])
        })
    }

    self.get_group_list = function (k) {
        $QUERY(`SELECT playlists.id as id , playlists.name, IFNULL(counts.count, 0) as count FROM
        playlists LEFT JOIN (SELECT playlist_id, count(track_id) as count FROM playlist_tracks GROUP BY playlist_id) counts
        ON playlists.id=counts.playlist_id ORDER BY name`, k)
    }
 
    self.get_queue_elements = function (k) {
        var tracks_sql = `(${self.base_track_view_sql()}) tracks_view`
        var sql = `SELECT session_queue.position AS position, \`tracks_view\`.* 
                    FROM session_queue 
                    JOIN ${tracks_sql} 
                    ON tracks_view.id = session_queue.track_id 
                    WHERE session_queue.status='pending' 
                    ORDER BY session_queue.position`
        $QUERY(sql, k)
    }

    self.get_played_queue_elements = function (k) {
        var tracks_sql = `(${self.base_track_view_sql()}) tracks_view`
        var sql = `SELECT session_queue.position AS position, \`tracks_view\`.* 
                    FROM session_queue 
                    JOIN ${tracks_sql} 
                    ON tracks_view.id = session_queue.track_id 
                    WHERE session_queue.status='played' 
                    ORDER BY session_queue.position`
        $QUERY(sql, k)
    }


    self.get_queue_track = function(id, k) {
        var tracks_sql = `(${self.base_track_view_sql()}) tracks_view`
        var sql = `SELECT session_queue.position AS position, \`tracks_view\`.* 
                   FROM session_queue 
                   JOIN ${tracks_sql} 
                   ON tracks_view.id = session_queue.track_id 
                   WHERE session_queue.status='pending' AND session_queue.track_id=${id} 
                   ORDER BY session_queue.position`
        $QUERY(sql, k)
    }

    self.get_suggested_tracks = function (k) {
        var tracks_sql = `(${self.base_track_view_sql()}) tracks_view`
        var sql = `SELECT \`tracks_view\`.* 
                    FROM ${tracks_sql} 
                    WHERE tracks_view.id IN 
                        (SELECT DISTINCT related_track_id 
                            FROM track_relations 
                            WHERE track_relations.track_id IN 
                                (SELECT track_id FROM session_queue WHERE status='pending'))`
        $QUERY(sql, k)
    }

    self.get_queue_duration = function (k) {
        $QUERY(`SELECT SUM(duration) as duration, COUNT(id) as count, AVG(wait_time) as wait_time FROM
        (SELECT 1 as id, tracks.stream_length as duration, session_queue.id as count, settings.wait_time as wait_time
        FROM tracks JOIN session_queue ON tracks.id=session_queue.track_id LEFT JOIN settings on 1
        WHERE session_queue.status='pending' OR session_queue.status='playing') dummy GROUP BY id`, k)
    }

    self.get_settings = function (k) {
       $QUERY("SELECT db_image_cache as image_root, db_music_cache as music_root, db_waveform_cache as waveform_root FROM settings",
            (settings) => {
                let S=settings[0]
                $QUERY("SELECT max(id) + 1 AS first_available_id FROM tracks",
                    (id_result) => {
                        if (id_result[0].first_available_id != null) {
                            S.next_id = id_result[0].first_available_id;
                        } else {
                            S.next_id = 1;
                        }
                        return k(S)
                    }
                )
            }
        )
    }

    self.add_track = function (track_info, k) {
        sql = `INSERT INTO tracks (
        id, title, artist, album, year, genre, bpm, rating, favorite, comments, waveform, cover_medium,
        cover_small, cover_large, cover_original, track_length, stream_start, stream_end, stream_length,
        date_added, date_modified, bitrate, samplerate, file_name, file_size, hash, category, description,
        disabled, original_file_name, grouping, color)
        VALUES (${track_info.id},${track_info.title}, ${track_info.artist}, ${track_info.album}, ${track_info.year},
        ${track_info.genre}, ${track_info.bpm}, ${track_info.rating}, ${track_info.favorite}, ${track_info.comments},
        ${track_info.waveform}, ${track_info.cover_medium}, ${track_info.cover_small}, ${track_info.cover_large},
        ${track_info.cover_original}, ${track_info.track_length}, ${track_info.stream_start}, ${track_info.stream_end},
        ${track_info.stream_length}, ${track_info.date_added}, ${track_info.date_modified}, ${track_info.bitrate},
        ${track_info.samplerate}, ${track_info.file_name}, ${track_info.file_size}, ${track_info.hash}, ${track_info.category},
        ${track_info.description}, ${track_info.disabled}, ${track_info.original_file_name}, ${track_info.grouping},  ${track_info.color})`
        $QUERY(sql, k)
    }

    self.update_track_data = function (id, track_info, k) {
        let sql = "UPDATE tracks SET "
        let fields = Object.keys(track_info);
        sql += fields.indexOf("title")          != -1 ? `title=${STRING(addslashes(track_info.title))},\n` : '' 
        sql += fields.indexOf("artist")         != -1 ? `artist=${STRING(addslashes(track_info.artist))},\n` : '' 
        sql += fields.indexOf("album")          != -1 ? `album=${STRING(addslashes(track_info.album))},\n` : '';
        sql += fields.indexOf("year")           != -1 ? `year=${track_info.year},\n` : '' 
        sql += fields.indexOf("genre")          != -1 ? `genre=${STRING(addslashes(track_info.genre))},\n` : '' 
        sql += fields.indexOf("bpm")            != -1 ? `bpm=${track_info.bpm},\n` : '' 
        sql += fields.indexOf("rating")         != -1 ? `rating=${track_info.rating},\n` : '' 
        sql += fields.indexOf("favorite")       != -1 ? `favorite=${track_info.favorite},\n` : '' 
        sql += fields.indexOf("color")          != -1 ? `color=${STRING(track_info.color)},\n` : '' 
        sql += fields.indexOf("comments")       != -1 ? `comments=${STRING(addslashes(track_info.comments))},\n` : '' 
        sql += fields.indexOf("cover_medium")   != -1 ? `cover_medium=${STRING(addslashes(track_info.cover_medium))},\n` : ''
        sql += fields.indexOf("cover_small")    != -1 ? `cover_small=${STRING(addslashes(track_info.cover_small))},\n` : '' 
        sql += fields.indexOf("cover_large")    != -1 ? `cover_large=${STRING(addslashes(track_info.cover_large))},\n` : '' 
        sql += fields.indexOf("cover_original") != -1 ? `cover_original=${STRING(addslashes(track_info.cover_original))},\n` : '' 
        sql += fields.indexOf("stream_start")   != -1 ? `stream_start=${track_info.stream_start},\n` : '' 
        sql += fields.indexOf("stream_end")     != -1 ? `stream_end=${track_info.stream_end},\n` : '' 
        sql += fields.indexOf("stream_length")  != -1 ? `stream_length=${track_info.sttream_length},\n` : ''
        sql += fields.indexOf("disabled")       != -1 ? `disabled=${track_info.disabled},\n` : '' 
        sql += fields.indexOf("grouping")       != -1 ? `grouping=${STRING(addslashes(track_info.grouping))}\n` : ''
        sql += `date_modified=${DATE(new Date())}\n` 
        sql += `WHERE id=${id}`
        $QUERY(sql, k)
    }

    self.get_queue_boundary_positions = function (cont){
        sql = "SELECT min(position) as min, max(position) as max FROM session_queue WHERE status='pending'"
        $QUERY(sql, function(result){
            //if (error) throw error;
            return cont(result[0].min, result[0].max)
        })
    }
    
    self.move_queue_element= function (from_position, to_position, when_done) {
        self.get_queue_boundary_positions(
            function (min, max) {
                new_position = Math.min(Math.max(to_position, min), max);
                if (new_position != from_position) {
                    $QUERY(
                        `UPDATE session_queue SET position=0 WHERE position=${from_position}`,
                        function(result) {
                            $QUERY(
                                `UPDATE session_queue SET position=position-1 WHERE position>${from_position}`,
                                function (result) {
                                    $QUERY(
                                        `UPDATE session_queue SET position=position+1 WHERE position>=${new_position}`,
                                        function (result) {
                                            $QUERY(
                                                `UPDATE session_queue SET position=${new_position} WHERE position=0`,
                                                function (result) {
                                                    when_done(new_position);
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
    
    self.delete_queue_element= function (position, when_done) {
        $QUERY(
            `UPDATE session_queue SET position=0 WHERE position=${position}`,
            function(result) {
                $QUERY(
                    `UPDATE session_queue SET position=position-1 WHERE position>${position}`,
                    function (result) {
                        $QUERY(
                            `DELETE FROM session_queue WHERE position=0`,
                            function (result) {
                                when_done()
                            }
                        )
                    }
                )
            }
        )
    }
    
    self.add_id_to_queue = function (track_id, when_done) {
        $QUERY(`SELECT 1 FROM session_queue WHERE track_id=${track_id} LIMIT 1`,
            function (result){
                if (result.length == 0){
                    $QUERY('SELECT max(id) + 1 as new_id, max(position)+1 as new_position FROM session_queue',
                        function (result) {
                            var new_id = result[0].new_id ? result[0].new_id :1;
                            var new_position = result[0].new_id ? result[0].new_position :1;
                            $QUERY(`INSERT INTO session_queue (id, track_id, status, position)
                                    VALUES (${new_id}, ${track_id}, 'pending', ${new_position})`,
                                function (result) {
                                    when_done();
                                }
                            );
                        }
                    )
                }
            }
        );
    }
    
    self.save_session = function (name, location, address, k) {
        $QUERY(`SELECT track_id, start_time, end_time FROM session_queue WHERE status='played' ORDER BY position`,
            function (played_tracks) {
                if (played_tracks.length > 0) {
                    $QUERY(
                        `SELECT max(id) + 1 AS new_session_id FROM sessions`,
                        function (result) {
                            new_session_id = result[0].new_session_id;
                            $QUERY(
                                `SELECT min(start_time) AS start, max(end_time) AS end FROM session_queue WHERE status='played'`,
                                function (start_end_time) {
                                    format = webix.Date.dateToStr("%Y-%m-%d %H:%i:%s");
                                    start_date = format(start_end_time[0].start);
                                    end_date = format(start_end_time[0].end);
                                    $QUERY(
                                        `INSERT INTO sessions (id, event_name, start_date, end_date, location, address)
                                         VALUES (${new_session_id}, "${name}", '${start_date}', '${end_date}', "${location}", "${address}")`,
                                         function (x) {
                                             session_data = [];
                                             relation_data = [];
    
                                             for(var i =0; i<played_tracks.length; i++){
                                                 start_time = format(played_tracks[i].start_time);
                                                 end_time = format(played_tracks[i].end_time);
                                                 session_data.push(`(${new_session_id}, ${played_tracks[i].track_id}, '${start_time}', '${end_time}', ${i+1})`)
                                                 if (i+1 < played_tracks.length) {
                                                     relation_time = format(played_tracks[i+1].start_time);
                                                     relation_data.push(`(${played_tracks[i].track_id}, ${played_tracks[i+1].track_id}, 'PLAYED_IN_SET', 1, '${relation_time}')`)
                                                 }
                                             }
                                             $QUERY(`INSERT INTO session_tracks (session_id, track_id, start_time, end_time, position) VALUES ${session_data.join(',')}`,
                                                 function (r) {
                                                     $QUERY(`INSERT INTO track_relations (track_id, related_track_id, reason, count, date) VALUES ${relation_data.join(',')} ON DUPLICATE KEY UPDATE count=count+1`,
                                                         function (r) {
                                                             $QUERY(`DELETE FROM session_queue WHERE status='played'`,
                                                                 function (r) {
                                                                     $QUERY(`SELECT min(position) as first FROM session_queue`,
                                                                        function (result) {
                                                                            $QUERY(`UPDATE session_queue SET status='pending', start_time=NULL, end_time=NULL, position=position-(${result[0].first}-1)`, k)
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
    
    self.add_id_to_short_list = function (id, k) {
        sql = `SELECT 1 FROM short_listed_tracks WHERE track_id=${id} LIMIT 1`;
        $QUERY(sql,
            function (result){
                if (result.length == 0){
                    insert_sql = `INSERT INTO short_listed_tracks (track_id) VALUES (${id})`;
                    $QUERY(insert_sql, k)
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

    self.add_id_to_unavailable = function (id, k) {
        $QUERY(
            `SELECT 1 FROM unavailable_tracks WHERE track_id=${id} LIMIT 1`,
            function (result) {
                if (result.length == 0) {
                    $QUERY(`INSERT INTO unavailable_tracks (track_id) VALUES (${id})`, k)
                }
            }
        )
    },

    self.remove_id_from_unavailable = function (id, k) {
        $QUERY(`SELECT 1 FROM unavailable_tracks WHERE track_id=${id} LIMIT 1`,
            function (result) {
                if (result.length > 0) {
                    $QUERY(`DELETE FROM unavailable_tracks WHERE track_id=${id}`, k)
                }
            }
        )
    }

    self.count_queue_elements = function (k) {
        $QUERY(`SELECT count(id) as queue_count FROM session_queue WHERE status='pending'`,
            function (result) {
                k(result[0].queue_count)
            }
        )
    }

    self.get_waiting_time = function (k) {
        $QUERY(`SELECT wait_time FROM settings`,
            (r) => {
                k(r[0].wait_time)
            }
        )
    }

    self.get_next_track_position = function (k) {
        $QUERY(`SELECT min(position) as next_position FROM session_queue WHERE status='pending' GROUP BY status`,
            function (result) {
                k(result[0].next_position)
            }
        )
    }

    self.start_playing = function (queue_position, k) {
        current_time = webix.Date.dateToStr('%Y-%m-%d %H:%i:%s')(new Date());
        $QUERY(`UPDATE session_queue SET status='playing', start_time='${current_time}' WHERE position=${queue_position}`,
            function (result) {
                $QUERY(`SELECT track_id FROM session_queue WHERE position=${queue_position}`,
                    function (result) {
                        self.get_track_by_id(result[0].track_id, k)
                    }
                )
            }
        )
    }

    self.mark_as_played = function(queue_position, continuation) {
        current_time = webix.Date.dateToStr('%Y-%m-%d %H:%i:%s')(new Date());
        $QUERY(`UPDATE session_queue SET status='played', end_time='${current_time}' WHERE position=${queue_position}`, continuation)
    }

    self.add_id_to_playlist = function(track_id, playlist_id, k) {
        $QUERY(`SELECT COUNT(*) as N FROM playlist_tracks WHERE track_id=${track_id} AND playlist_id=${playlist_id}`,
            (count) => {
                if (count[0].N == 0) {
                    $QUERY(`INSERT INTO playlist_tracks (playlist_id, track_id) VALUES (${playlist_id}, ${track_id})`, k)
                }
            }
        )
    }

    self.add_to_current_session = function (track_data, k) {
        k()
    }
}