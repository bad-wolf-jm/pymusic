

class Playlist:
    def __init__(self, library):
        self._library = library

    def get_tracks(self):
        return self._library.values()


class MainPlaylist(Playlist):
    pass


class FilteredPlaylist(Playlist):
    def __init__(self, library, field = None, comparison = None, value = None):
        Playlist.__init__(self, library)
        self._field = field
        self._comparison = comparison
        self._value = value


    def _contains(self, track):
        if self._field is not None:
            try:
                foo = getattr(track.metadata, self._field)
                #print foo, self._value
                i = foo.rfind(self._value)
                if i > -1:
                    return True
                return False
            except Exception, details:
                print details
                
                return False


    def get_tracks(self):
        try:
            cmpr = getattr(self, "_"+self._comparison)
        except Exception, details:
            print details
            return []
        ret_val = []
        for t in self._library.values():
            try:
                if cmpr(t):
                    ret_val.append(t)
            except Exception, details:
                print details
                pass
        return ret_val
