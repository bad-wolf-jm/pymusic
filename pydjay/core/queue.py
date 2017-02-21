import os
import time

from kivy.clock import mainthread, Clock
from kivy.properties import ObjectProperty, StringProperty, ListProperty, BooleanProperty, NumericProperty
from kivy.logger import Logger
from pydjay.gui.track_data import TrackData

        
class MasterQueue(EventDispatcher):
    track_list        = ListProperty()
    queue_time        = StringProperty()
    play_time         = StringProperty()
    queue_end_time    = StringProperty()
    queue_changed     = BooleanProperty(False)
    preview_player    = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        super(MasterQueue, self).__init__(*args, **kwargs)
        self._queued_tracks = set([])

    def contains(self, location):
        return location in self._queued_tracks
        

    def dequeue(self, incomplete = None):
        self._queued_tracks.discard(self.adapter.data[0]['item'].track.location)
        t_track = self.adapter.data.pop(0)
        return t_track['item']

    def remove_track(self, track):
        self._queued_tracks.discard(track.track.location)
        self.queue_view.remove_track(track)
    
    def top(self):
        t_track = self.adapter.data[0]
        return t_track

    @property
    def is_empty(self):
        return len(self.adapter.data) == 0

    
    def add_track(self, track, index = None):
        self.queue_view.add_track(track, index)
    enqueue = add_track

    def set_track_list(self, list):
        self.queue_view.set_track_list(list, False)
        self._queued_tracks = set([track.location for track in list])


    def _update_queue_times(self, *a):
        pl_remaining_time = self.deck._player.remaining_time if self.deck._player is not None else 0
        total_length = 0
        for track in self.queue_view.adapter.data:#track_list:
            total_length += track['item'].track.info.length + 5000000000
        total_length = max(total_length - 5000000000, 0)
        total_length += (pl_remaining_time)
        self.queue_time = "[color=#bbbbbb]Total time:[/color] " + \
                          "[color=#ffffff]" + \
                          seconds_to_human_readable(total_length / 1000000000) + \
                          "[/color]"
        current_time = time.time()
        current_time += total_length / 1000000000
        self.queue_end_time = "[color=#bbbbbb]Queue ends at:[/color] " + \
                              "[color=#ffffff]" + \
                              time.strftime("%H:%M", time.localtime(current_time)) + \
                              "[/color]"  #time.ctime(current_time)
        #self._play_time += 1
        self.play_time = "[color=#bbbbbb]Play time:[/color] " + \
                         "[color=#ffffff]" + \
                         seconds_to_human_readable(self._play_time) + \
                         "[/color]"

    def update_labels(self):
        total_length = 0
        for track in self.queue_view.adapter.data:#track_list:
            total_length += track['item'].track.info.length + 5000000000
        total_length = max(total_length - 5000000000, 0)
        self._total_queue_time = total_length
        self._update_queue_times()
        current_time = time.time()
        for card in self.queue_view.adapter.data:
            play_time = time.strftime("%H:%M", time.localtime(current_time))
            card['item'].play_time = play_time
            current_time += card['item'].track.info.length / 1000000000 + 5


