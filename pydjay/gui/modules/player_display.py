import os
#import re
#import mimetypes
#import threading
#import socket
#import functools
#import json
import time
#import cPickle as pickle
import array

#from functools import partial
#from threading import Thread
from os.path import getsize
from datetime import datetime

from kivy.clock import mainthread, Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
#from kivy.uix.bubble import Bubble
#from kivy.uix.popup import Popup
from kivy.uix.button import Button

from kivy.properties import ObjectProperty
from kivy.factory import Factory

#from pydjay.audio.wavegen import WaveformGenerator
#from pydjay.audio.gst import AudioDecoder
#from pydjay.audio.remote import SlavePlayer

from pydjay.library import save_to_current_session

from pydjay.uix import widgets, waveform_seekbar#screen, paged_grid, paged_display
#from pydjay.gui.turntable import turntable
#from main_queue import UploadTrack
from pydjay.gui.utils import seconds_to_human_readable
from pydjay.gui import volume_slider
from pydjay.utils.protocol import MAGIC
#from pydjay.uix import clickable_area
#from pydjay.uix import long_press_button
#from pydjay.uix.slider import XSlider
#from pydjay.gui.swipe_behaviour import SwipeBehavior
#from pydjay.gui.files_screen import file_browser, location_browser
#from mediacentre.skins.default.theme import get_path

from kivy.logger import Logger
import pydjay.bootstrap


