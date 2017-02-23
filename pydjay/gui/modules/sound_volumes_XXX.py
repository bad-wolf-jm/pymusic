import os
import re
import mimetypes
import threading
import socket
import functools
import json
import time
import cPickle as pickle
import array

from functools import partial
from threading import Thread
from os.path import getsize
from datetime import datetime

from kivy.clock import mainthread, Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.bubble import Bubble
from kivy.uix.popup import Popup
from kivy.uix.button import Button

from kivy.properties import ObjectProperty
from kivy.factory import Factory

#from pydjay.audio.wavegen import WaveformGenerator
#from pydjay.audio.gst import AudioDecoder
#from pydjay.audio.remote import SlavePlayer
#from pydjay.audio.audio_player import AudioPlayer

#from pydjay.library import save_to_current_session

from pydjay.uix import waveform_seekbar#screen, paged_grid, paged_display
#from pydjay.gui.turntable import turntable
#from track_upload import UploadTrack
from pydjay.gui.utils import seconds_to_human_readable
from pydjay.utils.protocol import MAGIC
#from pydjay.uix import clickable_area
#from pydjay.uix import long_press_button
#from pydjay.uix.slider import XSlider

#from pydjay.gui.files_screen import file_browser, location_browser
#from mediacentre.skins.default.theme import get_path

from kivy.logger import Logger

import pydjay.core


kv_string = """
<VolumeKnob@BoxLayout>:
    orientation: 'vertical'
    max: 2.0
    knob: volume_slide
    text: ""
    channel: ""
    controller: None
    volume_controls: None
    canvas:
        Color:
            rgba: 0.1,0.1,0.1,1
        Rectangle:
            size:self.size
            pos: self.pos

    Slider:
        orientation: 'vertical'
        id: volume_slide
        size_hint: 1,1
        min: 0
        max: root.max
        value: 1.0
        on_value: root.volume_controls.set_volume(root.channel, self.value) if root.volume_controls is not None else False
    Label:
        size_hint: 1, None
        height: 50
        text: "%s"%int(volume_slide.value * 100) + "%"
    Label:
        size_hint: 1, None
        height: 50
        text: root.text

<VolumeControls>:
    main_player_slider:main_player_slider
    main_player_monitor_slider:monitor_slider
    preview_player_slider: preview_slider
    main_player_monitor_mute_slider:main_player_monitor_mute_slider
    orientation: 'horizontal'
    title: "Volume setup:"
    auto_dismiss: True
    size_hint: None, None
    size: 700,500

    BoxLayout:
        orientation: 'horizontal'
        padding: [10,30,10,30]
        spacing: 20

        VolumeKnob:
            id: main_player_slider
            text: "Main player"
            max: 4.0
            channel: 'main_player'
            volume_controls: root.volume_controls

        VolumeKnob:
            id: monitor_slider
            text: "Monitor"
            max: 4.0
            channel: 'main_player_monitor'
            volume_controls: root.volume_controls

        VolumeKnob:
            id: preview_slider
            text: "Preview player"
            max: 10.0
            channel: 'preview_player'
            volume_controls: root.volume_controls

        VolumeKnob:
            id: main_player_monitor_mute_slider
            text: "Monitor mute"
            max: 0.5
            channel: 'main_player_monitor_mute'
            volume_controls: root.volume_controls


"""



