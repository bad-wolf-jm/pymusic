#init
import os
import cPickle as pickle
import time
from track import load_file, Track
from playlist import MainPlaylist, FilteredPlaylist, Playlist, TrackList, FilePlaylist
from queue import PlayQueue
from short_list import ShortList
from track_set import TrackSet

class MusicLibrary(object):

    def __init__(self, root_folder = None):
        super(MusicLibrary, self).__init__()
        self._root_folder = root_folder
        self._state_folder = os.path.join(self._root_folder, 'state')

        self._short_list         = ShortList(self, self._state_folder, 'short_list', display_name = 'Short list')
        self._main_queue         = PlayQueue(self, self._state_folder, 'queue')
        self._current_session    = FilePlaylist(self, self._state_folder, 'current_session', auto_save = True,  display_name = 'Current session')
        self._unavailable_tracks = TrackSet(self, self._state_folder, 'unavailable_tracks', auto_save = True)
        self._sessions           = {}
        self._playlists          = {}
        self._library            = {}
        self._genres_count       = {}
        self._styles_count       = {}

        structure = ['state', 'sessions', 'image_cache', 'wave_cache', 'playlists']

        for x in structure:
            path = os.path.join(self._root_folder, x)
            if not os.path.exists(path):
                os.makedirs(path)

        if os.path.exists(os.path.join(self._root_folder, "library.data")):
            foo = open(os.path.join(self._root_folder, "library.data"))
            _tracks = pickle.load(foo)
            for key, location, info, metadata in _tracks:
                self._library[key] = (location, info, metadata)
        self._modified = False

        playlist_folder = os.path.join(self._root_folder, "playlists")
        for playlist in os.listdir(playlist_folder):
            if playlist.endswith('.m3u'):
                name, ext = os.path.splitext(playlist)
                self._playlists[name] = FilePlaylist(self, playlist_folder, name)

        session_folder = os.path.join(self._root_folder, "sessions")
        for session in os.listdir(session_folder):
            if session.endswith('.m3u'):
                name, ext = os.path.splitext(session)
                self._sessions[name] = FilePlaylist(self, session_folder, name)


        for loc, info, metadata in self._library.values():
            sty = metadata.get('style', 'N/A')
            gen = metadata.get('genre', 'N/A')
            if sty not in self._styles_count:
                self._styles_count[sty] = 0
            if gen not in self._genres_count:
                self._genres_count[gen] = 0
            self._styles_count[sty] += 1
            self._genres_count[gen] += 1

    def __getitem__(self, index):
        return Track(*self._library[index])

    def iterate_tracks(self):
        for key in self._library:
            yield self[key]

    def save(self):
        if self._root_folder is not None:
            foo = open(os.path.join(self._root_folder, "library.data"), "w")
            tracks = [(key, self._library[key][0], self._library[key][1], self._library[key][2]) for key in _library]
            pickle.dump(tracks, foo)
            foo.close()

    def add_file(self, filename):
        if os.path.exists(filename):
            if filename not in _library and filename.endswith('.mp3'):
                ii = load_file(filename)
                _library[filename] = ii

    def get_main_playlist(self, name):
        return TrackList(name, [self[x] for x in self._library])

    def get_all_styles(self):
        styles = set([])
        for loc, info, metadata in self._library.values():
            styles.add(metadata.get('style', None))
        styles = sorted(list(styles))
        return [self.get_style_by_name(g) for g in styles]

    def get_style_by_name(self, name):
        return FilteredPlaylist(self, 'style', 'equals', name, self._styles_count.get(name, None))

    def get_all_genres(self):
        genres = set([])
        for loc, info, metadata in self._library.values():
            genres.add(metadata.get('genre', None))
        genres = sorted(list(genres))
        return [self.get_genre_by_name(g) for g in genres]

    def get_genre_by_name(self, name):
        return FilteredPlaylist(self, 'genre', 'equals', name, self._genres_count.get(name, None))


    def get_all_playlists(self):
        return [self._playlists[x] for x in self._playlists]

    def get_all_sessions(self):
        return [self._sessions[x] for x in self._sessions]

    def get_current_session(self, name):
        return TrackList(name, self._current_session.track_list)
