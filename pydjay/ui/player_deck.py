import os
import time

from kivy.clock import mainthread, Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.button import Button

from kivy.animation import Animation

from kivy.properties import ObjectProperty
from kivy.factory import Factory

#from pydjay.library import save_to_current_session

from elements import waveform_seekbar
from elements import widgets
#from elements.utils import seconds_to_human_readable
from kivy.logger import Logger
import pydjay.bootstrap
from pydjay.bootstrap import session_manager, play_queue, playback_manager

kv_string = """
<MainPlayerDeck>:
    #deck:                 deck
    wait_toggle: wait_toggle
    wait_time_input: wait_time
    start_queue_button:   start_queue_button
    stopping_message: stopping_message
    orientation: 'horizontal'
    size_hint: 1, 1
    RelativeLayout:
        id: deck
        size_hint: (1, 1)
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
    stopping_message = ObjectProperty(None)
    wait_time_input      = ObjectProperty(None)
    wait_toggle          = ObjectProperty(None)
    window               = ObjectProperty(None)
    
    def __init__(self, *args, **kw):
        super(MainPlayerDeck, self).__init__(*args, **kw)
        self._track              = None
        playback_manager.bind(queue_is_playing = self._watch_queue_data,
                              queue_stop_request = self._on_queue_stop_request)
        play_queue.bind(on_queue_content_change = self._watch_queue_data)
        Clock.schedule_once(self._post_init, -1)


    def _post_init(self, *args):
        self.wait_time_input.text = "%s"%playback_manager.wait_time
        self.wait_time_input.bind(focus = self._toggle_keyboard_shortcuts)

    def _toggle_keyboard_shortcuts(self, *a):
        if not self.wait_time_input.focus:
            self.window.restore_focus()
        else:
            self.window.suspend_focus()
    
    def set_volume_control(self, volume_control):
        self._volume_control = volume_control

    def set_wait_time(self, *args):
        try:
            t = int(self.wait_time_input.text)
            playback_manager.wait_time = t
        except:
            self.wait_time_input.text = '2'
            playback_manager.wait_time = 2
        self.wait_toggle.active = False
            
    def set_wait_time_by_focus(self, i, value):
        if not value:
            self.set_wait_time()
            
    def shutdown(self):
        pass
                
    def _watch_queue_data(self, *q):
        if not play_queue.is_empty:
            if not playback_manager.queue_is_playing:
                self.start_queue_button.text = "START"
                self.stopping_message.text = "" 
                self.start_queue_button.disabled = False
            else:
                self.start_queue_button.text = "STOP"
                self.stopping_message.text = "" 
                self.start_queue_button.disabled = False
                
        else:
            if not playback_manager.queue_is_playing:
                self.start_queue_button.text = "EMPTY"
                self.stopping_message.text = "" 
                self.start_queue_button.disabled = True

            
    def start_queue(self):
        if not playback_manager.queue_is_playing:
            playback_manager.start_queue()
        else:
            playback_manager.queue_stop_request = not playback_manager.queue_stop_request

    def _on_queue_stop_request(self, *a):
        if playback_manager.queue_stop_request:
            self.start_queue_button.text = 'CANCEL'
            self.stopping_message.text = "Queue will stop after this song"
        else:
            self._stop_counter = True
            self.start_queue_button.text = 'STOP'
            self.stopping_message.text = ""


        
    def _set_volume(self, *a):
        if self._volume_control is not None:
            self._volume_control.set_volume('main_player', self.volume)

Builder.load_string(kv_string)
Factory.register('MainPlayerDeck', MainPlayerDeck)