kv_string = """
<MainPlayerDisplay>:
    seekbar:              seekbar
    #turntable:           turntable
    display_window:       display_window
    album_art:            album_art
    artist_label:         artist_label
    title_label:          title_label
    time_remaining_label: time_remaining
    player_stopped:       player_stopped.__self__
    main_player_volume:   main_player_volume
    #track_uploading:     track_uploading
    #start_queue_button:  start_queue_button
    #stopping_message:    stopping_message #queue_stop_options:  queue_stop_options
    orientation: 'horizontal'
    size_hint: 1, 1
    #swipe_to_play_next: swipe_to_play_next
    #transparent_overlay: transparent_overlay 
    skip_to_next_overlay: skip_to_next_overlay.__self__
    countdown: countdown.__self__
    #padding: [10,10,0,0]
    #spacing: 10
    size_hint: 1, 1


    BoxLayout:
        orientation: 'vertical'
        size_hint: None, 1
        width: 70
        padding: [10,10,10,10]
        spacing: 10

        VolumeSlider:
            id: main_player_volume
            size_hint: None, 1
            pos_hint: {'center_x': .5}
            width: 50
        Label:
            text: "Volume"
            font_size: 11
            text_size: self.size
            halign: 'center'
            valign: 'middle'
            size_hint: 1, None
            height: 11
    VDivider:
    StencilView:
        size_hint: 1,None
        height: 150
        RelativeLayout:
            size_hint: (None,None)
            size: self.parent.size
            pos: self.parent.pos
            id: display_window

            BoxLayout:
                orientation: 'vertical'
                BoxLayout:
                    orientation: 'horizontal'
                    size_hint: 1,1
                    Image:
                        id: album_art
                        size_hint: None, 1
                        width: self.height
                        source: 'atlas://pydjay/gui/images/resources/default_album_cover'
                        allow_stretch: True
                        keep_ratio: True
                    VDivider:
                    BoxLayout:
                        orientation: 'vertical'
                        size_hint: 1,1
                        BoxLayout:
                            orientation: 'vertical'
                            size_hint: 1,1 
                            padding: [10,7,5,7]
                            BoxLayout:
                                orientation: 'horizontal'
                                size_hint: 1,1
                                #height:35
                                spacing: 15
                                Label:
                                    size_hint: 1,1
                                    id: title_label
                                    font_size:'15sp'
                                    bold: True
                                    #color: 0,0,0,1
                                    text: '' 
                                    text_size: self.size
                                    halign: 'left'
                                    valign: 'middle'
                                    shorten: True
                                    ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}


                                Label:
                                    size_hint: None,1
                                    id: time_remaining
                                    font_size:'15sp'
                                    width: 50
                                    bold: True
                                    #color: 0.8,0.8,0.8,1
                                    text: ""
                                    text_size: self.size
                                    halign: 'left'
                                    valign:'middle'
                                    shorten: True
                                    ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}

                                    #size_hint: None, None
                                    #height:35
                            BoxLayout:
                                orientation: 'horizontal'
                                size_hint: 1,1
                                #height:35
                                spacing: 15
           
                                Label:
                                    size_hint: 1,1
                                    id:artist_label
                                    text: '' #asdfasdfasdf'#root.track.artist #"Artist"
                                    color: .6,.6,.6,1
                                    text_size: self.size
                                    halign: 'left'
                                    valign:'middle'
                                    font_size: 15
                                    #size_hint: 1, None
                                    #height:35

                                ImageButton:
                                    size_hint: None, None
                                    size: 25,25
                                    pos_hint: {'top': 1}
                                    #text: 'SL'
                                    image:'atlas://pydjay/gui/images/resources/add_to_shortlist'
                                    on_press: root.show_eject_panel()
                                    #    root.stop() 

                HDivider:
                WaveformSeekbar:
                    size_hint: 1, 1
                    id: seekbar

            #Carousel:
            #    size_hint: 1,1
            #    id: swipe_to_play_next
            #    direction: 'left'#
#
#                Widget:
#                    id: transparent_overlay
#                    size_hint: 1,1
            RelativeLayout:
                size_hint: 1,1
                id: skip_to_next_overlay
                canvas:
                    Color:
                        rgba: .3,0.3,0.3,.98
                    Rectangle:
                        size: self.size
                        pos: self.pos
                Button:
                    size_hint: None, None
                    size: 100,50
                    pos_hint:{'center_x':.25, 'center_y':.5}
                    text: "EJECT"
                    #disabled: not root.show_force_skip
                    on_press: root.immediate_stop()

                Button:
                    size_hint: None, None
                    size: 100,50
                    pos_hint:{'center_x':.75, 'center_y':.5}
                    text: "SKIP"
                    #disabled: not root.show_force_skip
                    on_press: root.play_next_track()
                Button:
                    size_hint: None, None
                    size: 75,25
                    pos_hint:{'right':1, 'y':0}
                    text: "Cancel"
                    #disabled: not root.show_force_skip
                    on_press: root.dismiss_eject_panel()

            RelativeLayout:
                size_hint: 1,1
                id: countdown
                disabled: False
                #opacity: 1 if root.show_force_skip else 0
                canvas:
                    Color:
                        rgba: 0,0,0,.8
                    Rectangle:
                        size: self.size
                        pos: 0,0 #self.pos

                BoxLayout:
                    orientation: 'vertical'
                    size_hint: .5, 1
                    pos_hint: {'center_x':.5, 'center_y':.5}
                    height: 50
                    spacing: 10
                    padding:[0,10,0,10]
                    Label:
                        size_hint: 1,1
                        height: 40
                        font_size: 20
                        markup: True
                        halign: 'center'
                        valign: 'top'
                        text_size: self.size
                        text: root.countdown_timeout 
                    Button:
                        id: start_queue_button
                        size_hint: None, None
                        size: 200,40
                        pos_hint:{'center_x':.5, 'center_y':.5}
                        text: "PLAY NOW"
                        #disabled: not root.show_force_skip
                        on_press: root.play_next_track()


            RelativeLayout:
                size_hint: 1,1
                id: player_stopped
                disabled: False
                #opacity: 1 if root.show_force_skip else 0
                canvas:
                    Color:
                        rgba: 0,0,0,.9
                    Rectangle:
                        size: self.size
                        pos: 0,0 #self.pos

                BoxLayout:
                    orientation: 'vertical'
                    size_hint: .5, 1
                    pos_hint: {'center_x':.5, 'center_y':.5}
                    height: 50
                    spacing: 10
                    padding:[0,10,0,10]
                    Label:
                        size_hint: 1,1
                        height: 40
                        font_size: 20
                        markup: True
                        halign: 'center'
                        valign: 'middle'
                        text_size: self.size
                        text: "No track currently playing" 

            #ColoredRectangle:
            #    id: track_uploading
            #    #size_hint: 1, 1
             #   rect_color: 0,0,0,.9

             #   BoxLayout:
             #       orientation: 'vertical'
             #       size_hint: 1,1
             #       padding: [30,0,30,10]
             #       Label:
             #           #id:artist_label
             #           bold: True
             #           text: "UPLOADING"
             #           color: (.6,.6,.6,1) #if not root.connected else (1,1,1,1)
             #           text_size: self.size
             #           halign: 'center'
             #           valign: 'middle'
             #           font_size: 20    #self.parent.height * 0.27
             #           size_hint: 1, 1
             #           shorten: True
             #           ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}

              #      Label:
              #          text: "%s - %s"%(root.track.track.metadata.title, root.track.track.metadata.artist) if root.track is not None else ""
              #          color: (.9,.9,.9,1) #if not root.connected else (1,1,1,1)
              #          text_size: self.size
              #          halign: 'center'
              #          valign: 'middle'
              #          font_size: 25        #self.parent.height * 0.27
              #          size_hint: 1, 1
              #          shorten: True
              #          ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}
              #          #height:40

              #      ProgressBar:
              #          size_hint: 1, 1
              #          min:0
              #          max:100
              #          #height: 30
              #          value: root.upload_progress * 100 #if root.track is not None else 0
"""


