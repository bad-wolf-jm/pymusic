import os
#import time
#from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty
#from pydjay.library import save_to_current_session
#from kivy.logger import Logger
#import pydjay.bootstrap

class SessionManager(EventDispatcher):
    def __init__(self, session_filename, playlists_folder, *args, **kw):
        super(MainPlayerDeck, self).__init__(*args, **kw)
        self._playlist_folder     = session_folder
        self._session_filename    = playlist_filename
        self._played_tracks       = set([])
        self._unavailable_tracks  = set([])
        self.register_event_type('current_session_changed')
        self.register_event_type('played_tracks_changed')

    def has_played(self, location):
        if self.track is not None and (location == self._track.track.location):
            return True
        return (location in self._current_session) or (location in self._unavailable_tracks)

    def add_unavailable(self, location):
        self._unavailable_tracks.add(location)
        self.dispatch("current_session_changed")

    def remove_unavailable(self, location):
        try:
            self._unavailable_tracks.remove(location)
            self.dispatch("current_session_changed")
        except:
            pass
        
    def add_to_current_session(self, track):
        current_session = self._session_filename
        if not os.path.exists(current_session):
            foo = open(current_session, 'w')
        else:
            foo = open(current_session, 'a')

        if track.location is not None:
            foo.write(track.location+'\n')
            self._played_tracks.append(location)
            self.dispatch("current_session_changed")
            self.dispatch("played_tracks_changed")
            
        foo.close()

    def save_current_session(self, file_name):
        current_session = self._session_filename
        if os.path.exists(current_session):
            foo = open(current_session, 'rU').readlines()
            bar = [x for x in foo if x != '\n']

            if os.path.exists(file_name + '.m3u'):
                index = 1
                path = file_name
                while os.path.exists(path + " - "+ str(index)+ '.m3u'):
                    index += 1
                file_name = path+" - "+str(index)
            session = open(file_name + '.m3u', 'w')
            for x in bar:
                session.write(x)
            session.close()
            os.unlink(current_session)
            self._played_tracks = set([])
            self.dispatch("current_session_changed")
            self.dispatch("played_tracks_changed")
