import os
import time
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty
from kivy.logger import Logger
from kivy.event import EventDispatcher


class PlaybackManager(EventDispatcher):
    track = ObjectProperty(None)
    queue = ObjectProperty(None)
    session_manager = ObjectProperty(None)
    wait_time = NumericProperty(5)
    queue_length = NumericProperty(0)
    queue_end_time = NumericProperty(0)
    queue_is_playing = BooleanProperty(False)
    queue_stop_request = BooleanProperty(False)
    track_position = NumericProperty(0, allownone=True)
    track_duration = NumericProperty(None, allownone=True)
    track_length = NumericProperty(None, allownone=True)
    remaining_time = NumericProperty(None, allownone=True)

    def __init__(self, player, queue, session_manager, *args, **kw):
        super(PlaybackManager, self).__init__(*args, **kw)
        self.player = player
        self.queue = queue
        self.session_manager = session_manager
        self.player.bind(on_end_of_stream=self._on_eos,
                         track_length=self._forward_track_length,
                         track_duration=self._forward_track_duration,
                         track_position=self._forward_track_position,
                         remaining_time=self._forward_remaining_time)
        self.queue.bind(queue_length=self._update_queue_length)
        self.bind(wait_time=self._update_queue_length)

        self._update_queue_length()
        self.queue_is_playing = False
        self._current_time = None

        self.register_event_type('on_playback_started')
        self.register_event_type('on_end_of_stream')
        self.register_event_type('on_track_eject')
        self.register_event_type('on_queue_started')
        self.register_event_type('on_queue_stopped')

    def on_playback_started(self, *args):
        pass

    def on_queue_started(self, *args):
        pass

    def on_queue_stopped(self, *args):
        pass

    def on_end_of_stream(self, *args):
        pass

    def on_track_eject(self, *args):
        pass

    def _forward_track_position(self, *a):
        self.track_position = self.player.track_position

    def _forward_track_duration(self, *a):
        self.track_duration = self.player.track_duration

    def _forward_remaining_time(self, *a):
        self.remaining_time = self.player.remaining_time

    def _forward_track_length(self, *a):
        self.track_length = self.player.track_length

    def shutdown(self):
        pass

    def immediate_stop(self, queue_stop=False):
        Logger.info('MainPlayer: Stopping player')
        self.player.stop(flush=True)
        if self.track is not None:
            self.session_manager.add(self.track, True)
            if self._current_time is not None:
                self.track.metadata.add_play_time(self._current_time)
                self._current_time = None

        if queue_stop:
            self.queue_is_playing = False
            self.dispatch("on_track_eject")
            self.dispatch('on_queue_stopped')

    def play_next_track_in(self, time):
        Logger.info('MainPlayer: End of stream %s', self.track)
        self.immediate_stop()
        Clock.unschedule(self._load_next)
        Clock.schedule_once(self._load_next, time)

    def _on_eos(self, *args):
        if not self.queue_stop_request:
            if self.queue.is_empty:
                self.queue_is_playing = False
                self.dispatch('on_queue_stopped')
                self.immediate_stop()
            else:
                self.play_next_track_in(self.wait_time)
                self.dispatch("on_end_of_stream")
        else:
            self.queue_is_playing = False
            self.immediate_stop()
            self.dispatch('on_queue_stopped')

    def play_next_track(self, *args):
        self.play_next_track_in(0)

    def _load_next(self, *args):
        Logger.info('MainPlayer: Loading next track')
        if not self.queue.is_empty:
            if not self.queue_stop_request:
                track = self.queue.dequeue()
                self.track = track
                self.play()
            else:
                self.queue_is_playing = False
        else:
            self.queue_is_playing = False

    def _start_play(self):
        if self.queue is not None and not self.queue.is_empty:
            Clock.schedule_once(self._load_next, 0)
            self.dispatch('on_queue_started')

    def start_queue(self):
        if not self.queue_is_playing and not self.queue.is_empty:
            Logger.info('MainPlayer: Starting queue')
            self.queue_is_playing = True
            self.queue_stop_request = False
            self._start_play()

    def stop_queue(self):
        if not self.queue_stop_request:
            Logger.info('MainPlayer: Setting queue to stop after the current track')
            self.queue_stop_request = True

    def play(self):
        if self.track is not None:
            Logger.info('MainPlayer: Starting playback of %s', self.track)
            self._current_time = time.time()
            self.player.play(self.track.location, self.track.info.start_time,
                             self.track.info.end_time)
            self.dispatch('on_playback_started')

    def _update_queue_length(self, *a):
        l = self.queue.queue_length
        num = len(self.queue)
        if num > 0:
            self.queue_length = l + self.wait_time * (num - 1)

        current_time = time.time()
        r_t = self.remaining_time if self.remaining_time is not None else 0
        self.queue_end_time = current_time + (r_t + self.queue_length) / 1000000000
