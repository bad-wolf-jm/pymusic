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

#from pydjay.core.library import save_to_current_session

from kivy.uix.modalview import ModalView
from elements import widgets, waveform_seekbar
from elements.utils import seconds_to_human_readable
#from pydjay.gui import volume_slider
from pydjay.utils.protocol import MAGIC

from kivy.logger import Logger
import pydjay.bootstrap


kv_string = """
<MainPlayerDisplay>:
    seekbar:              seekbar
    display_window:       display_window
    album_art:            album_art
    artist_label:         artist_label
    title_label:          title_label
    time_remaining_label: time_remaining
    #player_stopped:       player_stopped.__self__
    #main_player_volume:   main_player_volume
    start_queue_button:    start_queue_button
    #stopping_message: stopping_message
    orientation: 'horizontal'
    size_hint: 1, 1
    #skip_to_next_overlay: skip_to_next_overlay.__self__
    #countdown: countdown.__self__
    size_hint: 1, 1

    StencilView:
        size_hint: 1,None
        height: 125
        RelativeLayout:
            size_hint: (None,None)
            size: self.parent.size
            pos: self.parent.pos
            id: display_window



            BoxLayout:
                orientation: 'horizontal'
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
                    BoxLayout:
                        orientation: 'horizontal'
                        size_hint: 1,1
                        BoxLayout:
                            orientation: 'vertical'
                            size_hint: 1,1
                            BoxLayout:
                                orientation: 'vertical'
                                size_hint: 1,1
                                padding: [10,3,5,5]
                                BoxLayout:
                                    orientation: 'horizontal'
                                    size_hint: 1,1
                                    #height:35
                                    spacing: 15
                                    Label:
                                        size_hint: 1,1
                                        id: title_label
                                        font_size:'20sp'
                                        bold: True
                                        #color: 0,0,0,1
                                        text: 'TITLE OF SONG'
                                        text_size: self.size
                                        halign: 'left'
                                        valign: 'middle'
                                        shorten: True
                                        ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}


                                    Label:
                                        size_hint: None,1
                                        id: time_remaining
                                        font_size:'20sp'
                                        width: 75
                                        bold: True
                                        #color: 0.8,0.8,0.8,1
                                        text: "0:00"
                                        text_size: self.size
                                        halign: 'left'
                                        valign:'middle'
                                        shorten: True
                                        ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}
                                BoxLayout:
                                    orientation: 'horizontal'
                                    size_hint: 1,1
                                    #height:35
                                    spacing: 15
                                    BoxLayout:
                                        orientation: 'vertical'
                                        size_hint: 1,1
                                        Label:
                                            size_hint: 1,1
                                            id:artist_label
                                            text: 'ARTIST - ALBUM'
                                            color: .6,.6,.6,1
                                            text_size: self.size
                                            halign: 'left'
                                            valign:'middle'
                                            font_size: 15
                                            shorten: True
                                            ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}

                                            #size_hint: 1, None
                                            #height:35

                                        Label:
                                            size_hint: 1,1
                                            id: countdown_label
                                            markup: True
                                            text: root.countdown_timeout #'Next song playing in 5 seconds'
                                            color: .6,.6,.6,1
                                            text_size: self.size
                                            halign: 'left'
                                            valign:'middle'
                                            shorten: True
                                            ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}

                                            font_size: 12
                                            #size_hint: 1, None
                                            #height:35

                                    #HorizontalBox:
                                    #    size_hint: 1,1
                                    #    padding: [5,10,5,3]
                                    #    Button:
                                    #        id: start_queue_button
                                    #        size_hint: None, 1
                                    #        size: 100,40
                                    #        pos_hint: {'center_y': .5}
                                    #        text: ''
                                    #        font_size: 20
                                    #        on_press: root.start_queue() #_start_play()
                                    #        pos: self.parent.width - 130, 10

                                    #    Label:
                                    #        id: stopping_message
                                    #        size_hint: None, None
                                    #        pos_hint: {'center_y': .5}
                                    #        halign: 'center'
                                    #        valign: 'middle'
                                    #        size: 125,75
                                    #        text_size: self.size
                                    #        text: ''
                                    #        font_size: 15
                                    #        pos: self.parent.width - 130, 65



                                    #ImageButton:
                                    #    size_hint: None, None
                                    #    size: 25,25
                                    #    pos_hint: {'top': 1}
                                    #    #text: 'SL'
                                    #    image:'atlas://pydjay/gui/images/resources/add_to_shortlist'
                                    #    on_press: root.show_eject_panel()

                                    ImageButton:
                                        id: start_queue_button
                                        size_hint: None, None
                                        size: 25,25
                                        opacity: 1 if not self.disabled else 0.25
                                        pos_hint: {'top': .75}
                                        #text: 'SL'
                                        image:'atlas://pydjay/gui/images/resources/play_2'
                                        on_press: root.start_queue()

                                    ImageButton:
                                        size_hint: None, None
                                        size: 25,25
                                        pos_hint: {'top': .75}
                                        #text: 'SL'
                                        image:'atlas://pydjay/gui/images/resources/pause_2'
                                        on_press: root.show_eject_panel()

                                    ImageButton:
                                        size_hint: None, None
                                        size: 25,25
                                        pos_hint: {'top': .75}
                                        #text: 'SL'
                                        image:'atlas://pydjay/gui/images/resources/settings'
                                        on_press: root.show_settings_panel()




                    HDivider:
                    WaveformSeekbar:
                        size_hint: 1, .5
                        id: seekbar

            #RelativeLayout:
            #    size_hint: 1,1
            #    id: skip_to_next_overlay
            #    canvas:
            #        Color:
            #            rgba: .3,0.3,0.3,.98
            #        Rectangle:
            #            size: self.size
            #            pos: self.pos
            #    Button:
            #        size_hint: None, None
            #        size: 100,50
            #        pos_hint:{'center_x':.25, 'center_y':.5}
            #        text: "EJECT"
            #        #disabled: not root.show_force_skip
            #        on_press: root.immediate_stop()
#
#                Button:
#                    size_hint: None, None
#                    size: 100,50
#                    pos_hint:{'center_x':.75, 'center_y':.5}
#                    text: "SKIP"
#                    #disabled: not root.show_force_skip
#                    on_press: root.play_next_track()
#                Button:
#                    size_hint: None, None
#                    size: 75,25
#                    pos_hint:{'right':1, 'y':0}
#                    text: "Cancel"
#                    #disabled: not root.show_force_skip
#                    on_press: root.dismiss_eject_panel()

#            RelativeLayout:
#                size_hint: 1,1
#                id: countdown
#                disabled: False
#                #opacity: 1 if root.show_force_skip else 0
#                canvas:
#                    Color:
#                        rgba: 0,0,0,.8
#                    Rectangle:
#                        size: self.size
#                        pos: 0,0 #self.pos
#
#                BoxLayout:
#                    orientation: 'vertical'
#                    size_hint: .5, 1
#                    pos_hint: {'center_x':.5, 'center_y':.5}
#                    height: 50
#                    spacing: 10
#                    padding:[0,10,0,10]
#                    Label:
#                        size_hint: 1,1
#                        height: 40
#                        font_size: 20
#                        markup: True
#                        halign: 'center'
#                        valign: 'top'
#                        text_size: self.size
#                        text: root.countdown_timeout
#                    Button:
#                        id: start_queue_button_XXX
#                        size_hint: None, None
#                        size: 200,40
#                        pos_hint:{'center_x':.5, 'center_y':.5}
#                        text: "PLAY NOW"
#                        #disabled: not root.show_force_skip
#                        on_press: root.play_next_track()


            #RelativeLayout:
            #    size_hint: 1,1
            #    id: player_stopped
            #    disabled: False
            #    #opacity: 1 if root.show_force_skip else 0
            #    canvas:
            #        Color:
            #            rgba: 0,0,0,.9
            #        Rectangle:
            #            size: self.size
            #            pos: 0,0 #self.pos

            #    BoxLayout:
            #        orientation: 'vertical'
            #        size_hint: .5, 1
            #        pos_hint: {'center_x':.5, 'center_y':.5}
            #        height: 50
            #        spacing: 10
            #        padding:[0,10,0,10]
            #        Label:
            #            size_hint: 1,1
            #            height: 40
            #            font_size: 20
            #            markup: True
            #            halign: 'center'
            #            valign: 'middle'
            #            text_size: self.size
            #            text: "No track currently playing"
"""


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
#                        Widget:
#                            size_hint: 1,1

