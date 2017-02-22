import os
import time
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty
from kivy.logger import Logger
        

class PlaybackManager(EventDispatcher):
    track            = ObjectProperty(None)
    queue            = ObjectProperty(None)
    session_manager  = ObjectProperty(None)
    wait_time        = NumericProperty(1)
    queue_length     = NumericProperty(1)
    queue_end_time   = NumericProperty(1)
    track_position   = NumericProperty(None, allownone = True)
    track_duration   = NumericProperty(None, allownone = True)
    
    
    def __init__(self, player, queue, session_manager, *args, **kw):
        super(MainPlayerDeck, self).__init__(*args, **kw)
        #self._track           = None
        self.player          = player 
        self.queue           = queue
        self.session_manager = session_manager
        self.player.bind(on_end_of_stream = self._on_eos,
                          track_duration   = self._forward_track_duration,
                          track_position   = self._forward_track_position)

        self._duration      = None
        self._queue_playing = False
        self._stop_counter  = None
        self._current_time  = None
        self._countdown_timeout = 0

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
        self.track_position = self._player.track_position

    def _forward_track_duration(self, *a):
        self.track_duration = self._player.track_duration

    def shutdown(self):
        pass

    def immediate_stop(self, queue_stop = False): #, fade = False, continuation = None):
        Logger.info('MainPlayer: Stopping player')
        self._player.stop()
        if self._track is not None:
            save_to_current_session(self._track.track)
            self._current_session.add(self._track.track.location)
            self.current_session_list.add_track(self._track.track)
            if self._current_time is not None:
                self._track.track.metadata.add_play_time(self._current_time)
                self._current_time = None

        if queue_stop:
            self._queue_playing = False
            self.dispatch("on_track_eject")
            self.dispatch('on_queue_stopped')
                
    def play_next_track_in(self, time):
        Logger.info('MainPlayer: End of stream %s', self._track)
        self.immediate_stop()
        self._duration = None
        Clock.unschedule(self._load_next)
        Clock.schedule_once(self._load_next, time)

    def _on_eos(self, *args):
        if not self._stop_counter:
            if self.queue is not None and self.queue.is_empty:
                self._queue_playing = False
                self.dispatch('on_queue_stopped')
                self.immediate_stop()
            else:
                if self.queue is not None and not self.queue.is_empty:
                    if not self._stop_counter:
                        self.play_next_track_in(self.wait_time)
                        self.dispatch("on_end_of_stream")
        else:
            self._queue_playing = False
            self.immediate_stop()
            self.dispatch('on_queue_stopped')
                            
    def play_next_track(self, *args):
        self.play_next_track_in(0)
            
    def _load_next(self, *args):
        Logger.info('MainPlayer: Loading next track')
        if self.queue is not None and not self.queue.is_empty:
            if not self._stop_counter:
                track = self.queue.dequeue()
                self._track = track
                self.track = self._track
                self.play()
        elif self.queue.is_empty:
            self._queue_playing = False
        
    def _start_play(self):
        if self.queue is not None and not self.queue.is_empty:
            Clock.schedule_once(self._load_next, 0)
            self.dispatch('on_queue_started')
            
    def start_queue(self):
        if not self._queue_playing:
            if self.queue is not None and not self.queue.is_empty:
                Logger.info('MainPlayer: Starting queue')
                self._queue_playing = True
                self._stop_counter = False
                self._start_play()
        else:
            if self._stop_counter:
                Logger.info('MainPlayer: Cancel stop')
                self._stop_counter = False
            else:
                Logger.info('MainPlayer: Setting queue to stop after the current track')
                self._stop_counter = True
    
    def play(self):
        if self._track is not None:
            Logger.info('MainPlayer: Starting playback of %s', self._track)
            self._current_time = time.time()
            print self._track.track.location
            self._player.play(self._track.track.location, self._track.track.info.start_time, self._track.track.info.end_time)
            self.dispatch('on_playback_started')

