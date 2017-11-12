import os
import re
import mimetypes
import array

from functools import partial
from threading import Thread
from os.path import getsize
from datetime import datetime


from kivy.graphics import Mesh, Color, Rectangle, Line, RoundedRectangle, Ellipse
from kivy.clock import mainthread, Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget

from kivy.properties import ObjectProperty, NumericProperty
from kivy.factory import Factory

#from kivy.uix.popup import Popup

#from pydjay.uix import waveform_seekbar
from elements import volume_slider
#from pydjay.gui.utils import seconds_to_human_readable
from kivy.animation import Animation
import pydjay.bootstrap


kv_string = """
<Mixer>:
    main_player_volume: main_player_volume
    preview_volume: preview_volume
    monitor_volume: monitor_volume

    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            orientation: 'horizontal'
            size_hint: 1, 1
            #width: 140
            padding: [5,5,5,5] 
            spacing: 20

            BoxLayout:
                orientation: 'vertical'
                size_hint: None, 1
                width: 75
                spacing: 3
                Label:
                    text: "Preview"
                    font_size: 13
                    text_size: self.size
                    halign: 'center'
                    valign: 'middle'
                    size_hint: 1, None
                    height: 11
                VolumeLevel:
                    id: preview_volume
                    size_hint: 1, 1
                    font_size: 15
                    width: 75
                    bold: True

            Widget:
                size_hint: 1,1

            BoxLayout:
                orientation: 'vertical'
                size_hint: None, 1
                width: 75
                spacing: 3
                Label:
                    text: "Monitor"
                    font_size: 13
                    text_size: self.size
                    halign: 'center'
                    valign: 'middle'
                    size_hint: 1, None
                    height: 11
                VolumeLevel:
                    id: monitor_volume
                    size_hint: None, 1
                    font_size: 15
                    width: 75
                    bold: True
            Widget:
                size_hint: 1,1

            BoxLayout:
                orientation: 'vertical'
                size_hint: None, 1
                width: 75
                spacing: 3
                Label:
                    text: "Main"
                    font_size: 13
                    text_size: self.size
                    halign: 'center'
                    valign: 'middle'
                    size_hint: 1, None
                    height: 11
                VolumeLevel:
                    id:  main_player_volume
                    size_hint: None, 1
                    font_size: 15
                    width: 75
                    bold: True

"""


class Mixer(RelativeLayout):
    main_player_volume = ObjectProperty(None)
    monitor_volume = ObjectProperty(None)
    preview_volume = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        super(Mixer, self).__init__(*args, **kwargs)
        self.volume_controls = None
        self._save_monitor_volume = 1.0
        pydjay.bootstrap.volume_control.bind(main_player_monitor=self._update_monitor_volume,
                                             preview_player=self._update_preview_volume,
                                             main_player=self._update_main_player_volume)
        self._duration = None
        Clock.schedule_once(self._post_init, -1)

    def _update_monitor_volume(self, *args):
        self.monitor_volume.volume = pydjay.bootstrap.volume_control.main_player_monitor

    def _update_preview_volume(self, *args):
        self.preview_volume.volume = pydjay.bootstrap.volume_control.preview_player

    def _update_main_player_volume(self, *args):
        self.main_player_volume.volume = pydjay.bootstrap.volume_control.main_player

    def _set_monitor_volume(self, *args):
        pydjay.bootstrap.volume_control.main_player_monitor = self.monitor_volume.volume

    def _set_preview_volume(self, *args):
        pydjay.bootstrap.volume_control.preview_player = self.preview_volume.volume

    def _set_main_player_volume(self, *args):
        pydjay.bootstrap.volume_control.main_player = self.main_player_volume.volume

    def _post_init(self, *a):
        self.preview_volume.bind(volume=self._set_preview_volume)
        self.monitor_volume.bind(volume=self._set_monitor_volume)
        self.main_player_volume.bind(volume=self._set_main_player_volume)

    def _update_track_end(self, *a):
        if self._track is not None:
            self._track.info.end_time = self.cut_window.track_end
        self._update_track_labels()

    def _on_eos(self, *a):
        pass

    def _set_volume(self, i, value):
        self.volume_controls.set_volume('main_player_monitor', self.volume)


Builder.load_string(kv_string)
Factory.register('Mixer', Mixer)