"""



class PlaybackSettingsDialog(ModalView):
    #stopping_message = ObjectProperty(None)
    #wait_time_input      = ObjectProperty(None)
    #wait_toggle          = ObjectProperty(None)
    #window               = ObjectProperty(None)

    def __init__(self, *args, **kw):
        super(PlaybackSettingsDialog, self).__init__(*args, **kw)
#        self._track              = None
#        playback_manager.bind(queue_is_playing   = self._watch_queue_data,
#                              queue_stop_request = self._on_queue_stop_request)
#        play_queue.bind(on_queue_content_change = self._watch_queue_data)
        Clock.schedule_once(self._post_init, -1)


    def _post_init(self, *args):
        self.wait_time_input.text = "%s"%pydjay.bootstrap.playback_manager.wait_time
        #self.wait_time_input.bind(focus = self._toggle_keyboard_shortcuts)

#    def _toggle_keyboard_shortcuts(self, *a):
#        if not self.wait_time_input.focus:
#            self.window.restore_focus()
#        else:
#            self.window.suspend_focus()

    def set_volume_control(self, volume_control):
        self._volume_control = volume_control

    def set_wait_time(self, *args):
        try:
            t = int(self.wait_time_input.text)
            pydjay.bootstrap.playback_manager.wait_time = t
        except:
            self.wait_time_input.text = '2'
            pydjay.bootstrap.playback_manager.wait_time = 2
        #self.wait_toggle.active = False

    def set_wait_time_by_focus(self, i, value):
        if not value:
            self.set_wait_time()

#    def shutdown(self):
#        pass

#    def _watch_queue_data(self, *q):
#        if not play_queue.is_empty:
#            if not playback_manager.queue_is_playing:
#                self.start_queue_button.text = "START"
#                self.stopping_message.text = ""
#                self.start_queue_button.disabled = False
#            else:
#                self.start_queue_button.text = "STOP"
#                self.stopping_message.text = ""
#                self.start_queue_button.disabled = False
#
#        else:
#            if not playback_manager.queue_is_playing:
#                self.start_queue_button.text = "EMPTY"
#                self.stopping_message.text = ""
#                self.start_queue_button.disabled = True

#
#    def start_queue(self):
#        if not playback_manager.queue_is_playing:
#            playback_manager.start_queue()
#        else:
#            playback_manager.queue_stop_request = not playback_manager.queue_stop_request

#    def _on_queue_stop_request(self, *a):
#        if playback_manager.queue_stop_request:
#            self.start_queue_button.text = 'CANCEL'
#            self.stopping_message.text = "Queue will stop after this song"
#        else:
#            self._stop_counter = True
#            self.start_queue_button.text = 'STOP'
#            self.stopping_message.text = ""



#    def _set_volume(self, *a):
#        if self._volume_control is not None:
#            self._volume_control.set_volume('main_player', self.volume)

Builder.load_string(settings_dialog_kv)
Factory.register('PlaybackSettingsDialog', PlaybackSettingsDialog)


class MainPlayerDisplay(BoxLayout):
    seekbar           = ObjectProperty(None)
    title_label       = ObjectProperty(None)
    artist_label      = ObjectProperty(None)
    album_art         = ObjectProperty(None)
    #skip_to_next_overlay = ObjectProperty(None)
    display_window       = ObjectProperty(None)
    countdown            = ObjectProperty(None)
    countdown_timeout    = StringProperty("")


    def __init__(self, *args, **kw):
        super(MainPlayerDisplay, self).__init__(*args, **kw)
        self._track              = None
        self._duration = None
        self.countdown_timeout = ""
        self._countdown_timeout = 0
        pydjay.bootstrap.playback_manager.bind(track               = self.set_track,
                                               track_duration      = self._update,
                                               track_position      = self._update,
                                               remaining_time      = self._update,
                                               on_end_of_stream    = self._on_eos,
                                               on_queue_started    = self.dismiss_stopped_state,
                                               on_queue_stopped    = self.display_stopped_state,
                                               on_playback_started = self._on_playback_started)
        pydjay.bootstrap.playback_manager.bind(queue_is_playing   = self._watch_queue_data,
                                               queue_stop_request = self._on_queue_stop_request)
        pydjay.bootstrap.play_queue.bind(on_queue_content_change = self._watch_queue_data)

        Clock.schedule_once(self._post_init, -1)

    def _post_init(self, *args):
        #self.display_window.remove_widget(self.skip_to_next_overlay)
        #self.display_window.remove_widget(self.countdown)
        #self.player_stopped.pos = 0,0
        pass

    def _watch_queue_data(self, *q):
        if not pydjay.bootstrap.play_queue.is_empty:
            if not pydjay.bootstrap.playback_manager.queue_is_playing:
                #self.start_queue_button.text = "START"
                #self.stopping_message.text = ""
                self.countdown_timeout = ""
                self._stop_blink_indicator()

                self.start_queue_button.disabled = False
            else:
                #self.start_queue_button.text = "STOP"
                #self.stopping_message.text = ""
                self.countdown_timeout = ""
                self._stop_blink_indicator()

                self.start_queue_button.disabled = False

        else:
            if not pydjay.bootstrap.playback_manager.queue_is_playing:
                #self.start_queue_button.text = "EMPTY"
                #self.stopping_message.text = ""
                self.start_queue_button.disabled = True


    def start_queue(self):
        if not pydjay.bootstrap.playback_manager.queue_is_playing:
            pydjay.bootstrap.playback_manager.start_queue()
        else:
            pydjay.bootstrap.playback_manager.queue_stop_request = not pydjay.bootstrap.playback_manager.queue_stop_request


    def _blink(self, *a):
        self.start_queue_button.opacity = (0 if self.start_queue_button.opacity == 1 else 1)

    def _start_blink_indicator(self):
        Clock.schedule_interval(self._blink, 0.5)

    def _stop_blink_indicator(self):
        Clock.unschedule(self._blink)
        self.start_queue_button.opacity = 1

    def _on_queue_stop_request(self, *a):
        if pydjay.bootstrap.playback_manager.queue_stop_request:
            #self.start_queue_button.text = 'CANCEL'
            self.countdown_timeout = "Queue will stop after this song"
            self._start_blink_indicator()
        else:
            #self._stop_counter = True
            #self.start_queue_button.text = 'STOP'
            self.countdown_timeout = ""
            self._stop_blink_indicator()

    def show_eject_panel(self, *a):
        foo = StopOptionsDialog()
        foo.open()


    def show_settings_panel(self, *a):
        foo = PlaybackSettingsDialog()
        foo.open()
        #self.display_window.add_widget(self.skip_to_next_overlay)

    #def dismiss_eject_panel(self, *a):
    #    self.display_window.remove_widget(self.skip_to_next_overlay)

    def _update_volume(self, *args):
        self.main_player_volume.volume = pydjay.bootstrap.volume_control.main_player

    def shutdown(self):
        try:
            self._player.shutdown()
        except:
            pass

    def _on_playback_started(self, *a):
        self.dismiss_countdown()

    def immediate_stop(self):
        pydjay.bootstrap.playback_manager.immediate_stop(True)
        #self.display_window.remove_widget(self.skip_to_next_overlay)

    def _update_countdown(self, *a):
        self._countdown_timeout -= 1
        if self._countdown_timeout > 0:
            self.countdown_timeout = '[color=#aaaaaa]Next track will play in [/color] [b]%s seconds[/b]'% self._countdown_timeout
        else:
            self.countdown_timeout = "" #s[b]The next track should be playing now...[/b]"

    def display_countdown(self, timeout):
        self._countdown_timeout = timeout
        self.countdown_timeout = "[color=#aaaaaa]Next track will play in: [/color] [b]%s seconds[/b]"% self._countdown_timeout
        Clock.schedule_interval(self._update_countdown, 1)
        #self.display_window.add_widget(self.countdown) #.pos = 0,0

    def dismiss_countdown(self, *args):
        Clock.unschedule(self._update_countdown)
        self.countdown_timeout = ""
        #self.display_window.remove_widget(self.countdown)

    def display_stopped_state(self, timeout):
        pass
        #elf.display_window.add_widget(self.player_stopped)

    def dismiss_stopped_state(self, *args):
        pass
        #self.display_window.remove_widget(self.player_stopped)

    def _on_eos(self, *args):
        Logger.info('MainPlayer: End of stream %s', self._track)
        self.display_countdown(pydjay.bootstrap.playback_manager.wait_time)

    def play_next_track(self):
        Logger.info('MainPlayer: Skipping end of track <%s>', self._track)
        self._duration = None
        #self.display_window.remove_widget(self.skip_to_next_overlay)
        pydjay.bootstrap.playback_manager.play_next_track()

    def set_track(self, i, track):
        Logger.info('MainPlayer: Setting track')
        self._track = track
        if self._track is not None:
            self.artist_label.text = (self._track.metadata.artist + u' - ' + self._track.metadata.album).upper()
            self.title_label.text = (self._track.metadata.title).upper()
            if self._track.metadata.album_cover is not None:
                try:
                    self.album_art.source = self._track.metadata.album_cover['medium']
                except:
                    self.album_art.source = 'atlas://pydjay/gui/images/resources/default_album_cover'
            else:
                self.album_art.source = 'atlas://pydjay/gui/images/resources/default_album_cover'

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
                self.seekbar.waveform.points =  points
            except EOFError:
                ll = arr.tolist()
                offset = 0
                points = [ll[offset:offset+2] for offset in range(0, len(ll) - 1, 2)]
                points = sorted(points, cmp = lambda x,y: cmp(x[0], y[0]))
                self.seekbar.waveform.points =  points
            except Exception, details:
                print details
                self.seekbar.waveform.points = []
            finally:
                try:
                    f.close()
                except:
                    pass

    def _update(self, *a):
        self._duration = pydjay.bootstrap.playback_manager.track_duration
        if self._duration is not None:
            t_l =  pydjay.bootstrap.playback_manager.track_length
            t_l = t_l if t_l is not None else self._duration
            self.seekbar.max_value      = t_l
            self.seekbar.waveform.x_max = t_l
        else:
            self.seekbar.max_value = 1
        position = pydjay.bootstrap.playback_manager.track_position or 0
        duration = pydjay.bootstrap.playback_manager.track_duration

        if duration is None:
            self.time_remaining_label.text = ""
        else:
            position = min(position, duration)
            self.time_remaining_label.text = "-"+seconds_to_human_readable((duration - position) / 1000000000)
            self.seekbar.value = position



Builder.load_string(kv_string)
Factory.register('MainPlayerDisplay', MainPlayerDisplay)
