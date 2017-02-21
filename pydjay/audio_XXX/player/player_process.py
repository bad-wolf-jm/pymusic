import os
#import re
#import mimetypes
import threading
#import socket
#import functools
#import json
import time
#import cPickle as pickle
#import array
import sys

#from functools import partial
#from threading import Thread
from os.path import getsize
from datetime import datetime

from kivy.clock import mainthread, Clock
#from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty, AliasProperty
#from kivy.uix.boxlayout import BoxLayout
#from kivy.uix.bubble import Bubble
#from kivy.uix.popup import Popup
#from kivy.uix.button import Button

from kivy.properties import ObjectProperty
#from kivy.factory import Factory
from kivy.event import EventDispatcher
#from pydjay.audio.wavegen import WaveformGenerator
#from pydjay.audio.gst import AudioDecoder
#from pydjay.audio.remote import SlavePlayer

#from pydjay.library import save_to_current_session

#from pydjay.uix import waveform_seekbar#screen, paged_grid, paged_display
#from pydjay.gui.turntable import turntable
#from track_upload import UploadTrack
#from pydjay.gui.utils import seconds_to_human_readable
#from pydjay.utils.protocol import MAGIC
#from pydjay.uix import clickable_area
#from pydjay.uix import long_press_button
#from pydjay.uix.slider import XSlider

#from pydjay.gui.files_screen import file_browser, location_browser
#from mediacentre.skins.default.theme import get_path

from player import AudioPlayer as AP
#from kivy.logger import Logger
#from decoder import GstAudioFile
#from output_jack import JackOutput
from multiprocessing import Process, Queue, Value
from Queue import Empty, Full


class AudioPlayerProcess(Process):
    def __init__(self, name = "", num_channels = 2, in_queue = None, out_queue = None, position = None, duration = None, state = None, eos = None):
        super(AudioPlayerProcess, self).__init__()
        self.in_queue  = in_queue
        self.out_queue = out_queue
        self.position = position
        self.duration = duration
        self.state    = state
        self.eos      = eos
        self.player_name = name
        self.num_channels = num_channels
        self.player    = None #AP(name, num_channels)

    def run(self):
        def _end_of_stream():
            self.eos.value = 1
        self.player    = AP(self.player_name, self.num_channels)
        self.player.add_eos_callback(_end_of_stream)
        while True:
            try:
                command, args, kwargs = self.in_queue.get_nowait()
                if command == 'QUIT':
                    break
                try:
                    getattr(self.player, command)(*args, **kwargs)
                    time.sleep(.1)
                except AttributeError, details:
                    pass 
                except Exception, details:
                    print 'y', details
            except Empty, details:
                if self.player._tr_time is not None:
                    self.position.value = self.player._tr_time 
                else:
                    self.position.value = 0
                if self.player._tr_dur is not None:
                    self.duration.value = self.player._tr_dur 
                else:
                    self.duration.value = 0

                st = {"stopped": 0, "paused":1, "playing":2}
                self.state.value = st[self.player._state]
                time.sleep(.05)
            


        
class AudioPlayer(EventDispatcher):
    state                = StringProperty(None, allownone = True)
    track_duration       = NumericProperty(None, allownone = True)
    track_position       = NumericProperty(None, allownone = True)

    def __init__(self, player_name, num_channels = 2, *args, **kw):
        super(AudioPlayer, self).__init__(*args, **kw)
        self.register_event_type("on_end_of_stream")
        self.out_queue  = Queue()
        self.in_queue   = Queue()
        self._position  = Value('L',0)
        self._duration  = Value('L',0)
        self._state     = Value('i',0)
        self._eos       = Value('i',0)
        self._running   = True
        self._audio_process = AudioPlayerProcess(player_name, num_channels,
                                                 self.out_queue, self.in_queue,
                                                 self._position, self._duration,
                                                 self._state, self._eos)
        self._audio_process.start()

        self._foo = threading.Thread(target = self._print_info)
        self._foo.start()


    def _print_info(self):
        while self._running:
            #print "INFO:: ", self._position.value, self._duration.value
            self._signal_stream_time(self._position.value)
            self._signal_stream_duration(self._duration.value)
            self._signal_state(self._state.value)
            self._signal_eos(self._eos.value)
            time.sleep(.1)
            
    def on_end_of_stream(self, *args):
        pass

    def connect_outputs(self, **kwargs):
        self.out_queue.put(('connect_outputs', (), kwargs))

    def disconnect_outputs(self, **kwargs):
        self.out_queue.put(('disconnect_outputs', (), kwargs))

    @mainthread
    def _signal_eos(self, timestamp):
        if timestamp:
            self._eos.value = 0
            self.dispatch('on_end_of_stream')

    @mainthread
    def _signal_stream_time(self, timestamp):
        #print self.track_position, self.track_duration
        self.track_position = timestamp if timestamp > 0 else None

    @mainthread
    def _signal_state(self, timestamp):
        states = {0:'stopped', 1:'paused', 2:'playing'}
        self.state = states[timestamp]
        
    @mainthread
    def _signal_stream_duration(self, time):
        self.track_duration = time  if time > 0 else None

    @mainthread
    def _signal_end_of_stream(self):
        self.dispatch('on_end_of_stream')

    def play(self, filename):
        self._eos.value = 0
        self.out_queue.put(('play', (filename,), {}))

    def stop(self):
        self._eos.value = 0
        self.out_queue.put(('stop', (), {}))
        
    def pause(self):
        self._eos.value = 0
        self.out_queue.put(('pause', (), {}))

    @property
    def is_playing(self):
        return self.state == 'playing'

#buffer = []
if __name__ == '__main__':

    path = os.path.abspath(os.path.expanduser(sys.argv[1]))
    player = AudioPlayer("TestPlayer", 2)
    player.connect_outputs(output_1 = "system:playback_1",
                           output_2 = "system:playback_2")
    player.play(path)
    player._audio_process.join()
    #time.sleep(45)
    #player.stop()
