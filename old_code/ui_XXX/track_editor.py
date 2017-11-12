#import os
#import re
#import mimetypes
import array

#from functools import partial
#from threading import Thread
#from os.path import getsize
#from datetime import datetime

from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Line, Ellipse, Triangle
from kivy.clock import mainthread, Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty
#from kivy.uix.boxlayout import BoxLayout
#from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label

from kivy.properties import NumericProperty
from kivy.factory import Factory

#from kivy.uix.popup import Popup
from kivy.uix.modalview import ModalView

#from pydjay.audio.wavegen import WaveformGenerator
#from pydjay.audio.gst import AudioDecoder

#from pydjay.audio.player.player import AudioPlayer

from elements import waveform_seekbar  # screen, paged_grid, paged_display
#from pydjay.gui.turntable import turntable
from elements.utils import seconds_to_human_readable
#from pydjay.uix import memory_image, clickable_area
from kivy.animation import Animation
#from pydjay.uix import long_press_button
#from pydjay.uix import screen

#from pydjay.gui.files_screen import file_browser, location_browser
#from mediacentre.skins.default.theme import get_path
import pydjay.bootstrap


kv_string = """
<PlayPauseButton@ImageButton>:
    play: 'atlas://pydjay/gui/images/resources/play_2' #get_path('play')
    pause: 'atlas://pydjay/gui/images/resources/pause_2'#get_path('pause')
    media_state: "pause"
    image: self.play if self.media_state == 'pause' else self.pause

<TrackEditor>:
    size_hint: .6,.4
    waveform: waveform
    cut_window: cut_window
    cue_point_window: cue_point_window
    start_time_label: start_time_label
    end_time_label: end_time_label
    album_cover: album_art
    artist_label: artist_label
    title_label:  title_label
    album_label:  album_label
    title: "PREVIEW"

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
            text: "TRACK EDITOR"
        BoxLayout:
            orientation: 'vertical'
            size_hint: 1,1
            padding: [15,10,15,7]

            BoxLayout:
                orientation: 'horizontal'
                size_hint: 1, None
                height: 85
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
                    orientation: 'horizontal'
                    size_hint: 1,1
                    size_hint_min_y: 100
                    BoxLayout:
                        orientation: 'vertical'
                        size_hint: 1,None
                        spacing: 10
                        height: 70
                        pos_hint: {'top': 1}
                        Label:
                            id: title_label
                            size_hint: 1,None
                            #shorten: True
                            text: "3 Little Monkeys"
                            text_size: self.size
                            font_size: 18
                            color: .2,.2,.2,1
                            height: 15
                            bold: True
                            halign: 'left'
                            valign: 'middle'
                            shorten: True
                            ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}

                        Label:
                            id: artist_label
                            size_hint: 1,None
                            height: 15
                            text: ""
                            #color: .7,.7,.7,1
                            color: .4,.4,.4,1
                            text_size: self.size
                            font_size: 15
                            halign: 'left'
                            valign: 'middle'
                            shorten: True
                            ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}

                        Label:
                            id: album_label
                            size_hint: 1,None
                            height: 15
                            text_size: self.size
                            text: ""
                            color: .4,.4,.4,1
                            halign: 'left'
                            valign: 'middle'
                            shorten: True
                            ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}
                            text: ""
                            font_size: 15
            Widget:
                size_hint: None, 1
            BoxLayout:
                orientation: 'vertical'
                spacing: 10
                size_hint: 1, None
                height: 200
                padding:[10,10,10,10]

                RelativeLayout:
                    size_hint: 1,1
                    WaveformSeekbar:
                        canvas.before:
                            Color:
                                rgba: 0,0,0,0
                            Rectangle:
                                pos:  0,0#self.pos[0] - root.pos[0], self.pos[1] - root.pos[1]
                                size: self.size

                        size_hint: 1, None
                        height: 100
                        pos:0,0
                        id: waveform

                    TrackCutWindow:
                        id: cut_window
                        size_hint: 1,None
                        height: 100
                        pos:0,0

                    TrackCuePointWindow:
                        id: cue_point_window
                        size_hint: 1,1

                RelativeLayout:
                    size_hint: 1, None
                    height: 15
                    Label:
                        id: start_time_label
                        color: .2,.2,.2,1
                        text: '0:00'
                        font_size: 13
                    Label:
                        id: end_time_label
                        color: .2,.2,.2,1
                        text: '0:00'
                        font_size: 13

            Widget:
                size_hint: None, 1
            BoxLayout:
                orientation: 'horizontal'
                size_hint: 1, None
                height: 40
                padding: [30,0,30,0]
                spacing: 10
                Button:
                    size_hint:1,1
                    text: "APPLY"
                    on_press: root.apply_changes()
                Button:
                    size_hint:1,1
                    text: "CANCEL"
                    on_press: root.dismiss()
"""


