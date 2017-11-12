from playlist import FilePlaylist


class ShortList(FilePlaylist):
    def __init__(self, library, path, name, display_name, *args, **kwargs):
        super(ShortList, self).__init__(library, path, name, display_name, True)
        self._queued_tracks_indices = set([])

    def contains(self, location):
        return location in self._queued_tracks_indices

    def add_track(self, track, index=None):
        if not self.contains(track.location):
            self.insert(track.location, index)
            self._queued_tracks_indices.add(track.location)

    def remove_track(self, track):
        self.remove(track)
        self._queued_tracks_indices.discard(track.location)
