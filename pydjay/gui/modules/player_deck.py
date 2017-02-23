import os
#import re
#import mimetypes
#import threading
#import socket
#import functools
#import json
import time
#import cPickle as pickle
#import array

#from functools import partial
#from threading import Thread
#from os.path import getsize
#from datetime import datetime

from kivy.clock import mainthread, Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
#from kivy.uix.bubble import Bubble
from kivy.uix.popup import Popup
from kivy.uix.button import Button

from kivy.animation import Animation

from kivy.properties import ObjectProperty
from kivy.factory import Factory

#from pydjay.audio.wavegen import WaveformGenerator
#from pydjay.audio.gst import AudioDecoder
#from pydjay.audio.remote import SlavePlayer
#from pydjay.audio.audio_player import AudioPlayer

#from pydjay.audio.player.player_process import AudioPlayer



from pydjay.library import save_to_current_session

from pydjay.uix import waveform_seekbar#screen, paged_grid, paged_display
#from pydjay.gui.turntable import turntable
from pydjay.uix import widgets

#from track_upload import UploadTrack
#from sound_volumes import VolumeControls
from pydjay.gui.utils import seconds_to_human_readable
#from pydjay.utils.protocol import MAGIC
#from pydjay.uix import clickable_area
#from pydjay.uix import long_press_button
#from pydjay.uix.slider import XSlider

#from pydjay.gui.files_screen import file_browser, location_browser
#from mediacentre.skins.default.theme import get_path

from kivy.logger import Logger
import pydjay.bootstrap

kv_string = """
<MainPlayerDeck>:
    deck:                 deck
    wait_toggle: wait_toggle
    wait_time_input: wait_time
    start_queue_button:   start_queue_button
    stopping_message: stopping_message
    orientation: 'horizontal'
    size_hint: 1, 1
    RelativeLayout:
        id: deck
        size_hint: (1, 1)
        #width: self.height * 1.4


        ColoredRectangle:
            rect_color: .1,.1,.1,1

        VerticalBox:
            HorizontalBox:
                size_hint: 1,1
                padding: [5,10,5,3]
                Button:
                    id: start_queue_button
                    size_hint: None, 1
                    size: 100,40
                    pos_hint: {'center_y': .5}
                    text: ''
                    font_size: 20
                    on_press: root.start_queue() #_start_play()
                    pos: self.parent.width - 130, 10

                Label:
                    id: stopping_message
                    size_hint: None, None
                    pos_hint: {'center_y': .5}
                    halign: 'center'
                    valign: 'middle'
                    size: 125,75
                    text_size: self.size
                    text: ''
                    font_size: 15
                    pos: self.parent.width - 130, 65

                Widget:
                    size_hint: .5, None
            HorizontalBox:
                size_hint: 1, 0.8
                padding: [0,0,0,0]
                canvas.before:
                    Color:
                        rgba: .4,.4,.4,1
                    Rectangle:
                        pos:  self.pos
                        size: self.size
                CheckBox:
                    id: wait_toggle
                    size_hint: None, 1
                    width: self.height

                HorizontalBox:
                    size_hint: 1,1
                    disabled: not wait_toggle.active
                    padding: [0,0,0,0]
                    Label:
                        size_hint: None, 1
                        pos_hint: {'center_y': .5}
                        halign: 'center'
                        valign: 'middle'
                        size: 40,20
                        text_size: self.size
                        text: 'Wait'
                        font_size: 15
                        #pos: self.parent.width - 130, 65
                    BoxLayout:
                        orientation: 'horizontal'
                        size_hint: None, None
                        pos_hint: {'center_y': .5}
                        width: 30
                        height: 30
                        spacing: 0
                        canvas.before:
                            Color:
                                rgba: .3,.3,.3,1
                            Rectangle:
                                pos:  self.pos
                                size: self.size

                        TextInput:
                            id: wait_time
                            size_hint: 1,1
                            font_size: 15
                            pos_hint: {'center_y':.5}
                            multiline: False
                            halign: 'center'
                            valign: 'middle'
                            text_size: self.width, self.height
                            text: '5'
                            foreground_color: 1,1,1,.8
                            background_color: 0,0,0,0
                            on_text_validate: root.set_wait_time(*args)
                            on_focus: root.set_wait_time_by_focus(*args)
                    Label:
                        size_hint: 1, None
                        height: 20
                        pos_hint: {'center_y': .5}
                        halign: 'left'
                        valign: 'middle'
                        #size: 125,75
                        text_size: self.size
                        text: 'seconds between songs'
                        font_size: 15
                        pos: self.parent.width - 130, 65

"""

        