class VolumeControls(Popup):
    player_choice = ObjectProperty(None)
    volume_controls = ObjectProperty(None)
    def __init__(self, deck, volume_controls):
        super(VolumeControls, self).__init__()
        self.deck = deck
        self.volume_controls = pydjay.core.volume_control
        Clock.schedule_once(self._post_init, -1)
        #self._broadcast = False
        #self._discovery_thread = None
        #self.bind(on_dismiss = self._stop_loop)
        #self.start_broadcast()


    def _post_init(self, *a):
        self.main_player_slider.knob.value              = self.volume_controls.get_volume('main_player')
        self.preview_player_slider.knob.value           = self.volume_controls.get_volume('preview_player')
        self.main_player_monitor_slider.knob.value      = self.volume_controls.get_volume('main_player_monitor')
        self.main_player_monitor_mute_slider.knob.value = self.volume_controls.get_volume('main_player_monitor_mute')



        
    #def _do_broadcast_loop(self):
    #    #while True:
    #    Logger.info('remote: Waiting for remote player')
    #    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #create UDP socket
    #    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #    s.bind(('', 8989))
    #    s.settimeout(.1)
    #    self._broadcast = True
    #    addresses = {}
    #    while self._broadcast:
    #        try:
    #            data, addr = s.recvfrom(1024)#sendto(data, ('<broadcast>', 8989))
    #            if data.startswith(MAGIC):
    #                data = data[len(MAGIC):]
    #            if addr[0] not in addresses:
    #                Logger.info('remote: Found new remote player')
    #                self._add_choice(data, addr[0])
    #                addresses[addr[0]] = data
    #        except socket.timeout:
    #            pass

        #print 'stopped'
        
    #@mainthread
    #def _add_choice(self, data, address):
    #    but = Button(text = data)
    #    but.bind(on_press = partial(self._connect, address, data))
    #    self.player_choice.add_widget(but)


    #def _stop_loop(self, *args):
    #    self._broadcast = False
        
    #    #def _stop(self, *args):
    #    #self.dismiss()


    #def _connect(self, address, name, *args):
    #    self.deck._do_connect_remote(address, name)
    #    self.dismiss()

                 
    #def start_broadcast(self):
    #    self._discovery_thread = threading.Thread(target = self._do_broadcast_loop)
    #    self._discovery_thread.start()





Builder.load_string(kv_string)
Factory.register('VolumeControls', VolumeControls)
#Factory.register('DisconnectFromRemote', DisconnectFromRemote)



buffer = []
if __name__ == '__main__':
    from kivy.base import runTouchApp
    #from mediacentre.database.TVShows import database_pickle
    from kivy.core.window import Window
    from kivy.clock import Clock
    from kivy.uix.button import Button
    ## red background color
    #from jmc.gui import config


    import gi
    import pprint
    import sys
    import urllib
    gi.require_version("Gst", "1.0")
    #gi.require_version('Gtk', '3.0')
    from gi.repository import Gst, GObject as gobject, GLib
    
    from struct import unpack_from


    from pydjay.library.track import load_file
    
  


    Window.clearcolor = (0.0,0,0, 1)
    #Window.width = 350
    #Window.height = 475
    Window.size = (1448, 350)
    #index = 0
    #def add_item(*a):
    #    global index
    #    index += 1
    #    #print index
    #    item = Button(text= '%s'%index)
    #    bar.add_page(item)
    
    #foo = WaveformGenerator("/Users/jihemme/Python/DJ/pydjay/audio/test.mp3", 35000)




   

    
    #def add_point(total_time, timestamp, value):
    #    global buffer
    #    bar.seekbar.waveform.x_max = total_time
    #    buffer.append((timestamp, value))
    #    if len(buffer) == 150:
    #        bar.seekbar.waveform.points.extend(buffer)
    #        buffer = []

            
    #def done_points(points):
    #    bar.seekbar.waveform.points = points
    #    #x = open('ttt.txt','w')
    #    #x.write(str(points))
    #    #x.close()
    #foo.set_data_point_callback(add_point)
    #foo.set_process_done_callback(done_points)
    #def _foo(*a):
    #    Clock.schedule_interval(add_item, 1)
    #db = database_pickle.Database('/Users/jihemme/mediaserver_data')
    #from kivy.clock import Clock
    #foo = AnchorLayout(size_hint = (1,1), anchor_x = 'center', anchor_y = 'center')
    #init_gui()
    
    bar = MainPlayerDeck()#Builder.load_string(kv_string)#FilesScreen(size_hint = (1,1))#size = (450,550))
    tra = load_file("/Users/jihemme/Python/DJ/Algiers Hoodooo Woman - Dr. Michael White (Dancing in the Sky) .mp3")
    bar.set_track(tra)
    bar.play()
    #bar.location_browser.set_default_locations()
    #bar.set_list(locations)
    #add_item()
    #add_item()
    
    #add_item()
    
    #add_item()
    
    #add_item()
    #Clock.schedule_once(add_item, 5)
    #button = Button(test="FOO",size_hint = (1,1))
    #bar.set_seasons(12)
    #bar.set_episodes(123, 45)
    #foo.add_widget(bar)
    #foo.add_widget(button)
    #button.bind(on_press = lambda *x: 
    #bar.set_show(db.get_tv_show('stargate-sg-1'))#db.get_tv_shows())
    runTouchApp(bar)#size=(400,200)))#, size_hint = (None, None)))
    bar.unload()
