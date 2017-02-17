import os
import threading
import time
import sys
from os.path import getsize
from datetime import datetime
from decoder import GstAudioFile
from output_jack import JackOutput

from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty, AliasProperty
from kivy.event import EventDispatcher
from kivy.clock import mainthread, Clock

class AudioPlayer(EventDispatcher):
    state                = StringProperty(None, allownone = True)
    track_duration       = NumericProperty(None, allownone = True)
    track_position       = NumericProperty(None, allownone = True)

    def __init__(self, player_name, num_channels = 2, *args, **kw):
        super(AudioPlayer, self).__init__(*args, **kw)
        self.register_event_type("on_end_of_stream")

        self._track_promise = None
        self._current_time  = None
        self.player_name = player_name
        self._output        = JackOutput(player_name, num_channels)
        self._is_playing    = False
        self._player_thread = None
        self._decoder       = None
        self._tr_time = None
        self._tr_dur  = None
        self._state   = 'stopped'
        self._eos_callbacks = []
        
    def on_end_of_stream(self, *args):
       pass

    def connect_outputs(self, **kwargs):
        self._output.connect_outputs(**kwargs)

    def disconnect_outputs(self, **kwargs):
        self._output.disconnect_outputs(**kwargs)



    def _get_remaining_time(self, *a):
        if self.track_duration is not None and self.track_position is not None:
            return self.track_duration - self.track_position
        return 0

    remaining_time  = AliasProperty(_get_remaining_time, bind = ['track_duration', 'track_position'])


        
    @mainthread
    def _signal_stream_time(self, timestamp):
        self.track_position = timestamp

    @mainthread
    def _signal_stream_duration(self, time):
        self.track_duration = time

    @mainthread
    def _signal_end_of_stream(self):
        self.stop()
        self.dispatch('on_end_of_stream')
        #self.on_end_of_stream()

    def _player_loop(self):
        eos = False
        if self._decoder is not None:
            while self._is_playing:
                try:
                    timestamp, samples = self._decoder.next()
                    if self._decoder.duration is not None:
                        self._signal_stream_duration(self._decoder.duration)
                    self._signal_stream_time(self._output.stream_time)
                    self._output.send(samples)
                except StopIteration:
                    eos = True
                    break
            self._decoder.close()
            self._is_playing = False
            self._player_thread = None
            if eos:
                self._signal_end_of_stream()
            

    def play(self, filename, start_time = None, end_time = None):
        self.stop()
        self._file          = filename
        #print start_time, end_time
        self._decoder       = GstAudioFile(self._file, self._output.num_channels, self._output.samplerate, 'F32LE', None, start_time, end_time)
        if start_time is not None:
            self._decoder.seek(start_time)
            self._output.reset_timer(start_time)
        else:
            self._output.reset_timer()
        self._player_thread = threading.Thread(target = self._player_loop)
        self._is_playing    = True
        self._player_thread.start()
        self.state = "playing"

    def stop(self):
        self._is_playing = False
        self._output.flush_buffer()
        self._output.reset_timer()
        if self._player_thread is not None:
            self._player_thread.join()
        self._player_thread = None
        self._decoder       = None
        self.track_duration = None
        self.track_position = None
        self.state          = "stopped"
        
    def pause(self):
        self.state = "paused"

    def seek(self, timestamp):
        if self._decoder is not None:
            self._decoder.seek(timestamp)
            self._output.reset_timer(timestamp)

    @property
    def is_playing(self):
        return self.state == 'playing'

    def shutdown(self):
        self.stop()
        self._output.close()
        print "shutting down", self.player_name




    
buffer = []
if __name__ == '__main__':

    path = os.path.abspath(os.path.expanduser(sys.argv[1]))
    player = AudioPlayer("TestPlayer", 2)
    player.connect_outputs(output_1 = "system:playback_1",
                           output_2 = "system:playback_2")
    player.play(path)
    #time.sleep(45)
    #player.stop()