class TrackCutWindow(Widget):
    track_length = NumericProperty(0)
    track_start = NumericProperty(0, allownone=True)
    track_end = NumericProperty(0, allownone=True)

    def __init__(self, *args, **kwargs):
        super(TrackCutWindow, self).__init__(*args, **kwargs)
        self._redraw = Clock.create_trigger(self.draw_window)
        self.bind(track_length=self._redraw,
                  track_start=self._redraw,
                  track_end=self._redraw,
                  size=self._redraw,
                  pos=self._redraw)

        self.bind(on_touch_down=self._on_touch_down,
                  on_touch_up=self._on_touch_up,
                  on_touch_move=self._on_touch_move)
        self._move_func = None

    def _move_start_time(self, x, y):
        x_factor = float(self.width) / self.track_length if self.track_length is not 0 else 1
        if x < 10:
            x = 0
        foo = int(x / x_factor)
        if foo + 7000000000 <= self.track_end:
            self.track_start = foo if foo > 0 else 0
        pass

    def _move_end_time(self, x, y):
        x_factor = float(self.width) / self.track_length if self.track_length is not 0 else 1
        if x > self.width - 10:
            x = self.width
        foo = int(x / x_factor)
        if foo - 7000000000 >= self.track_start:
            self.track_end = foo if foo < self.track_length else self.track_length

    def _on_touch_down(self, window, event):
        x_factor = float(self.width) / self.track_length if self.track_length is not 0 else 1
        track_start = self.track_start if self.track_start is not None else 0
        track_end = self.track_end if self.track_end is not None else self.track_length

        if self.collide_point(*event.pos):
            x, y = event.pos
            if x < track_start * x_factor + 10 and x > track_start * x_factor - 10:
                if y < self.height / 2 + 10 and y > self.height / 2 - 10:
                    # if self._move_func is not None:
                    self._move_func = self._move_start_time  # print "MOVE START"
            if x < track_end * x_factor + 10 and x > track_end * x_factor - 10:
                if y < self.height / 2 + 10 and y > self.height / 2 - 10:
                    self._move_func = self._move_end_time  # print "MOVE END"

        pass

    def _on_touch_up(self, window, event):
        self._move_func = None
        pass

    def _on_touch_move(self, window, event):
        if self.collide_point(*event.pos):
            if self._move_func is not None:
                self._move_func(*event.pos)

    def draw_window(self, *args):
        self.canvas.clear()
        # zero_x = self.x
        x_factor = float(self.width) / self.track_length if self.track_length is not 0 else 1
        track_start = self.track_start if self.track_start is not None else 0
        track_end = self.track_end if self.track_end is not None else self.track_length

        with self.canvas:
            Color(.2, .2, .2, .8)
            Rectangle(size=(track_start * x_factor,
                            self.height),
                      pos=self.pos)
            window_end = (self.track_length - track_end) * x_factor
            Rectangle(size=(window_end, self.height),
                      pos=[self.pos[0] + self.width - window_end, self.pos[1]])
            Color(.3, .3, .3, 1)
            Line(rounded_rectangle=[track_start * x_factor, self.y,
                                    (track_end - track_start) * x_factor, self.height, 10],
                 width=2)

            Ellipse(size=[16, 16],
                    pos=[track_start * x_factor + self.x - 8, self.y + self.height / 2 - 8])
            Ellipse(size=[16, 16],
                    pos=[track_end * x_factor + self.x - 8, self.y + self.height / 2 - 8])


