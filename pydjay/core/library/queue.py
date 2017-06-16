from playlist import FilePlaylist

class PlayQueue(FilePlaylist):
    def __init__(self, library, path, name, *args, **kwargs):
        super(PlayQueue, self).__init__(library, path, name, auto_save = True)
        self._queued_tracks_indices = set([])
        #self._track_list    = []

    #def contains(self, location):
    #    return location in self._queued_tracks_indices

    def dequeue(self, incomplete = None):
        t_track = self._tracks.pop(0)
        #self._queued_tracks_indices.discard(t_track.location)
        self.save()
        return t_track

    def add_track(self, track, index = None):
        self.insert(track.location, index)
        #if index is not None:
        #    self._track_list.insert(index, track)
        #else:
        #    self._track_list.append(track)
        #self._queued_tracks_indices.add(track.location)

    def remove_track(self, track):
        self.remove(track)
        #self._queued_tracks_indices.discard(track.location)
        #        self._track_list.remove(track)

    #def move_track(self, track, to_index):
    #    to_index = max(min(len(self), to_index), 0)
    #    print 'Moving', track.metadata.title, 'to index', to_index, 'from_index',
#
#        try:
#            item = self._tracks.index(track)
#        except:
#            item = None
#        print item
#        if item is not None:
#            item = self._tracks[item]
#            self.remove(item)
#            self.insert(item, to_index)
#
    def top(self):
        t_track = self._tracks[0]
        return t_track

#    @property
#    def is_empty(self):
#        return len(self._track_list) == 0

#    @property
#    def track_list(self):
#        self.load()
#        for t in self._tracks if self._tracks is not None else []:
#            print t.metadata.title
#        print
#        return [x for x in self._tracks]

    #def set_track_list(self, list):
    #    self._track_list = [x for x in list]
    #    self._queued_tracks = set([track.location for track in list])

    #@property
    #def _update_queue_length(self):
    #    total_length = 0
    #    for track in self._track_list:
    #        total_length += track.info.length
    #    return total_length

    #def __len__(self):
    #    return len(self._track_list)
