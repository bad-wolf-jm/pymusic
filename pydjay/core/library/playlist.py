import os

class Playlist(object):
    def __init__(self, library, name):
        super(Playlist, self).__init__()
        #self._path          = path
        self._tracks        = None
        self._name          = name
        self._library       = library
        self._is_editable   = True
        self._is_modifiable = True
        self._is_modified   = False

    @property
    def name(self):
        return self._name

    @property
    def is_editable(self):
        return self._is_editable


    @property
    def is_modifiable(self):
        return self._is_modifiable

    @property
    def is_modified(self):
        return self._is_modified

    def load(self):
        pass

    def __len__(self):
        self.load()
        return len(self._tracks) if self._tracks is not None else 0

    def get_tracks(self):
        return [x for x in self._tracks]

    def append(self, element):
        self.load()
        self._tracks.append(element)
        self._is_modified = True

    def insert(self, element, index):
        self.load()
        self._tracks.insert(index, element)
        self._is_modified = True

    def remove(self, element):
        self.load()
        self._tracks.remove(element)
        self._is_modified = True

    def remove_all(self, element, index):
        self.load()
        self._tracks = []
        self._is_modified = True

    def save(self):
        pass


class FilePlaylist(Playlist):
    def __init__(self, library, path, name):
        super(FilePlaylist, self).__init__(library, name)
        self._path = path
        #self._tracks = None
        #self._name = name
        #self._library = library

    @property
    def name(self):
        return self._name

    def load(self):
        if self._tracks is None:
            path = os.path.join(self._path, self.name+'.m3u')
            self._tracks = []
            if os.path.exists(path):
                file_ = open(path, 'rU')
                for bar in file_.readlines():
                    try:
                        self._tracks.append(self._library[bar.strip('\n')])
                    except:
                        pass
    def __len__(self):
        self.load()
        return len(self._tracks)

    def get_tracks(self):
        return [x for x in self._tracks]

    def append(self, element):
        self.load()
        self._tracks.append(element)

    def insert(self, element, index):
        self.load()
        self._tracks.insert(element, index)

    def remove(self, element, index):
        self.load()
        self._tracks.remove(element)

    def remove_all(self, element, index):
        self.load()
        self._tracks = []

    def save(self):
        if self._tracks is not None:
            path = os.path.join(self._path, name+'m3u')
            file_ = open(path, '')
            for bar in self._tracks:
                file_.write(bar.location)

class MainPlaylist(Playlist):
    def load(self):
        pass

    def save(self):
        pass

class TrackList(Playlist):
    def __init__(self, name, tracks):
        super(TrackList, self).__init__(None, name)
        self._tracks = tracks

#    def load(self):
#        pass

#    def save(self):
#        pass


class FilteredPlaylist(Playlist):
    def __init__(self, library, field = None, comparison = None, value = None):
        super(FilteredPlaylist, self).__init__(library, value)
        self._field = field
        self._comparison = comparison
        self._value = value


    def load(self):
        if self._tracks is None:
            self._tracks = []
            try:
                cmpr = getattr(self, "_"+self._comparison)
            except Exception, details:
                return None
            ret_val = []
            for t in self._library.values():
                try:
                    if cmpr(t):
                        self._tracks.append(t)
                except Exception, details:
                    pass

#    def append(self, element):
#        pass

#    def insert(self, element, index):
#        pass

#    def remove(self, element, index):
#        pass

#    def remove_all(self, element, index):
#        pass

#    def save(self):
#        pass

    def _contains(self, track):
        if self._field is not None:
            try:
                foo = getattr(track.metadata, self._field)
                i = foo.rfind(self._value)
                if i > -1:
                    return True
                return False
            except Exception, details:
                return False

    def _equals(self, track):
        if self._field is not None:
            try:
                foo = getattr(track.metadata, self._field)
                return foo == self._value
            except Exception, details:
                #print details
                return False


    def _true(self, track):
        return True

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