Factory.register('TrackCutWindow', TrackCutWindow)


class TrackCuePointWindow(Widget):
    track_length = NumericProperty(0)
    track_start = NumericProperty(0, allownone=True)
    track_end = NumericProperty(0, allownone=True)

    def __init__(self, *args, **kwargs):
        super(TrackCuePointWindow, self).__init__(*args, **kwargs)
        self._redraw = Clock.create_trigger(self.draw_window)
        self._update_label_positions = Clock.create_trigger(self.update_label_positions)
        self.bind(track_length=self._redraw,
                  size=self._redraw,
                  pos=self._redraw)

        self.bind(track_length=self._update_label_positions,
                  size=self._update_label_positions,
                  pos=self._update_label_positions)

        self.bind(on_touch_down=self._on_touch_down,
                  on_touch_up=self._on_touch_up,
                  on_touch_move=self._on_touch_move)
        self._move_func = None
        self._active_cue_point = None
        self._cue_points = []
        self._time_labels = []

    def _on_touch_down(self, window, event):
        pass

    def _on_touch_up(self, window, event):
        pass

    def _on_touch_move(self, window, event):
        pass

    def add_cue_point(self, timestamp):
        self._cue_points.append(timestamp)
        self._cue_points = sorted(self._cue_points)
        self.draw_window()

    def remove_cue_point(self, timestamp):
        try:
            if timestamp > 0 and timestamp < self.track_end:
                self._cue_points.remove(timestamp)
                self._active_cue_point = max(min(self._active_cue_point, len(self._cue_points)), 0)
                self.previous_cue_point()
        except ValueError:
            pass

    def clear_cue_points(self):
        self._cue_points = [0, self.track_end]  # sorted(self._cue_points)
        self._active_cue_point = None
        self.draw_window()

    def next_cue_point(self, timestamp=None):
        # if timestamp is not None:
        #    i = 0
        if self._active_cue_point == None:
            self._active_cue_point = 0
        else:
            self._active_cue_point += 1
            self._active_cue_point = max(min(self._active_cue_point, len(self._cue_points)), 0)

        self.draw_window()

    def previous_cue_point(self):
        if self._active_cue_point == None:
            self._active_cue_point = len(self._cue_points) - 1
        else:
            self._active_cue_point -= 1
            self._active_cue_point = max(min(self._active_cue_point, len(self._cue_points)), 0)
        self.draw_window()

    def get_cue_point_after(self, timestamp):
        #i = 0
        for cue in self._cue_points:
            if cue > timestamp:
                return cue
        else:
            return self._cue_points[-1]

    def get_cue_point_before(self, timestamp):
        #i = 0
        for j in range(len(self._cue_points)):
            if self._cue_points[j] >= timestamp:
                if j > 0:
                    return self._cue_points[j - 1]
                else:
                    return self._cue_points[j]

        else:
            return self._cue_points[0]

    def current_cue_point(self):
        if self._active_cue_point is not None:
            return self._cue_points[self._active_cue_point]

    def modify_current_cue_point(self, amount):
        if self._active_cue_point is not None:
            try:
                t = self._cue_points[self._active_cue_point]
            except IndexError:
                return
            t += amount
            if t > 0 and t < self.track_end:
                self._cue_points[self._active_cue_point] = t
                self._cue_points = sorted(self._cue_points)
                self.draw_window()

    def update_label_positions(self, *args):
        # self.canvas.clear()
        #zero_x = self.x
        #x_factor = float(self.width) / self.track_length if self.track_length is not 0 else 1
        #track_start = self.track_start if self.track_start is not None else 0
        #track_end   = self.track_end if self.track_end is not None else self.track_length
        # print 'REDRAW'
        # with self.canvas:
        seconds = int(round(self.track_length / 1000000000))
        y = self.height - 40
        if seconds == 0:
            seconds = 300
        tick_space = (float(self.width) / seconds) * 3
        # if tick_space * seconds > self.width:
        #    tick_space -= 1
        # elif tick_space * seconds < self.width:
        #    tick_space += 1

        #overshoot = self.width - tick_space * seconds / 3
        for l in self._time_labels:
            self.remove_widget(l)
        # print seconds, self.width, overshoot
        #x = 0
        for i in range(seconds / 3):
            x = round(i * tick_space)
            if i % 5 == 0:
                l = Label(text=seconds_to_human_readable(i * 3), color=[.2, .2, .2, 1])
                self.add_widget(l)
                self._time_labels.append(l)
                l.size_hint = (None, None)
                l.size = 20, 12
                l.font_size = 11
                l.center_x = self.x + x
                l.y = y + 17

    def draw_window(self, *args):
        self.canvas.before.clear()
        #zero_x = self.x
        x_factor = float(self.width) / self.track_length if self.track_length is not 0 else 1
        #track_start = self.track_start if self.track_start is not None else 0
        #track_end = self.track_end if self.track_end is not None else self.track_length
        # print 'REDRAW'
        with self.canvas.before:
            i = 0

            y = self.height - 40
            Color(.2, .2, .2, 1)
            Line(points=[self.x, y, self.width + self.x, y])

            seconds = int(round(self.track_length / 1000000000))

            if seconds == 0:
                seconds = 300
            tick_space = (float(self.width) / seconds) * 3
            # if tick_space * seconds > self.width:
            #    tick_space -= 1
            # elif tick_space * seconds < self.width:
            #    tick_space += 1

            #overshoot = self.width - tick_space * seconds / 3

            # print seconds, self.width, overshoot
            x = 0
            for i in range(seconds / 3):
                x = round(i * tick_space)
                if i % 5 == 0:
                    Line(points=[self.x + x,
                                 y,
                                 self.x + x,
                                 y + 15])
                else:
                    Line(points=[self.x + x,
                                 y,
                                 self.x + x,
                                 y + 10])

            i = 0
            for cue_point in self._cue_points:
                if i == self._active_cue_point:
                    Color(1, 0, 0, 1)
                else:
                    Color(1, 1, .1, 1)
                Line(points=[cue_point * x_factor, self.y,
                             cue_point * x_factor, self.y + self.height - 40],
                     width=1)
                Triangle(points=[cue_point * x_factor, self.y + self.height - 40,
                                 cue_point * x_factor - 5, self.y + self.height - 32,
                                 cue_point * x_factor + 5, self.y + self.height - 32])
                i += 1