class MainPlayerDisplay(BoxLayout):
    seekbar           = ObjectProperty(None)
    turntable         = ObjectProperty(None)
    track             = ObjectProperty(None, allownone = True)
    title_label       = ObjectProperty(None)
    artist_label      = ObjectProperty(None)
    album_art         = ObjectProperty(None)
    queue             = ObjectProperty(None)
    deck              = ObjectProperty(None)
    stopping_message  = ObjectProperty(None)
    upload_progress      = NumericProperty(0)
    swipe_to_play_next   = ObjectProperty(None)
    transparent_overlay  = ObjectProperty(None) 
    skip_to_next_overlay = ObjectProperty(None) 
    display_window       = ObjectProperty(None) 
    countdown = ObjectProperty(None)
    countdown_timeout = StringProperty("")
    connected_icon   = StringProperty('atlas://pydjay/gui/images/resources/slave-disconnected')
    connected_host   = StringProperty("Not Connected")

    #show_force_skip  = BooleanProperty(False)
    
    uploading       = BooleanProperty(False)
    upload_progress = NumericProperty(0)
    upload_track    = ObjectProperty(None, allownone = True)

    
    def __init__(self, *args, **kw):
        super(MainPlayerDisplay, self).__init__(*args, **kw)
        self._track              = None
        self._waveform_generator = None
        self._wave_buffer        = []
        self._duration = None
        self._queue_playing = False
        self._stop_counter = None
        self._eject_panel = None
        self._current_session = set([])
        self._is_connected = False
        self.countdown_timeout = ""
        self._countdown_timeout = 0
        self.bind(queue = self._new_queue_set)
        self.bind(deck = self._new_deck_set)
        pydjay.bootstrap.volume_control.bind(main_player = self._update_volume)
        Clock.schedule_once(self._post_init, -1)

    def _post_init(self, *args):
        #self.countdown.pos = 0, -150
        self.display_window.remove_widget(self.skip_to_next_overlay)
        self.display_window.remove_widget(self.countdown)

        #self.track_uploading.pos = 0, -150
        self.player_stopped.pos = 0,0
        #self.swipe_to_play_next.disabled = True
        self.main_player_volume.bind(volume = self._set_volume)
        #self.bind(on_drag_start = self._start_show_eject,
        #          on_drag = self._drag_show_eject)
        #self.swipe_rect_width = 400
        #self.swipe_rect_width = 200
        #self.
        #self.track_uploading.disabled = True



    def show_eject_panel(self, *a):
        self.display_window.add_widget(self.skip_to_next_overlay)

        pass

    def dismiss_eject_panel(self, *a):
        self.display_window.remove_widget(self.skip_to_next_overlay)

        pass

    def _drag_show_eject(self, *a):
        print 'drag', a
        pass

    

        
    def _update_volume(self, *args):
        self.main_player_volume.volume = pydjay.bootstrap.volume_control.main_player

    def _set_volume(self, *args):
        pydjay.bootstrap.volume_control.main_player = self.main_player_volume.volume

    def _new_deck_set(self, *args):
        self.deck.bind(track               = self.set_track,
                       track_duration      = self._update,
                       track_position      = self._update,
                       on_end_of_stream    = self._on_eos)
        self.deck.bind(on_queue_started    = self.dismiss_stopped_state,
                       on_queue_stopped    = self.display_stopped_state,
                       #on_track_eject      = self.display_stopped_state,
                       on_playback_started = self._on_playback_started)

    def shutdown(self):
        try:
            self._player.shutdown()
        except:
            pass
        
        
    def _new_queue_set(self, *a):
        if self.queue is not None:
            Logger.info('MainPlayer: New queue has been set')

    def _on_playback_started(self, *a):
        self.dismiss_countdown()

    def immediate_stop(self):
        self.deck.immediate_stop(True, fade = False)
        self.display_window.remove_widget(self.skip_to_next_overlay)

    def _update_countdown(self, *a):
        self._countdown_timeout -= 1
        if self._countdown_timeout > 0:
            self.countdown_timeout = '[color=#aaaaaa]Next track will play in:\n[/color] [b]%s seconds[/b]'% self._countdown_timeout
        else:
            self.countdown_timeout = "[b]The next track should be playing now...[/b]"
            
        pass
        
    def display_countdown(self, timeout):
        self._countdown_timeout = timeout
        self.countdown_timeout = "[color=#aaaaaa]Next track will play in:\n[/color] [b]%s seconds[/b]"% self._countdown_timeout
        Clock.schedule_interval(self._update_countdown, 1)
        self.display_window.add_widget(self.countdown) #.pos = 0,0

    def dismiss_countdown(self, *args):
        Clock.unschedule(self._update_countdown)
        self.display_window.remove_widget(self.countdown)

    def display_stopped_state(self, timeout):
        self.display_window.add_widget(self.player_stopped)

    def dismiss_stopped_state(self, *args):
        self.display_window.remove_widget(self.player_stopped)
                
    def _on_eos(self, *args):
        Logger.info('MainPlayer: End of stream %s', self._track)
        self.display_countdown(self.queue.deck.wait_time)

    def play_next_track(self):
        Logger.info('MainPlayer: Skipping end of track <%s>', self._track)
        self._duration = None
        self.display_window.remove_widget(self.skip_to_next_overlay)
        self.deck.play_next_track()

    def set_track(self, i, track):
        self._set_track_metadata(None, track)
        self.finish_set_track()

    def _update_upload_progress(self, i, value):
        self.upload_progress = value
        
    def _set_track_metadata(self, i, track):
        Logger.info('MainPlayer: Setting track')
        self._track = track.track
        self.track = track
        if self._track is not None:
            self.artist_label.text = self._track.metadata.artist
            self.title_label.text = self._track.metadata.title
            self.finish_set_track()
            if self._track.metadata.album_cover is not None:
                self.album_art.source = self._track.metadata.album_cover['medium']
            else:
                self.album_art.source = 'atlas://pydjay/gui/images/resources/default_album_cover'

    def finish_set_track(self):
        Logger.info('MainPlayer: Setting track')
        if self._track is not None:
            if self._track.metadata.waveform is None:
                Logger.info('MainPlayer: No waveform found for [%s], generating a new one', self._track)
                self._generate_track_waveform()
            else:
                try:
                    Logger.info('MainPlayer: Setting the waveform to the track\'s waveform, track length: %s', self._track.info.length)
                    if self._track.info.length is not None:
                        self.seekbar.max_value      = self._track.info.stream_length   
                        self.seekbar.waveform.x_max = self._track.info.stream_length                        
                    try:
                        f = open(self._track.metadata.waveform, 'rb')
                        arr = array.array('f')
                        num_points = int(f.readline().split('\n')[0])
                        arr.fromfile(f, num_points)
                        ll = arr.tolist()
                        offset = 0
                        points = [ll[offset:offset+2] for offset in range(0, len(ll) - 1, 2)]
                        points = sorted(points, cmp = lambda x,y: cmp(x[0], y[0]))
                        self.seekbar.waveform.points =  points#self._track.metadata.waveform
                    except EOFError:
                        ll = arr.tolist()
                        offset = 0
                        points = [ll[offset:offset+2] for offset in range(0, len(ll) - 1, 2)]
                        points = sorted(points, cmp = lambda x,y: cmp(x[0], y[0]))
                        self.seekbar.waveform.points =  points#self._track.metadata.waveform                        
                    except Exception:
                         self.seekbar.waveform.points = []
                    finally:
                        try:
                            f.close()
                        except:
                            pass
                except Exception, details:
                    Logger.error('MainPlayer: Setting the waveform failed for [%s]... generating a new one, %s', self._track, details)
                    self._generate_track_waveform()

    def _update(self, *a):
        self._duration = self.queue.deck.track_duration
        if self._duration is not None:
            self.seekbar.max_value      = self.queue.deck.track_duration
            self.seekbar.waveform.x_max = self.queue.deck.track_duration
        else:
            self.seekbar.max_value = 1
        position = self.queue.deck.track_position or 0
        duration = self.queue.deck.track_duration

        if duration is None:
            self.time_remaining_label.text = ""
        else:
            position = min(position, duration)
            self.time_remaining_label.text = "-"+seconds_to_human_readable((duration - position) / 1000000000)
            self.seekbar.value = position



Builder.load_string(kv_string)
Factory.register('MainPlayerDisplay', MainPlayerDisplay)
