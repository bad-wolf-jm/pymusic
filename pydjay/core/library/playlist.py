import os

class Playlist(object):
    def __init__(self, library, name, auto_save = False):
        super(Playlist, self).__init__()
        self._tracks        = None
        self._name          = name
        self._library       = library
        self._is_editable   = True
        self._is_modifiable = True
        self._is_modified   = False
        self._auto_save     = auto_save
        self._track_indices = {}

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

    def contains(self, track_location):
        self.load()
        return (track_location in self._track_indices)


    def find(self, track):
        foo = [id(x) for x in self._tracks].index(id(track))
        return foo

    def auto_save(self):
        if self._auto_save:
            #print 'saving'
            self.save()
            self._is_modified = False

    def __len__(self):
        self.load()
        return len(self._tracks) if self._tracks is not None else 0

    def get_tracks(self):
        self.load()
        return [x for x in self._tracks]

    def _update_track_dict(self, element_idx, n):
        if element_idx not in self._track_indices:
            self._track_indices[element_idx] = 0
        self._track_indices[element_idx] += n
        if self._track_indices[element_idx] <= 0:
            del self._track_indices[element_idx]

    def append(self, element):
        self.load()
        elem = self._library[element]
        self._tracks.append(elem)
        self._is_modified = True
        self._update_track_dict(element, 1)
        self.auto_save()
        return elem

    def insert(self, element, index):
        self.load()
        #print element
        if index is None:
            return self.append(element)
        else:
            elem = self._library[element]
            self._tracks.insert(index, elem)
            self._is_modified = True
            self._update_track_dict(element, 1)
            self.auto_save()
            return elem

    def remove(self, element):
        #self.load()
        i = self.find(element)
        del self._tracks[i]
        #self._tracks.remove(element)
        self._is_modified = True
        self._update_track_dict(element.location, -1)
        self.auto_save()

    def remove_all(self, element, index):
        #self.load()
        self._tracks = []
        self._is_modified = True
        self._track_indices = {}
        self.auto_save()

    @property
    def length(self):
        total_length = 0
        for track in self._tracks:
            total_length += track.info.length
        return total_length

    @property
    def is_empty(self):
        self.load()
        return len(self._tracks) == 0

    @property
    def track_list(self):
        self.load()
        return [x for x in self._tracks]

    def load(self):
        pass

    def save(self):
        pass


class FilePlaylist(Playlist):
    def __init__(self, library, path, file_name, display_name = None, auto_save = False):
        super(FilePlaylist, self).__init__(library, display_name if display_name is not None else file_name, auto_save)
        self._path = path
        self._file_name = file_name
        #self._display_name = file_name if display_name is None else display_name

    def load(self):
        if self._tracks is None:
            path = os.path.join(self._path, self._file_name+'.m3u')
            self._tracks = []
            if os.path.exists(path):
                file_ = open(path, 'rU')
                for bar in file_.readlines():
                    try:
                        self.append(bar.strip('\n'))
                    except:
                        pass

    def save(self):
        if self._tracks is not None:
            path = os.path.join(self._path, self._file_name+'.m3u')
            file_ = open(path, 'w')
            for bar in self._tracks:
                file_.write(bar.location+"\n")
            file_.close()
        super(FilePlaylist, self).save()

class MainPlaylist(Playlist):
    def load(self):
        pass

    def save(self):
        pass

class TrackList(Playlist):
    def __init__(self, name, tracks):
        super(TrackList, self).__init__(None, name)
        self._tracks = tracks


class FilteredPlaylist(Playlist):
    def __init__(self, library, field = None, comparison = None, value = None):
        super(FilteredPlaylist, self).__init__(library, value)
        self._field = field
        self._comparison = comparison
        self._value = value


    def load(self):
        #print 'LOADING', self._value
        if self._tracks is None:
            self._tracks = []
            try:
                cmpr = getattr(self, "_"+self._comparison)
            except Exception, details:
                print details
                return None
            ret_val = []
            for t in self._library.iterate_tracks():
                try:
                    if cmpr(t):
                        #print 'TRUE'
                        self._tracks.append(t)
                except Exception, details:
                    print details
                    pass

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

    #def get_tracks(self):
    #    try:
    #        cmpr = getattr(self, "_"+self._comparison)
    #    except Exception, details:
    #        print details
    #        return []
    #    ret_val = []
    #    for t in self._library.values():
    #        try:
    #            if cmpr(t):
    #                ret_val.append(t)
    #        except Exception, details:
    #            print details
    #            pass
    #    return ret_val
