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

from kivy.uix.popup import Popup

from elements import waveform_seekbar
#from pydjay.gui import volume_slider
from elements.utils import seconds_to_human_readable
from kivy.animation import Animation
import pydjay.bootstrap


kv_string = """
<PlayPauseButton@ImageButton>:
    play: 'atlas://pydjay/gui/images/resources/play_2' #get_path('play')
    pause: 'atlas://pydjay/gui/images/resources/pause_2'#get_path('pause')
    media_state: "pause"
    image: self.play if self.media_state == 'pause' else self.pause

<PreviewPlayer>:
    seekbar: seekbar
    album_cover: album_art
    artist_label: artist_label
    title_label:  title_label
    #album_label:  album_label
    length_label:  length_label
    position_label:  position_label
    #preview_volume: preview_volume
    #monitor_volume: monitor_volume
    title: "PREVIEW"
    title_color: 1,1,1,1
    artist_color: .7,.7,.7,1
    time_color: 1,1,1,1

    BoxLayout:
        orientation: 'vertical'

        padding: [7,7,7,7]
        spacing: 0
        size_hint: 1, 1

        BoxLayout:
            orientation: 'horizontal'
            size_hint: 1, 1
            #height: 100
            spacing: 20
            RelativeLayout:
                size_hint: None, 1
                width: self.height

                Image:
                    id: album_art
                    size_hint: 1, 1
                    #width: self.height
                    source: 'atlas://pydjay/gui/images/resources/default_album_cover'
                    allow_stretch: True
                    keep_ratio: True
            BoxLayout:
                orientation: 'vertical'
                size_hint: 1,1
                spacing: 6
                Label:
                    id: title_label
                    size_hint: 1,1
                    #shorten: True
                    text: "<No track being previewed>"
                    color: root.title_color
                    text_size: self.size
                    font_size: 15
                    bold: True
                    halign: 'left'
                    valign: 'middle'
                    shorten: True
                    ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}

                Label:
                    id: artist_label
                    size_hint: 1,1
                    text: ""
                    color: root.artist_color #.7,.7,.7,1
                    text_size: self.size
                    font_size: 15
                    halign: 'left'
                    valign: 'middle'
                    shorten: True
                    ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}

                BoxLayout:
                    orientation: 'vertical'
                    size_hint: 1,None
                    height: 30
                    padding:[0,0,0,0]
                    ProgressBar:
                        id: seekbar
                        pos_hint: {'center_y': 0.5}
                        size_hint: 1,None
                        height: 10
                        on_touch_down: root._do_seek(*args)

                    BoxLayout:
                        orientation: 'horizontal'
                        size_hint: 1, None
                        height: 15
                        Label:
                            id: position_label
                            size_hint: None, 1
                            width: 40
                            text_size: self.size
                            text: "0:00"
                            #color: .9,.9,.9,1
                            color: root.time_color
                            halign: 'left'
                            valign: 'middle'
                            shorten: True
                            ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}
                            font_size: 13

                        Widget:
                            size_hint: 1,None

                        Label:
                            id: length_label
                            size_hint: None, 1
                            width: 40
                            text_size: self.size
                            text: "0:00"
                            color: root.time_color
                            #color: .9,.9,.9,1
                            halign: 'right'
                            valign: 'middle'
                            shorten: True
                            ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}
                            font_size: 13

"""


