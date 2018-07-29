
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
                    LEFT JOIN ((SELECT track_id 
                                FROM   unavailable_tracks) 
                            UNION 
                            (SELECT track_id 
                                FROM   session_queue)) availability 
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
        sql += ` WHERE tracks.id=${id} ORDER BY title`
        $QUERY(sql, k)
    }

    self.get_all_tracks = function (k) {
        var sql =self.base_track_view_sql()
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
        var tracks_sql = `(${self.base_track_view_sql()}) tracks_view`
        var sql = `SELECT session_queue.position AS position, \`tracks_view\`.* 
                    FROM session_queue 
                    JOIN ${tracks_sql} 
                    ON tracks_view.id = session_queue.track_id 
                    WHERE session_queue.status='pending' 
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
        sql += `date_modified=${DATE(new Date())}\n` 
        sql += `WHERE id=${id}`
        $QUERY(sql, k)
    }
}