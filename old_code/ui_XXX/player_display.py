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
from elements import widgets, waveform_seekbar
from elements.utils import seconds_to_human_readable
from kivy.logger import Logger

from pydjay.ui.dialogs.stopping_options import StopOptionsDialog
from pydjay.ui.dialogs.playback_settings import PlaybackSettingsDialog
import pydjay.bootstrap


kv_string = """
<MainPlayerDisplay>:
    seekbar:              seekbar
    display_window:       display_window
    album_art:            album_art
    artist_label:         artist_label
    title_label:          title_label
    time_remaining_label: time_remaining
    start_queue_button:    start_queue_button
    orientation: 'horizontal'
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
"""

class MainPlayerDisplay(BoxLayout):
    seekbar = ObjectProperty(None)
    title_label = ObjectProperty(None)
    artist_label = ObjectProperty(None)
    album_art = ObjectProperty(None)
    display_window = ObjectProperty(None)
    countdown = ObjectProperty(None)
    countdown_timeout = StringProperty("")

    def __init__(self, *args, **kw):
        super(MainPlayerDisplay, self).__init__(*args, **kw)
        self._track = None
        self._duration = None
        self.countdown_timeout = ""
        self._countdown_timeout = 0
        pydjay.bootstrap.playback_manager.bind(track=self.set_track,
                                               track_duration=self._update,
                                               track_position=self._update,
                                               remaining_time=self._update,
                                               on_end_of_stream=self._on_eos,
                                               on_queue_started=self.dismiss_stopped_state,
                                               on_queue_stopped=self.display_stopped_state,
                                               on_playback_started=self._on_playback_started)
        pydjay.bootstrap.playback_manager.bind(queue_is_playing=self._watch_queue_data,
                                               queue_stop_request=self._on_queue_stop_request)
        pydjay.bootstrap.play_queue.bind(on_queue_content_change=self._watch_queue_data)

        Clock.schedule_once(self._post_init, -1)

    def _post_init(self, *args):
        pass

    def _watch_queue_data(self, *q):
        if not pydjay.bootstrap.play_queue.is_empty:
            if not pydjay.bootstrap.playback_manager.queue_is_playing:
                self.countdown_timeout = ""
                self._stop_blink_indicator()
                self.start_queue_button.disabled = False
            else:
                self.countdown_timeout = ""
                self._stop_blink_indicator()
                self.start_queue_button.disabled = False

        else:
            if not pydjay.bootstrap.playback_manager.queue_is_playing:
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
            self.countdown_timeout = "Queue will stop after this song"
            self._start_blink_indicator()
        else:
            self.countdown_timeout = ""
            self._stop_blink_indicator()

    def show_eject_panel(self, *a):
        foo = StopOptionsDialog()
        foo.open()

    def show_settings_panel(self, *a):
        foo = PlaybackSettingsDialog()
        foo.open()

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

    def _update_countdown(self, *a):
        self._countdown_timeout -= 1
        if self._countdown_timeout > 0:
            self.countdown_timeout = '[color=#aaaaaa]Next track will play in [/color] [b]%s seconds[/b]' % self._countdown_timeout
        else:
            self.countdown_timeout = ""

    def display_countdown(self, timeout):
        self._countdown_timeout = timeout
        self.countdown_timeout = "[color=#aaaaaa]Next track will play in: [/color] [b]%s seconds[/b]" % self._countdown_timeout
        Clock.schedule_interval(self._update_countdown, 1)

    def dismiss_countdown(self, *args):
        Clock.unschedule(self._update_countdown)
        self.countdown_timeout = ""

    def display_stopped_state(self, timeout):
        pass

    def dismiss_stopped_state(self, *args):
        pass

    def _on_eos(self, *args):
        Logger.info('MainPlayer: End of stream %s', self._track)
        self.display_countdown(pydjay.bootstrap.playback_manager.wait_time)

    def play_next_track(self):
        Logger.info('MainPlayer: Skipping end of track <%s>', self._track)
        self._duration = None
        pydjay.bootstrap.playback_manager.play_next_track()

    def set_track(self, i, track):
        Logger.info('MainPlayer: Setting track')
        self._track = track
        if self._track is not None:
            self.artist_label.text = (self._track.metadata.artist +
                                      u' - ' + self._track.metadata.album).upper()
            self.title_label.text = (self._track.metadata.title).upper()
            if self._track.metadata.album_cover is not None:
                try:
                    self.album_art.source = self._track.metadata.album_cover['medium']
                except:
                    self.album_art.source = 'atlas://pydjay/gui/images/resources/default_album_cover'
            else:
                self.album_art.source = 'atlas://pydjay/gui/images/resources/default_album_cover'

            Logger.info(
                'MainPlayer: Setting the waveform to the track\'s waveform, track length: %s', self._track.info.length)
            if self._track.info.length is not None:
                self.seekbar.max_value = self._track.info.stream_length
                self.seekbar.waveform.x_max = self._track.info.stream_length
            try:
                f = open(self._track.metadata.waveform, 'rb')
                arr = array.array('f')
                num_points = int(f.readline().split('\n')[0])
                arr.fromfile(f, num_points)
                ll = arr.tolist()
                offset = 0
                points = [ll[offset:offset + 2] for offset in range(0, len(ll) - 1, 2)]
                points = sorted(points, cmp=lambda x, y: cmp(x[0], y[0]))
                self.seekbar.waveform.points = points
            except EOFError:
                ll = arr.tolist()
                offset = 0
                points = [ll[offset:offset + 2] for offset in range(0, len(ll) - 1, 2)]
                points = sorted(points, cmp=lambda x, y: cmp(x[0], y[0]))
                self.seekbar.waveform.points = points
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
            t_l = pydjay.bootstrap.playback_manager.track_length
            t_l = t_l if t_l is not None else self._duration
            self.seekbar.max_value = t_l
            self.seekbar.waveform.x_max = t_l
        else:
            self.seekbar.max_value = 1
        position = pydjay.bootstrap.playback_manager.track_position or 0
        duration = pydjay.bootstrap.playback_manager.track_duration

        if duration is None:
            self.time_remaining_label.text = ""
        else:
            position = min(position, duration)
            self.time_remaining_label.text = "-" + \
                seconds_to_human_readable((duration - position) / 1000000000)
            self.seekbar.value = position


Builder.load_string(kv_string)
Factory.register('MainPlayerDisplay', MainPlayerDisplay)