class PreviewPlayer(RelativeLayout):
    seekbar = ObjectProperty(None)
    turntable = ObjectProperty(None)
    cut_window = ObjectProperty(None)
    start_time_label = ObjectProperty(None)
    end_time_label = ObjectProperty(None)
    album_cover = ObjectProperty(None)
    track = ObjectProperty(None)
    title_label = ObjectProperty(None)
    artist_label = ObjectProperty(None)
    queue = ObjectProperty(None)
    short_list = ObjectProperty(None)
    window = ObjectProperty(None)
    volume = NumericProperty(1.0)
    volume_controls = ObjectProperty(None)
    player = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        super(PreviewPlayer, self).__init__(*args, **kwargs)
        self._track = None
        self.player = pydjay.bootstrap.preview_player
        self.player.player.bind(on_end_of_stream=self._on_eos,
                                track_duration=self._update,
                                track_position=self._update)
        self.volume_controls = None
        self._save_monitor_volume = 1.0
        self._duration = None
        Clock.schedule_once(self._post_init, -1)

    def _post_init(self, *a):
        pass

    def _update_track_labels(self, *a):
        if self._track is not None:
            self.start_time_label.opacity = 1
            self.end_time_label.opacity = 1

            self.start_time_label.text = seconds_to_human_readable(self._track.info.start_time / 1000000000) \
                if self._track.info.start_time is not None \
                else '0:00'
            self.end_time_label.text = seconds_to_human_readable(self._track.info.end_time / 1000000000) \
                if self._track.info.end_time is not None \
                else seconds_to_human_readable(self._track.info.stream_length / 1000000000)
            x_factor = float(self.cut_window.width) / \
                self.cut_window.track_length if self.cut_window.track_length is not 0 else 1
            self.start_time_label.center_x = self.cut_window.track_start * \
                x_factor if self.cut_window.track_start is not None else 0
            self.end_time_label.center_x = self.cut_window.track_end * \
                x_factor if self.cut_window.track_end is not None else self.width

        else:
            self.start_time_label.opacity = 0
            self.end_time_label.opacity = 0

    def _update_track_start(self, *a):
        if self._track is not None:
            self._track.info.start_time = self.cut_window.track_start
        self._update_track_labels()

    def _update_track_end(self, *a):
        if self._track is not None:
            self._track.info.end_time = self.cut_window.track_end
        self._update_track_labels()

    def _on_eos(self, *a):
        pass

    def play(self, track):
        self.set_track(track)
        if self._track is not None:
            self.player.play(track)

    def pause(self):
        self.player.pause()

    def stop(self):
        self.player.stop()

    def _do_seek(self, window, event):
        if self.seekbar.collide_point(*event.pos):
            x_coord = event.pos[0] - self.seekbar.x
            factor = float(x_coord) / self.seekbar.width
            val = factor * self.seekbar.max
            self.player.seek(int(val))
            return False
        return True

    def set_track(self, track):
        self.player.stop()
        self._track = track
        self._duration = None
        self.length_label.text = seconds_to_human_readable(0)
        self.position_label.text = seconds_to_human_readable(0)
        self.seekbar.value = 0
        self.seekbar.max = 1
        if self._track is not None:
            self.artist_label.text = self._track.metadata.artist + u' - ' + self._track.metadata.album
            self.title_label.text = self._track.metadata.title
            #self.album_label.text  = self._track.metadata.album
            if self._track.metadata.album_cover is not None:
                try:
                    self.album_cover.source = self._track.metadata.album_cover['small']
                except:
                    self.album_cover.source = 'atlas://pydjay/gui/images/resources/default_album_cover'
            else:
                self.album_cover.source = 'atlas://pydjay/gui/images/resources/default_album_cover'

    def _update(self, *a):
        if self._duration is None:
            self._duration = self.player.track_duration
            if self._duration is not None:
                self.seekbar.max = self._duration
                self.length_label.text = seconds_to_human_readable(self._duration / 1000000000)
            else:
                self.length_label.text = seconds_to_human_readable(0)
                self.seekbar.max = 1
        position = self.player.track_position or 0
        duration = self._duration
        if duration is not None:
            self.seekbar.value = position
            self.position_label.text = seconds_to_human_readable(position / 1000000000)
        else:
            self.position_label.text = seconds_to_human_readable(0)


Builder.load_string(kv_string)
Factory.register('PreviewPlayer', PreviewPlayer)
