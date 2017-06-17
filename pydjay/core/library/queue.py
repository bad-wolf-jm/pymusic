from playlist import FilePlaylist


class PlayQueue(FilePlaylist):
    def __init__(self, library, path, name, *args, **kwargs):
        super(PlayQueue, self).__init__(library, path, name, auto_save=True)
        self._queued_tracks_indices = set([])

    def dequeue(self, incomplete=None):
        t_track = self._tracks.pop(0)
        self.save()
        return t_track

    def add_track(self, track, index=None):
        self.insert(track.location, index)

    def remove_track(self, track):
        self.remove(track)

    def top(self):
        t_track = self._tracks[0]
        return t_track
