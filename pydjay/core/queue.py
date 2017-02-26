from kivy.clock import mainthread, Clock
from kivy.logger import Logger
from kivy.event import EventDispatcher
from kivy.properties import NumericProperty

        
class PlayQueue(EventDispatcher):
    queue_length = NumericProperty(0)
    
    def __init__(self, *args, **kwargs):
        super(PlayQueue, self).__init__(*args, **kwargs)
        self._queued_tracks = set([])
        self._track_list    = []
        self.register_event_type("on_queue_content_change")

    def on_queue_content_change(self, *args):
        pass
        
    def contains(self, location):
        return location in self._queued_tracks
        
    def dequeue(self, incomplete = None):
        t_track = self._track_list.pop(0)
        self._queued_tracks.discard(t_track.location)
        self._update_queue_length()
        self.dispatch("on_queue_content_change", self.track_list)
        return t_track

    def add_track(self, track, index = None):
        if index is not None:
            self._track_list.insert(index, track)
        else:
            self._track_list.append(track)
        self._queued_tracks.add(track.location)
        self._update_queue_length()
        self.dispatch("on_queue_content_change", self.track_list)
    
    def remove_track(self, track):
        self._queued_tracks.discard(track.location)
        self._track_list.remove(track)
        self._update_queue_length()
        self.dispatch("on_queue_content_change", self.track_list)

    def move_track(self, track, to_index):
        try:
            item = self._track_list.index(track)
        except:
            item = None

        if item is not None:
            item = self._track_list[item]
            self._track_list.remove(item)
            self.add_track(item, to_index)
            #self.select(self._current_selection - 1)
    
    def top(self):
        t_track = self._track_list[0]
        return t_track

    @property
    def is_empty(self):
        return len(self._track_list) == 0

    @property
    def track_list(self):
        return [x for x in self._track_list]
    
    def set_track_list(self, list):
        self._track_list = [x for x in list]
        self._queued_tracks = set([track.location for track in list])
        self._update_queue_length()
        self.dispatch("on_queue_content_change", self.track_list)


    def _update_queue_length(self):
        total_length = 0
        for track in self._track_list:
            total_length += track.info.length
        self.queue_length = total_length

    def __len__(self):
        return len(self._track_list)
