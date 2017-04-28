import os
import re
import mimetypes
import array
from kivy.clock import mainthread, Clock
from kivy.event import EventDispatcher

from kivy.properties import ObjectProperty, NumericProperty
from kivy.animation import Animation

class PreviewPlayer(EventDispatcher):
    volume           = NumericProperty(1.0)
    track_duration   = NumericProperty(None, allownone = True)
    track_position   = NumericProperty(None, allownone = True)
    track_length   = NumericProperty(None, allownone = True)

    def __init__(self, player, volume, *args, **kwargs):
        super(PreviewPlayer, self).__init__(*args, **kwargs)
        self._track  = None
        self.player  = player
        self.player.bind(on_end_of_stream = self._on_eos,
                         track_duration   = self._forward_track_duration,
                         track_length     = self._forward_track_length,
                         track_position   = self._forward_track_position)
        self.volume_controls      = volume
        self._save_monitor_volume = 1.0
        self._is_playing          = False

        self._pause_track_timestamp = None
        self._pause_track = None
        self.bind(volume = self._set_volume)

    def _forward_track_duration(self, *a):
        self.track_duration = self.player.track_duration

    def _forward_track_position(self, *a):
        self.track_position = self.player.track_position


    def _forward_track_length(self, *a):
        self.track_length = self.player.track_length
        
    def _on_eos(self, *a):
        self._duck_main_player = Animation(volume = self._save_monitor_volume,
                                           t = 'in_out_sine', duration = 0.5)
        self._duck_main_player.start(self)


    def _set_volume(self, i, value):
        self.volume_controls.main_player_monitor = self.volume

    def play(self, track, start_time = None, end_time = None):
        if self._is_playing:
            self._track = track
            self._start_time = start_time if start_time is not None else self._track.info.start_time
            self._end_time   = end_time if end_time is not None else self._track.info.end_time
            self._do_play(self._start_time, self._end_time)
        else:
            if self._fade_state == 'fading_out':
                self._track = track
                self._start_time = start_time if start_time is not None else self._track.info.start_time
                self._end_time   = end_time if end_time is not None else self._track.info.end_time
            elif self._fade_state == 'fading_in':
                self._track = track
                self._start_time = start_time if start_time is not None else self._track.info.start_time
                self._end_time   = end_time if end_time is not None else self._track.info.end_time
                self._duck_main_player.cancel(self)
            self._duck_main_player = Animation(volume = self.volume_controls.get_volume('main_player_monitor_mute'),
                                               t = 'in_out_sine', duration = 0.5)
            self._duck_main_player.start(self)
            self._duck_main_player.bind(on_complete = self._do_play)
            self._fade_state = 'fading_out'

    def pause(self):
        if self._is_playing:
            if self._track is not None:
                self._pause_track_timestamp = self.player.track_position
                self._pause_track = self._track
                self.player.stop(flush = True)
            self._is_playing = False
        else:
            if self._pause_track is not None:
                if self._pause_track == self._track:
                    s_t = self._pause_track_timestamp if self._pause_track_timestamp is not None else 0
                    self.player.play(self._track.location, s_t, self._track.info.end_time)
                    self._is_playing = True
                    return
            if self._track is not None:
                self.play(self._track, self._start_time, self._end_time)

    def _do_play(self, *a):
        self.player.play(self._track.location, self._start_time, self._end_time)
        self._is_playing = True
        self._duck_main_player = None
        self._fade_state = 'idle'

    def __stopped(self, *a):
        self._fade_state = 'idle'

    def stop(self):
        self.player.stop(flush = True)
        self._fade_state = 'fading_in'
        self._duck_main_player = Animation(volume = self._save_monitor_volume,
                                           t = 'in_out_sine', duration = 0.5)
        self._duck_main_player.bind(on_complete = self.__stopped)
        self._duck_main_player.start(self)
        self._is_playing = False

    def seek(self, timestamp):
        self.player.seek(timestamp)

    def shutdown(self):
        self.player.shutdown()
