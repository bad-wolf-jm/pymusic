var display_list_fields = 'id, favorite, disabled as enabled, title, artist, album, genre, grouping, rating, bpm, stream_length, count(session_tracks.track_id) as play_count,  MAX(session_tracks.start_time) AS last_played';

function DataProvider() {
    var self = this

    self.get_track_by_id = function (id, k) {
        $QUERY(`SELECT availability.track_id IS NULL as available, tracks.id as id, tracks.id as track_id, tracks.favorite, tracks.disabled as enabled, tracks.title, tracks.artist, tracks.file_name as file_name,
        tracks.stream_start as stream_start, tracks.stream_end as stream_end, tracks.track_length as track_length, tracks.grouping, tracks.year,
        tracks.album, tracks.genre, tracks.rating, tracks.bpm, tracks.stream_length, foo.play_count, tracks.cover_small as cover, settings.db_image_cache as image_root, settings.db_music_cache as music_root,
        max_play_times.time as last_played FROM tracks JOIN (SELECT * FROM tracks JOIN (SELECT id as id_2, count(session_tracks.track_id) as play_count
        FROM tracks LEFT JOIN session_tracks ON tracks.id = session_tracks.track_id GROUP BY id) play_counts ON tracks.id=play_counts.id_2) foo ON tracks.id=foo.id LEFT JOIN
        ((select track_id from unavailable_tracks) UNION (select track_id from session_queue)) availability ON availability.track_id=tracks.id LEFT JOIN 
        (SELECT track_id, MAX(start_time) AS time FROM session_tracks GROUP BY track_id) max_play_times ON tracks.id = max_play_times.track_id LEFT JOIN settings on 1 
        WHERE tracks.id=${id} ORDER BY title`, k)
    }

    self.get_all_tracks = function (k) {
        var sql =`SELECT availability.track_id IS NULL as available, ${display_list_fields} FROM tracks LEFT JOIN session_tracks
        ON tracks.id = session_tracks.track_id LEFT JOIN ((select track_id from unavailable_tracks) UNION
        (select track_id from session_queue)) availability ON availability.track_id=tracks.id GROUP BY id ORDER BY title`;
        $QUERY(sql, k);
    }

    self.get_playlist_tracks = function (id, k) {
        var sql = `SELECT availability.track_id IS NULL as available, playlist_tracks.track_id, playlist_tracks.track_id as id, favorite, disabled as enabled, 
        title, artist, album, genre, rating, bpm, stream_length, foo.play_count, cover_small as cover, 
        settings.db_image_cache as image_root, max_play_times.time as last_played FROM playlist_tracks JOIN
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

    self.get_unavailable_tracks = function (k) {
        var sql = `SELECT availability.track_id IS NULL as available, ${display_list_fields} FROM tracks LEFT JOIN session_tracks ON
        tracks.id = session_tracks.track_id JOIN unavailable_tracks ON tracks.id=unavailable_tracks.track_id LEFT JOIN
        (select track_id from session_queue) availability ON availability.track_id=tracks.id GROUP BY id ORDER BY title`
         $QUERY(sql, k)
    }

    self.get_sessions_list = function (k) {
        $QUERY(`SELECT id, event_name as name, date(start_date) as date, counts.count as count FROM sessions 
        JOIN (select session_id, count(track_id) as count FROM session_tracks GROUP BY session_id) counts 
        ON sessions.id=counts.session_id ORDER BY date ASC`, k)
    }

    self.get_group_list = function (k) {
        $QUERY(`SELECT playlists.id as id , playlists.name, IFNULL(counts.count, 0) as count FROM
        playlists LEFT JOIN (SELECT playlist_id, count(track_id) as count FROM playlist_tracks GROUP BY playlist_id) counts
        ON playlists.id=counts.playlist_id ORDER BY name`, k)
    }
 
    self.get_queue_elements = function (k) {
        $QUERY(`SELECT tracks.id as track_id, session_queue.id as id, session_queue.position, tracks.title, tracks.artist, tracks.album,
        tracks.bpm, tracks.stream_length, settings.db_image_cache as image_root, tracks.cover_small as cover, session_queue.position as position
        FROM (tracks LEFT JOIN settings ON 1) LEFT JOIN session_queue ON tracks.id=session_queue.track_id WHERE session_queue.status='pending'
        ORDER BY session_queue.position`, k)
    }

    self.get_queue_track = function(id, k) {
        $QUERY(`SELECT tracks.id as track_id, session_queue.position, tracks.title, tracks.artist, tracks.album, tracks.bpm,
        tracks.stream_length, settings.db_image_cache as image_root, tracks.cover_small as cover, session_queue.position as position
        FROM (tracks LEFT JOIN settings ON 1) LEFT JOIN session_queue ON tracks.id=session_queue.track_id
        WHERE session_queue.status='pending' AND session_queue.track_id=${id} ORDER BY session_queue.position`, k)
    }

    self.get_suggested_tracks = function (k) {
        $QUERY(`SELECT availability.track_id IS NULL as available, tracks.id as id, tracks.title, tracks.artist, tracks.album,
        tracks.bpm, tracks.stream_length, settings.db_image_cache as image_root, tracks.cover_small as cover
        FROM (tracks LEFT JOIN settings ON 1 LEFT JOIN ((select track_id from unavailable_tracks) UNION
        (select track_id from session_queue)) availability ON availability.track_id=tracks.id) WHERE tracks.id IN
        (SELECT DISTINCT related_track_id FROM track_relations WHERE track_id IN (SELECT track_id FROM session_queue WHERE status='pending'))
        ORDER BY title ASC`, k)
    }

    self.get_queue_duration = function (k) {
        $QUERY(`SELECT SUM(duration) as duration, COUNT(id) as count, AVG(wait_time) as wait_time FROM
        (SELECT 1 as id, tracks.stream_length as duration, session_queue.id as count, settings.wait_time as wait_time
        FROM tracks JOIN session_queue ON tracks.id=session_queue.track_id LEFT JOIN settings on 1
        WHERE session_queue.status='pending' OR session_queue.status='playing') dummy GROUP BY id`, k)
    }
}