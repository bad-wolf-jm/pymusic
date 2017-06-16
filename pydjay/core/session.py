import os
from kivy.event import EventDispatcher


class SessionManager(EventDispatcher):
    def __init__(self, library, *args, **kw):
        super(SessionManager, self).__init__(*args, **kw)
        #self._session_filename    = session_filename
        self._library             = library
        self._played_tracks_list  = []
        self._played_tracks       = set([])
        self._unavailable_tracks  = set([])
        self.register_event_type('on_current_session_changed')

    def on_current_session_changed(self, *a):
        pass

    def is_available(self, track):
        return (not self._library._unavailable_tracks.contains(track.location)) and (not self._library._current_session.contains(track.location))

    def add(self, track, played = True):
        self._library._unavailable_tracks.add(track.location)
        #self._tracks[track.location] = track

        if not played:
            self.dispatch("on_current_session_changed", self.played_tracks)
            return None

        #current_session = self._session_filename
        #if not os.path.exists(current_session):
        #    foo = open(current_session, 'w')
        #else:
        #    foo = open(current_session, 'a')
        #try:
        #    if track.location is not None:
        #        foo.write(track.location+'\n')
        self._library._current_session.append(track.location)
        #        self._played_tracks.add(track.location)
        self.dispatch("on_current_session_changed", self.played_tracks)
        #finally:
        #    foo.close()


    def remove(self, track):
        #try:
        if not self._library._current_session.contains(track.location): #) not in self._played_tracks:
            self._library._unavailable_tracks.remove(track.location)
            self.dispatch("on_current_session_changed", self.played_tracks)
        #except:
        #    pass

    @property
    def played_tracks(self):
        return self._library._current_session.track_list #[x for x in self._played_tracks_list]

#    def save_current_session(self, folder, file_name_prefix):
#        current_session = self._session_filename
#        if os.path.exists(current_session):
#            foo = open(current_session, 'rU').readlines()
#            bar = [x for x in foo if x != '\n']
#
#            file_name = os.path.join(folder, file_name_prefix)
#
#            if os.path.exists(file_name + '.m3u'):
#                index = 1
#                path = file_name
#                while os.path.exists(path + " - " + str(index)+ '.m3u'):
#                    index += 1
#                file_name = path + " - " + str(index) + ".m3u"
#            else:
#                file_name += '.m3u'
#
#            session = open(file_name, 'w')
#            for x in bar:
#                session.write(x)
#            session.close()
#            os.unlink(current_session)
#            self._played_tracks = set([])
#            self.dispatch("on_current_session_changed", self.played_tracks)
#
#    def set_current_session(self, session):
#        self._played_tracks = set([x.location for x in session])
#        self._unavailable_tracks = set([x.location for x in session])
#        self._played_tracks_list = [x for x in session]
#        self.dispatch("on_current_session_changed", self.played_tracks)
