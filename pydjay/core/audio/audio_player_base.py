import os
import threading
from decoder import GstAudioFile
from output_jack import JackOutput
from pydjay.core.callback_dispatch import CallbackDispatcher

#from kivy.properties import StringProperty, NumericProperty, AliasProperty
#from kivy.event import EventDispatcher
#from kivy.clock import mainthread, Clock

class AudioPlayer(CallbackDispatcher):
    #state                = StringProperty(None, allownone = True)
    #track_duration       = NumericProperty(None, allownone = True)
    #track_position       = NumericProperty(None, allownone = True)
    #track_length         = NumericProperty(None, allownone = True)

    def __init__(self, player_name = None, num_channels = 2, **kw):
        super(AudioPlayer, self).__init__(**kw)
        self._current_time  = None
        self.player_name    = player_name
        self.num_channels   = num_channels
        self._is_playing    = False
        self._player_thread = None
        self._decoder       = None
        self._output        = JackOutput(self.player_name, self.num_channels)
        self.state          = None
        self.track_duration = None
        self.track_position = None
        self.register_callback("on_end_of_stream")
        self.register_callback("playback_state")
        self.register_callback("track_duration")
        self.register_callback("track_length")
        self.register_callback("track_position")

    def connect_outputs(self, **kwargs):
        self._output.connect_outputs(**kwargs)

    def disconnect_outputs(self, **kwargs):
        self._output.disconnect_outputs(**kwargs)

    def on_track_length(self, length):
        pass

    def on_track_duration(self, duration):
        pass

    def on_track_position(self, position):
        pass

    def on_track_remaining_time(self, position):
        pass

    def _player_loop(self):
        eos = False
        has_duration = False
        iteration = 0
        while self._is_playing:
            try:
                timestamp, samples = self._decoder.next()
                if self._decoder.duration is not None and not has_duration:
                    has_duration = True
                    self.on_track_duration(self._decoder.duration)
                    self.on_track_length(self._decoder.track_length)
                    #self.dispatch('track_duration', self._decoder.duration)
                    #self.dispatch('track_length', self._decoder.track_length)
                    #self.dispatch('remaining_time', self._decoder.track_length)
                #if iteration == 5:
                self.on_track_position(self._output.stream_time)
                #if self.track_duration is not None and self.track_position is not None:
                #    self.on_track_remaining_time(self.track_duration - self.track_position)
#                    iteration = 0
#                else:
#                    iteration += 1
                self._output.send(samples)
            except StopIteration:
                eos = True
                break
        self._decoder.close()
        self._is_playing = False
        self._player_thread = None
        if eos:
            self.on_end_of_stream()

    def play(self, filename, start_time = None, end_time = None):
        self.stop(flush = True)
        self._file  = filename
        try:
            self._decoder  = GstAudioFile(self._file, self._output.num_channels, self._output.samplerate, 'F32LE', None, start_time, end_time)
            if start_time is not None:
                self._decoder.set_start_time(start_time)
                self._output.reset_timer(start_time)
            else:
                self._output.reset_timer(0)
            self._player_thread = threading.Thread(target = self._player_loop)
            self._is_playing    = True
            self._player_thread.start()
            self.state = "playing"
        except IOError:
            self.state = 'stopped'
        except Exception, details:
            print details
            self.state = 'stopped'
        #    raise

    def stop(self, flush = False):
        self._is_playing = False
        if flush:
            self._output.flush_buffer()
        self._output.reset_timer()
        if self._player_thread is not None:
            self._player_thread.join()
        self._player_thread = None
        self._decoder       = None
        self.track_duration = None
        self.track_length   = None
        self.track_position = None
        self.state          = "stopped"

    def pause(self):
        self.state = "paused"

    def seek(self, timestamp):
        if self._decoder is not None:
            self._decoder.seek(timestamp)
            self._output.reset_timer(timestamp)
            self._output.flush_buffer()

    def seek_relative(self, time):
        if self._is_playing:
            p = self.track_position
            if p is not None:
                d = self.track_duration
                if d is not None:
                    p += time
                    p = max(min(p, d), 0)
                    self.seek(p)

    @property
    def is_playing(self):
        return self.state == 'playing'

    def shutdown(self):
        self.stop()
        self._output.close()
