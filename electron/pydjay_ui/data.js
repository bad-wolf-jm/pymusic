var display_list_fields = 'id, favorite, disabled as enabled, title, artist, album, genre, grouping, rating, bpm, stream_length, count(session_tracks.track_id) as play_count,  MAX(session_tracks.start_time) AS last_played';

function DataProvider() {
    var self = this

    self.get_all_tracks = function (k) {
        var sql =`SELECT availability.track_id IS NULL as available, ${display_list_fields} FROM tracks LEFT JOIN session_tracks
        ON tracks.id = session_tracks.track_id LEFT JOIN ((select track_id from unavailable_tracks) UNION
        (select track_id from session_queue)) availability ON availability.track_id=tracks.id GROUP BY id ORDER BY title`;
        $QUERY(sql, k);
    }

    self.get_playlist_tracks = function (id, k) {
        var sql = `SELECT availability.track_id IS NULL as available, playlist_tracks.track_id, favorite, disabled as enabled, title, artist,
                   album, genre, rating, bpm, stream_length, foo.play_count, cover_small as cover, settings.db_image_cache as image_root, 
                   max_play_times.time as last_played FROM playlist_tracks JOIN
                   (SELECT * FROM tracks JOIN (SELECT id as id_2, count(session_tracks.track_id) as play_count
                   FROM tracks LEFT JOIN session_tracks ON tracks.id = session_tracks.track_id GROUP BY id) play_counts
                   ON tracks.id=play_counts.id_2) foo ON playlist_tracks.track_id=foo.id LEFT JOIN
                   ((select track_id from unavailable_tracks) UNION (select track_id from session_queue)) availability
                   ON availability.track_id=playlist_tracks.track_id LEFT JOIN (SELECT track_id, MAX(start_time) AS time
                   FROM session_tracks GROUP BY track_id) max_play_times ON playlist_tracks.track_id = max_play_times.track_id
                   LEFT JOIN settings on 1 WHERE playlist_tracks.playlist_id=${id} ORDER BY title`;
        $QUERY(sql, k)        
    }

    self.get_session_tracks = function (id, k) {
        var sql = `SELECT availability.track_id IS NULL as available,  id, favorite, disabled as enabled, title, artist,
                   album, genre, rating, bpm, stream_length, foo.play_count, max_play_times.time as last_played
                   FROM session_tracks JOIN
                   (SELECT * FROM tracks JOIN (SELECT id as id_2, count(session_tracks.track_id) as play_count
                   FROM tracks JOIN session_tracks ON tracks.id = session_tracks.track_id GROUP BY id) play_counts ON
                   tracks.id=play_counts.id_2) foo ON session_tracks.track_id=foo.id LEFT JOIN
                   ((select track_id from unavailable_tracks) UNION (select track_id from session_queue)) availability ON
                   availability.track_id=session_tracks.track_id LEFT JOIN (SELECT track_id, MAX(start_time) AS time
                   FROM session_tracks GROUP BY track_id) max_play_times ON id = max_play_times.track_id
                   WHERE session_tracks.session_id=${id}`;
        $QUERY(sql, k)
    }

    self.get_never_played_tracks = function(k) {
        var sql =`SELECT * FROM (SELECT availability.track_id IS NULL as available, ${display_list_fields} FROM tracks LEFT JOIN session_tracks ON
            tracks.id = session_tracks.track_id LEFT JOIN
            (select track_id from session_queue) availability ON availability.track_id=tracks.id GROUP BY id ORDER BY title) q WHERE q.play_count = 0`;
        $QUERY(sql, k)
    }

    self.get_played_tracks = function(k) {
        var sql =`SELECT * FROM (SELECT availability.track_id IS NULL as available, ${display_list_fields} FROM tracks LEFT JOIN session_tracks ON
            tracks.id = session_tracks.track_id LEFT JOIN
            (select track_id from session_queue) availability ON availability.track_id=tracks.id GROUP BY id ORDER BY title) q WHERE q.play_count != 0`;
        $QUERY(sql, k)
    }

    self.get_shortlisted_tracks = function (k) {
        var sql =`SELECT availability.track_id IS NULL as available, ${display_list_fields}
                  FROM tracks LEFT JOIN session_tracks ON tracks.id = session_tracks.track_id
                  JOIN short_listed_tracks ON tracks.id=short_listed_tracks.track_id LEFT JOIN ((select track_id from unavailable_tracks) UNION
                  (select track_id from session_queue)) availability ON availability.track_id=tracks.id GROUP BY id ORDER BY title`;
        $QUERY(sql, k)
    }
}