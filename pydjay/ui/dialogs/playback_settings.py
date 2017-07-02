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
from kivy.logger import Logger
import pydjay.bootstrap


settings_dialog_kv = """
<PlaybackSettingsDialog>:
    #deck:                 deck
    #wait_toggle: wait_toggle
    wait_time_input: wait_time
    #start_queue_button:   start_queue_button
    #stopping_message: stopping_message
    #orientation: 'horizontal'
    size_hint: .5, .5

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
            text: "PLAYBACK SETTINGS"


        BoxLayout:
            orientation: 'vertical'
            size_hint: 1,1
            padding:[10,10,10,10]
            Label:
                size_hint: 1,None
                height: 20
                font_size: 20
                color: .2,.2,.2,1
                markup: True
                halign: 'left'
                valign: 'middle'
                text_size: self.size
                text: "Queue Management:"
            Widget:
                size_hint: None, None
                height:15
            VerticalBox:
                size_hint: 1,1
                HorizontalBox:
                    size_hint: 1, None
                    height: 15
                    padding: [20,0,0,0]
                    CheckBox:
                        id: wait_toggle
                        size_hint: None, 1
                        width: self.height

                    HorizontalBox:
                        Label:
                            size_hint: None, None
                            pos_hint: {'center_y': .5}
                            color: .2,.2,.2,1

                            halign: 'center'
                            valign: 'middle'
                            size: 50,20
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
                                    rgba: .6,.6,.6,1
                                Rectangle:
                                    pos:  self.pos
                                    size: self.size

                            TextInput:
                                id: wait_time
                                size_hint: 1,1
                                font_size: 15
                                pos_hint: {'center_y':.5}
                                multiline: False
                                color: .2,.2,.2,1
                                halign: 'center'
                                valign: 'middle'
                                text_size: self.width, self.height
                                text: '' #####tr(pydjay.bootstrap.playback_manager.wait_time)
                                foreground_color: 1,1,1,.8
                                background_color: 0,0,0,0
                                on_text_validate: root.set_wait_time(*args)
                                on_focus: root.set_wait_time_by_focus(*args)
                        Label:
                            size_hint: 1, None
                            height: 20
                            pos_hint: {'center_y': .5}
                            color: .2,.2,.2,1
                            halign: 'left'
                            valign: 'middle'
                            #size: 125,75
                            text_size: self.size
                            text: 'seconds between songs'
                            font_size: 15
                            pos: self.parent.width - 130, 65
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
"""


class PlaybackSettingsDialog(ModalView):
    def __init__(self, *args, **kw):
        super(PlaybackSettingsDialog, self).__init__(*args, **kw)
        Clock.schedule_once(self._post_init, -1)

    def _post_init(self, *args):
        self.wait_time_input.text = "%s" % pydjay.bootstrap.playback_manager.wait_time

    def set_volume_control(self, volume_control):
        self._volume_control = volume_control

    def set_wait_time(self, *args):
        try:
            t = int(self.wait_time_input.text)
            pydjay.bootstrap.playback_manager.wait_time = t
        except:
            self.wait_time_input.text = '2'
            pydjay.bootstrap.playback_manager.wait_time = 2

    def set_wait_time_by_focus(self, i, value):
        if not value:
            self.set_wait_time()

Builder.load_string(settings_dialog_kv)
Factory.register('PlaybackSettingsDialog', PlaybackSettingsDialog)