Factory.register('TrackCuePointWindow', TrackCuePointWindow)


class TrackEditor(ModalView):
    seekbar = ObjectProperty(None)
    turntable = ObjectProperty(None)
    cut_window = ObjectProperty(None)
    tick_line = ObjectProperty(None)
    start_time_label = ObjectProperty(None)
    end_time_label = ObjectProperty(None)
    album_cover = ObjectProperty(None)
    track = ObjectProperty(None)
    title_label = ObjectProperty(None)
    artist_label = ObjectProperty(None)
    queue = ObjectProperty(None)
    #short_list     = ObjectProperty(None)
    waveform = ObjectProperty(None)
    volume = NumericProperty(1.0)
    volume_controls = ObjectProperty(None)  # NumericProperty(1.0)

    def __init__(self, player, volume_control=None, window=None, queue=None, short_list=None, *args, **kw):
        super(TrackEditor, self).__init__(*args, **kw)
        self._track = None
        self._waveform_generator = None
        self._wave_buffer = []
        self._player = pydjay.bootstrap.preview_player
        self.volume_controls = pydjay.bootstrap.volume_control
        self._save_monitor_volume = 1.0
        self._player.player.bind(on_end_of_stream=self._on_eos,
                                 track_duration=self._update,  # forward_track_duration,
                                 track_position=self._update  # forward_track_position
                                 )
        self.bind(on_dismiss=lambda *a: self.stop())
        self.bind(volume=self._set_volume)
        self._duration = None
        self.queue = queue
        #self.short_list = short_list
        Clock.schedule_once(self._post_init, -1)

    def _post_init(self, *a):
        self.cut_window.bind(track_length=self._update_track_labels,
                             track_start=self._update_track_labels,
                             track_end=self._update_track_labels,
                             size=self._update_track_labels,
                             pos=self._update_track_labels
                             )
        self.cut_window.bind(  # track_length = self._update_track_labels,
            track_start=self._update_track_labels,
            track_end=self._update_track_labels,
        )
        self._update_track_labels()

    def open(self):
        super(TrackEditor, self).open()
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self, 'text')
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def dismiss(self):
        Window.release_keyboard(self)
        super(TrackEditor, self).dismiss()

    def _keyboard_closed(self):
        #print('My keyboard have been closed!')
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        #print('The key', keycode, 'have been pressed')
        #print(' - text is %r' % text)
        #print(' - modifiers are %r' % modifiers)

        key_seq = "+".join(modifiers + [keycode[1]])
        # print key_seq

        if key_seq == 'left':  # activate previous cue point
            self.cue_point_window.previous_cue_point()
            pass
        elif key_seq == 'right':  # activate next cue point
            self.cue_point_window.next_cue_point()
            pass
        elif key_seq == 'shift+left':  # move start to previous cue point
            t = self.cue_point_window.get_cue_point_before(self.cut_window.track_start)
            self.cut_window.track_start = t

            # self.cut_window
            pass
        elif key_seq == 'shift+right':  # move start to next cue point
            t = self.cue_point_window.get_cue_point_after(self.cut_window.track_start)
            self.cut_window.track_start = t

            pass
        elif key_seq == 'shift+ctrl+left':  # move end to previous cue point
            t = self.cue_point_window.get_cue_point_before(self.cut_window.track_end)
            self.cut_window.track_end = t
            pass
        elif key_seq == 'shift+ctrl+right':  # move end to next cue point
            t = self.cue_point_window.get_cue_point_after(self.cut_window.track_end)
            self.cut_window.track_end = t

            pass
        elif key_seq == 'backspace':  # delete current cue point
            t = self.cue_point_window.current_cue_point()
            if t is not None:
                self.cue_point_window.remove_cue_point(t)

        elif key_seq == 'k':  # move cue point to the left
            self.cue_point_window.modify_current_cue_point(-100000000)
            pass
        elif key_seq == 'l':  # move cue point to the right
            self.cue_point_window.modify_current_cue_point(100000000)

        elif key_seq == 'shift+k':  # move cue point to the left
            self.cue_point_window.modify_current_cue_point(-10000000)
        elif key_seq == 'shift+l':  # move cue point to the right
            self.cue_point_window.modify_current_cue_point(10000000)
        elif key_seq == 'shift+ctrl+k':  # move cue point to the left
            self.cue_point_window.modify_current_cue_point(-1000000000)
        elif key_seq == 'shift+ctrl+l':  # move cue point to the right
            self.cue_point_window.modify_current_cue_point(1000000000)
        elif key_seq == 'c':  # add cue point
            position = self._player.track_position or 0
            if position > 0:
                self.cue_point_window.add_cue_point(position)
            pass
        elif key_seq == 'escape':
            self.dismiss()

        # elif key_seq == 'shift+s':
        #    #if self._current_selection is not None:
        #    self.short_list.add_shortlist_track(self._track)
        #    self.dismiss()
        #    #else:
        #    #    self.select(0)

        # elif key_seq == 'shift+q':
        #    #if self._current_selection is not None:
        #    self.queue.add_track(self._track)
        #    self.dismiss()

        elif key_seq == 'enter':  # start playback from current cue point
            t = self.cue_point_window.current_cue_point()
            self._player.play(self._track, t)
        else:
            pydjay.core.keyboard.key_map.key_pressed(keycode, modifiers)
        return True

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

    def apply_changes(self, *a):
        if self._track is not None:
            self._track.info.start_time = self.cut_window.track_start
            self._track.info.end_time = self.cut_window.track_end
        self.dismiss()

    # def _update_track_start(self, *a):
    #    if self._track is not None:
    #        self._track.info.start_time = self.cut_window.track_start
    #    self._update_track_labels()

    # def _update_track_end(self, *a):
    #    if self._track is not None:
    #        self._track.info.end_time = self.cut_window.track_end
    #    self._update_track_labels()

    def _on_eos(self, *a):
        self._duck_main_player = Animation(volume=self._save_monitor_volume,
                                           t='in_out_sine', duration=0.65)
        self._duck_main_player.start(self)

    def _set_volume(self, i, value):
        self.volume_controls.set_volume('main_player_monitor', self.volume)

    def _set_preview_volume(self, value):
        self.volume_controls.set_volume('preview_player', value)

    def play(self):
        self._player.play(self._track, self.cut_window.track_start, self.cut_window.track_end)

    def stop(self):
        self._player.stop()

    def _do_seek(self, window, event):
        if self.seekbar.collide_point(*event.pos):
            x_coord = event.pos[0] - self.seekbar.x
            factor = float(x_coord) / self.seekbar.width
            val = factor * self.seekbar.max
            self._player.seek(int(val))
            return False
        return True

    def set_track(self, track):
        self._player.stop()
        self._track = track
        self._duration = None
        if self._track is not None:
            self.artist_label.text = self._track.metadata.artist
            self.title_label.text = self._track.metadata.title
            self.album_label.text = self._track.metadata.album
            if self._track.metadata.album_cover is not None:
                try:
                    # self.album_cover.memory_data = self._track.metadata.album_cover
                    self.album_cover.source = self._track.metadata.album_cover['small']
                except:
                    self.album_cover.source = 'atlas://pydjay/gui/images/resources/default_album_cover'
            else:
                self.album_cover.source = 'atlas://pydjay/gui/images/resources/default_album_cover'

            if self._track.info.length is not None:
                self.waveform.max_value = self._track.info.stream_length
                self.waveform.waveform.x_max = self._track.info.stream_length
                self.cut_window.track_length = self.cue_point_window.track_length = self._track.info.stream_length
                self.cut_window.track_start = self.cue_point_window.track_start = self._track.info.start_time if self._track.info.start_time is not None else 0
                self.cut_window.track_end = self.cue_point_window.track_end = self._track.info.end_time if self._track.info.end_time is not None else self._track.info.stream_length
                self.cue_point_window.clear_cue_points()
            try:
                f = open(self._track.metadata.waveform, 'rb')
                arr = array.array('f')
                num_points = int(f.readline().split('\n')[0])
                arr.fromfile(f, num_points)
                ll = arr.tolist()
                offset = 0
                points = [ll[offset:offset + 2] for offset in range(0, len(ll) - 1, 2)]
                points = sorted(points, cmp=lambda x, y: cmp(x[0], y[0]))
                self.waveform.waveform.points = points  # self._track.metadata.waveform
            except EOFError:
                ll = arr.tolist()
                offset = 0
                points = [ll[offset:offset + 2] for offset in range(0, len(ll) - 1, 2)]
                points = sorted(points, cmp=lambda x, y: cmp(x[0], y[0]))
                self.waveform.waveform.points = points  # self._track.metadata.waveform
            except Exception, details:
                print details
                self.waveform.waveform.points = []
            finally:
                try:
                    f.close()
                except:
                    pass

    def _update(self, *a):
        if self._duration is None:
            self._duration = self._player.track_duration
            if self._duration is not None:
                self.waveform.max_value = self._duration
                self.waveform.waveform.x_max = self._duration
            else:
                self.waveform.max_value = 1
        position = self._player.track_position or 0
        duration = self._duration
        if duration is None:
            pass
        else:
            position = min(position, duration)
            self.waveform.value = position


Builder.load_string(kv_string)
Factory.register('TrackEditor', TrackEditor)