class MainPlayerDeck(BoxLayout):
    seekbar          = ObjectProperty(None)
    turntable        = ObjectProperty(None)
    current_session_list = ObjectProperty(None)
    track            = ObjectProperty(None, allownone = True)
    title_label      = ObjectProperty(None)
    artist_label     = ObjectProperty(None)
    queue            = ObjectProperty(None)
    stopping_message = ObjectProperty(None)
    wait_time        = NumericProperty(1)
    swipe_to_play_next   = ObjectProperty(None)
    transparent_overlay  = ObjectProperty(None) 
    skip_to_next_overlay = ObjectProperty(None) 
    countdown            = ObjectProperty(None)
    countdown_timeout    = StringProperty("")
    wait_time_input      = ObjectProperty(None)
    wait_toggle          = ObjectProperty(None)
    window               = ObjectProperty(None)
    connected_icon       = StringProperty('atlas://pydjay/gui/images/resources/slave-disconnected')
    connected_host       = StringProperty("Not Connected")

    track_position = NumericProperty(None, allownone = True)
    track_duration = NumericProperty(None, allownone = True)
    
    volume          = NumericProperty(0)
    uploading       = BooleanProperty(False)
    upload_progress = NumericProperty(0)
    upload_track    = ObjectProperty(None, allownone = True)

    
    def __init__(self, *args, **kw):
        super(MainPlayerDeck, self).__init__(*args, **kw)
        self._track              = None
        self._wave_buffer        = []
        #self._player             = None
        self._player             = pydjay.bootstrap.main_player #AudioPlayer("MainDeckPlayer", num_channels = 2)
        self._player.bind(on_end_of_stream = self._on_eos,
                          track_duration   = self._forward_track_duration,
                          track_position   = self._forward_track_position)
        self._duration = None
        self._queue_playing = False
        self._stop_counter = None
        self._current_session = set([])
        self._unavailable_tracks = set([])
        self._current_time = None
        self._is_connected = False
        self.countdown_timeout = ""
        self._countdown_timeout = 0
        self._volume_control = None

        self._volume_fader   = None
        self._volume_restore = None
        self.bind(volume = self._set_volume)
        
        self.register_event_type('on_playback_started')
        self.register_event_type('on_end_of_stream')
        self.register_event_type('on_track_eject')
        self.register_event_type('on_queue_started')
        self.register_event_type('on_queue_stopped')
        self.register_event_type('on_unavailable_added')
        self.bind(queue = self._new_queue_set)
        Clock.schedule_once(self._post_init, -1)


    def _post_init(self, *args):
        self.wait_time_input.text = "%s"%self.wait_time
        self.wait_time_input.bind(focus = self._toggle_keyboard_shortcuts)

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

    def on_unavailable_added(self, *args):
        pass

    def _toggle_keyboard_shortcuts(self, *a):
        if not self.wait_time_input.focus:
            self.window.restore_focus()
        else:
            self.window.suspend_focus()
    
    def _forward_track_position(self, *a):
        self.track_position = self._player.track_position

    def _forward_track_duration(self, *a):
        self.track_duration = self._player.track_duration

    def set_current_session(self, session):
        self._current_session = set([x.location for x in session])
        self.dispatch("on_unavailable_added")

    def has_played(self, location):
        if self.track is not None and (location == self._track.track.location):
            return True
        return (location in self._current_session) or (location in self._unavailable_tracks)

    def add_unavailable(self, location):
        self._unavailable_tracks.add(location)
        self.dispatch("on_unavailable_added")

    def remove_unavailable(self, location):
        try:
            self._unavailable_tracks.remove(location)
            self.dispatch("on_unavailable_added")
        except:
            pass
        
    #def _connect_remote(self):
    #    #if not self._is_connected:
    #    if self._volume_control is not None:
    #        popup = VolumeControls(self, self._volume_control)
    #        popup.open()

    def set_volume_control(self, volume_control):
        self._volume_control = volume_control

    def set_wait_time(self, *args):
        try:
            t = int(self.wait_time_input.text)
            self.wait_time = t
        except:
            self.wait_time_input.text = '2'
            self.wait_time = 2
        self.wait_toggle.active = False
            
    def set_wait_time_by_focus(self, i, value):
        if not value:
            self.set_wait_time()
            
    def shutdown(self):
        pass

    def connect_player(self, player):
        pass
        
    def _new_queue_set(self, *a):
        if self.queue is not None:
            self.queue.bind(adapter = self._new_queue_adapter_set)

    def _new_queue_adapter_set(self, *a):
        Logger.info('MainPlayer: New queue has been set')
        self.queue.adapter.bind(data = self._watch_queue_data)
        if not self.queue.is_empty:
            self.start_queue_button.text = "START"
            self.start_queue_button.disabled = False
        else:
            self.start_queue_button.text = "EMPTY"
            self.start_queue_button.disabled = True
                
    def _watch_queue_data(self, *q):
        if not self.queue.is_empty:
            if not self._queue_playing:
                self.start_queue_button.text = "START"
                self.stopping_message.text = "" 
                self.start_queue_button.disabled = False
        else:
            if not self._queue_playing:
                self.start_queue_button.text = "EMPTY"
                self.stopping_message.text = "" 
                self.start_queue_button.disabled = True

    def immediate_stop(self, queue_stop = False, fade = False, continuation = None):
        Logger.info('MainPlayer: Stopping player')
        def _stop_after_fade(*args):
            #self.turntable.stop()
            self._player.stop()
            if self._track is not None:
                save_to_current_session(self._track.track)
                self._current_session.add(self._track.track.location)
                self.current_session_list.add_track(self._track.track)
                self.dispatch("on_unavailable_added")
                if self._current_time is not None:
                    self._track.track.metadata.add_play_time(self._current_time)
                    self._current_time = None

            if self._volume_restore is not None:
                self._volume_control.set_volume('main_player', self._volume_restore)
                self._volume_restore = None
                self._volume_fader = None

            if queue_stop:
                self._queue_playing = False
                self.dispatch("on_track_eject")
                self.dispatch('on_queue_stopped')
            if continuation is not None:
                continuation()
            self._watch_queue_data()

        if fade:
            if self._volume_fader is not None:
                self._volume_fader.cancel()
            if self._volume_control is not None:
                if self._volume_restore is None:
                    self._volume_restore = self._volume_control.get_volume('main_player')
                self._volume_control.set_volume('main_player', self.volume)
                self._volume_fader = Animation(volume = 0,
                                               t = 'in_out_sine',
                                               duration = 1)
                self._volume_fader.bind(on_complete = _stop_after_fade)
                self._volume_fader.start(self)
        else:
            _stop_after_fade()

                
    def play_next_track_in(self, time, fade = False):
        def _do_play_next_track_in():
            self._duration = None
            Clock.unschedule(self._load_next)
            if self._volume_restore is not None:
                if self._volume_control is not None:
                    self._volume_control.set_volume('main_player', self._volume_restore)
            Clock.schedule_once(self._load_next, time)

        Logger.info('MainPlayer: End of stream %s', self._track)
        self.immediate_stop(fade = fade, continuation = _do_play_next_track_in)

    def _on_eos(self, *args):
        if self._volume_fader is not None:
            self._volume_fader.stop(self)
            self.volume_fader = None

        if not self._stop_counter:
            if self.queue is not None and self.queue.is_empty:
                self._queue_playing = False
                self.dispatch('on_queue_stopped')
                self.immediate_stop()
                self._watch_queue_data()
            else:
                if self.queue is not None and not self.queue.is_empty:
                    if not self._stop_counter:
                        self.play_next_track_in(self.wait_time)
                        self.dispatch("on_end_of_stream")
        else:
            self._queue_playing = False
            self.immediate_stop()
            self.dispatch('on_queue_stopped')
            self._watch_queue_data()


            

                            
    def play_next_track(self, *args):
        self.play_next_track_in(0, fade = True)
            
    def _load_next(self, *args):
        Logger.info('MainPlayer: Loading next track')
        if self.queue is not None and not self.queue.is_empty:
            if not self._stop_counter:
                track = self.queue.dequeue()
                self._track = track
                self.track = self._track
                self.finish_set_track(track.track)
                self.play()
                self._set_track_metadata(track.track)
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
                self.start_queue_button.text = 'STOP'
        else:
            if self._stop_counter:
                Logger.info('MainPlayer: Cancel stop')
                self._stop_counter = False
                self.start_queue_button.text = 'STOP'
                self.stopping_message.text = ""
            else:
                Logger.info('MainPlayer: Setting queue to stop after the current track')
                self._stop_counter = True
                self.start_queue_button.text = 'CANCEL'
                self.stopping_message.text = "Queue will stop after this song"


    def _set_volume(self, *a):
        if self._volume_control is not None:
            self._volume_control.set_volume('main_player', self.volume)

    
    def play(self):
        def _restore_volume(*args):
            self._volume_control.set_volume('main_player', self._volume_restore)
            self._volume_restore = None
            self._volume_fader = None

        def _progress(*args):
            print args
            
        if self._track is not None:
            Logger.info('MainPlayer: Starting playback of %s', self._track)
            self._current_time = time.time()
            print self._track.track.location
            self._player.play(self._track.track.location, self._track.track.info.start_time, self._track.track.info.end_time)
            if self._track.track.info.start_time is not None:
                if self._volume_control is not None:
                    self._volume_restore = self._volume_control.get_volume('main_player')
                    self._volume_control.set_volume('main_player', 0)
                    self._volume_fader = Animation(volume = self._volume_restore,
                                                   t = 'in_out_sine',
                                                   duration = 1)
                    self._volume_fader.bind(on_complete = _restore_volume)
                    self._volume_fader.start(self)
            self.dispatch('on_playback_started')

    def set_track(self, track):
        self._set_track_metadata(track)
        self.finish_set_track()
            
    def _set_track_metadata(self, track):
        Logger.info('MainPlayer: Setting track')

    def finish_set_track(self, track):
        Logger.info('MainPlayer: Setting track')

Builder.load_string(kv_string)
Factory.register('MainPlayerDeck', MainPlayerDeck)
