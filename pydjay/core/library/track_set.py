from playlist import FilePlaylist


class TrackSet(FilePlaylist):
    def __init__(self, library, path, name, *args, **kwargs):
        super(TrackSet, self).__init__(library, path, name, auto_save=True)
        self._queued_tracks_indices = set([])

    def add(self, location, index=None):
        self.load()
        self.append(location)

    def remove(self, location):
        self.load()
        track_list = self.track_list
        for t in track_list:
            if t.location == location:
                super(TrackSet, self).remove(t)
