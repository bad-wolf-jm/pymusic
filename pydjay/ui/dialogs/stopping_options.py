import os
import time
import array

from os.path import getsize
from datetime import datetime

from kivy.clock import mainthread, Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

from kivy.properties import ObjectProperty
from kivy.factory import Factory

from kivy.uix.modalview import ModalView
from pydjay.ui.elements import widgets, waveform_seekbar
from pydjay.ui.elements.utils import seconds_to_human_readable
import pydjay.bootstrap


stop_options_kv = """
<StopOptionsDialog>:
    size_hint: .5,.35
    id: skip_to_next_overlay
    canvas:
        Color:
            rgba: .7,0.7,0.7,.98
        Rectangle:
            size: self.size
            pos: self.pos
    BoxLayout:
        orientation: 'vertical'

        Label:
            canvas.before:
                Color:
                    rgba: .3,0.3,0.3,.98
                Rectangle:
                    size: self.size
                    pos: self.pos
            size_hint: 1,None
            height: 50
            font_size: 25
            markup: True
            halign: 'center'
            valign: 'middle'
            text_size: self.size
            text: "STOP/SKIP THE CURRENT SONG"

        Widget:
            size_hint: 1,1

        Button:
            size_hint: .5, None
            size: 100,60
            pos_hint:{'center_x':.5, 'center_y':.5}
            text: "STOP the current song"
            #disabled: not root.show_force_skip
            on_press: root.immediate_stop()
        Widget:
            size_hint: 1,1
        Button:
            size_hint: .5, None
            size: 100,60
            pos_hint:{'center_x':.5, 'center_y':.5}
            text: "SKIP to the next song"
            #disabled: not root.show_force_skip
            on_press: root.play_next_track()
        Widget:
            size_hint: 1,1
        Label:
            size_hint: 1,None
            height: 50
            font_size: 15
            markup: True
            halign: 'center'
            valign: 'middle'
            text_size: self.size
            text: "[color=#333333]Tap of click anywhere outside the dialog to dismiss.[/color]"
        Widget:
            size_hint: 1,1

"""


class StopOptionsDialog(ModalView):

    def play_next_track(self):
        pydjay.bootstrap.playback_manager.play_next_track()
        self.dismiss()

    def immediate_stop(self):
        pydjay.bootstrap.playback_manager.immediate_stop(True)
        self.dismiss()


Builder.load_string(stop_options_kv)
Factory.register('StopOptionsDialog', StopOptionsDialog)
