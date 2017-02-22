import os
import time

from kivy.clock import mainthread, Clock
from kivy.properties import ObjectProperty, StringProperty, ListProperty, BooleanProperty, NumericProperty
from kivy.logger import Logger
from pydjay.gui.track_data import TrackData

        
class PlayQueue(EventDispatcher):
    queue_time        = StringProperty()
    play_time         = StringProperty()
    queue_end_time    = StringProperty()
    queue_changed     = BooleanProperty(False)
    preview_player    = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        super(PlayQueue, self).__init__(*args, **kwargs)
        self._queued_tracks      = set([])
        self._track_list = []
        self.register_event_type("on_queue_content_change")


    def on_queue_content_change(self, *args):
        pass
        
    def contains(self, location):
        return location in self._queued_tracks
        
    def dequeue(self, incomplete = None):
        t_track = self._track_list.pop(0)
        self._queued_tracks.discard(t_track.location)
        self.dispatch("on_queue_content_change", self.track_list)
        return t_track

    def remove_track(self, track):
        self._queued_tracks.discard(track.location)
        self._track_list.remove(track)
        self.dispatch("on_queue_content_change", self.track_list)
        #self.queue_view.remove_track(track)
    
    def top(self):
        t_track = self._track_list[0]
        return t_track

    @property
    def is_empty(self):
        return len(self._track_list) == 0

    @property
    def track_list(self):
        return [x for x in self._track_list]
    
    def add_track(self, track, index = None):
        self._track_list.insert(track, index)
        self.dispatch("on_queue_content_change", self.track_list)
    enqueue = add_track

    def set_track_list(self, list):
        self.queue_view.set_track_list(list, False)
        self._queued_tracks = set([track.location for track in list])
        self.dispatch("on_queue_content_change", self.track_list)


