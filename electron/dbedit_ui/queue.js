
function get_queue_boundary_positions(cont){
    sql = "SELECT min(position) as min, max(position) as max FROM session_queue WHERE status='pending'"
    db_connection.query(sql, function(error, result){
        if (error) throw error;
        return cont(result[0].min, result[0].max)
    })
}

function move_queue_element(from_position, to_position, when_done) {
    get_queue_boundary_positions(
        function (min, max) {
            new_position = Math.min(Math.max(to_position, min), max);
            if (new_position != from_position) {
                db_connection.query(
                    `UPDATE session_queue SET position=0 WHERE position=${from_position}`,
                    function(err, result) {
                        if (err) throw err;
                        db_connection.query(
                            `UPDATE session_queue SET position=position-1 WHERE position>${from_position}`,
                            function (err, result) {
                                if (err) throw err;
                                db_connection.query(
                                    `UPDATE session_queue SET position=position+1 WHERE position>=${new_position}`,
                                    function (err, result) {
                                        if (err) throw err;
                                        db_connection.query(
                                            `UPDATE session_queue SET position=${new_position} WHERE position=0`,
                                            function (err, result) {
                                                if (err) throw err;
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

function delete_queue_element(position, when_done) {
    db_connection.query(
        `UPDATE session_queue SET position=0 WHERE position=${position}`,
        function(err, result) {
             db_connection.query(
                `UPDATE session_queue SET position=position-1 WHERE position>${position}`,
                function (err, result) {
                    if (err) throw err;
                    db_connection.query(
                        `DELETE FROM session_queue WHERE position=0`,
                        function (err, result) {
                            if (err) throw err;
                            when_done()
                        }
                    )
                }
            )
        }
    )
}

function add_id_to_queue(track_id, when_done) {
    db_connection.query(`SELECT 1 FROM session_queue WHERE track_id=${track_id} LIMIT 1`,
        function (err, result){
            if (result.length == 0){
                db_connection.query('SELECT max(id) + 1 as new_id, max(position)+1 as new_position FROM session_queue',
                    function (err, result) {
                        if (!err){
                            var new_id = result[0].new_id ? result[0].new_id :1;
                            var new_position = result[0].new_id ? result[0].new_position :1;
                            db_connection.query(`INSERT INTO session_queue (id, track_id, status, position)
                                          VALUES (${new_id}, ${track_id}, 'pending', ${new_position})`,
                                function (err, result) {
                                    if (err) throw err;
                                    when_done();
                                }
                            );
                        }
                    }
                )
            }
        }
    );
}

function save_session(name, location, address) {
    db_connection.query(
        `SELECT track_id, start_time, end_time FROM session_queue WHERE status='played' ORDER BY position`,
        function (error, played_tracks) {
            if (error) throw error;
            if (played_tracks.length > 0) {
                db_connection.query(
                    `SELECT max(id) + 1 AS new_session_id FROM sessions`,
                    function (error, result) {
                        if (error) throw error;
                        new_session_id = result[0].new_session_id;
                        db_connection.query(
                            `SELECT min(start_time) AS start, max(end_time) AS end FROM session_queue WHERE status='played'`,
                            function (error, start_end_time) {
                                if (error) throw error;
                                format = webix.Date.dateToStr("%Y-%m-%d %H:%i:%s");
                                start_date = format(start_end_time[0].start);
                                end_date = format(start_end_time[0].end);
                                db_connection.query(
                                    `INSERT INTO sessions (id, event_name, start_date, end_date, location, address)
                                     VALUES (${new_session_id}, "${name}", '${start_date}', '${end_date}', "${location}", "${address}")`,
                                     function (error, x){
                                         if (error) throw error;
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
                                         db_connection.query(
                                             `INSERT INTO session_tracks (session_id, track_id, start_time, end_time, position) VALUES ${session_data.join(',')}`,
                                             function (error, r) {
                                                 if (error) throw error;
                                                 db_connection.query(
                                                     `INSERT INTO track_relations (track_id, related_track_id, reason, count, date) VALUES ${relation_data.join(',')} ON DUPLICATE KEY UPDATE count=count+1`,
                                                     function (error, r) {
                                                         if (error) throw error;
                                                         db_connection.query(
                                                             `DELETE FROM session_queue WHERE status='played'`,
                                                             function (error, r) {
                                                                 if (error) throw error;
                                                                 db_connection.query(
                                                                    `SELECT min(position) as first FROM session_queue`,
                                                                    function (error, result) {
                                                                        if (error) throw error;
                                                                        db_connection.query(
                                                                            `UPDATE session_queue SET status='pending', start_time=NULL, end_time=NULL, position=position-(${result[0].first}-1)`,
                                                                            function (error, r) {
                                                                                if (error) throw error;
                                                                                console.log('session saved');

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
                )
            }
        }
    )
}
