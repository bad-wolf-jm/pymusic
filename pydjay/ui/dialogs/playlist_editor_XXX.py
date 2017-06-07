import os
import re
import mimetypes
import array

from functools import partial
from threading import Thread
from os.path import getsize
from datetime import datetime

from kivy.core.window import Window
from kivy.graphics import Mesh, Color, Rectangle, Line, RoundedRectangle, Ellipse, Triangle
from kivy.clock import mainthread, Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label

from kivy.properties import ObjectProperty, NumericProperty
from kivy.factory import Factory

from kivy.uix.popup import Popup
from kivy.uix.modalview import ModalView

#from pydjay.audio.wavegen import WaveformGenerator
#from pydjay.audio.gst import AudioDecoder

#from pydjay.audio.player.player import AudioPlayer

#from elements import waveform_seekbar#screen, paged_grid, paged_display
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
<PlaylistEditor>:
    size_hint: .9,.9
    #seekbar: seekbar
    #waveform: waveform
    #cut_window: cut_window
    #tick_line: tick_line
    #cue_point_window: cue_point_window
    #start_time_label: start_time_label
    #end_time_label: end_time_label
    #turntable:turntable
    #album_cover: album_art
    #artist_label: artist_label
    #title_label:  title_label
    #album_label:  album_label
    #length_label:  length_label
    #position_label:  position_label
    #title: "PREVIEW"
    #time_remaining_label: time_remaining
    #orientation: 'horizontal'
    #size_hint: 1, 1
    #height:75

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
            text: "PLAYLIST EDITOR"

        BoxLayout:
            orientation: 'horizontal'
            size_hint: 1,1
            MainTrackList:
                id: master_list
                window: root
                #queue: master_queue
                short_list: short_list
                #main_player: deck
                preview_player: preview_player
                size_hint: (1.0, 1.0)
                #text: "Browser goes here"
            VDivider:
            #BoxLayout:
            #    orientation: 'vertical'
            #    size_hint: 1, 1
            #    #height: 125 #time_label.height+date_label.height

            #    HDivider:
            #    BoxLayout:
            #        orientation: 'horizontal'
            #        size_hint: 1,1
            #        #VDivider:
            #        BoxLayout:
            #            orientation: 'vertical'
            #            size_hint: 1,1
            BoxLayout:
                orientation: 'vertical'
                size_hint: 1,1
                TrackShortList:
                    #orientation: 'vertical'
                    size_hint: 1, 1
                    id: short_list
                    window:root
                    #queue: master_queue
                    preview_player: preview_player
                    #main_player: deck


                PreviewPlayer:
                    id: preview_player
                    size_hint: 1, None

                    height: 125
"""

class PlaylistEditor(ModalView):
    seekbar        = ObjectProperty(None)
    turntable      = ObjectProperty(None)
    cut_window     = ObjectProperty(None)
    tick_line      = ObjectProperty(None)
    start_time_label = ObjectProperty(None)
    end_time_label   = ObjectProperty(None)
    album_cover    = ObjectProperty(None)
    track          = ObjectProperty(None)
    title_label    = ObjectProperty(None)
    artist_label   = ObjectProperty(None)
    queue          = ObjectProperty(None)
    short_list     = ObjectProperty(None)
    waveform       = ObjectProperty(None)
    volume         = NumericProperty(1.0)
    volume_controls = ObjectProperty(None)#NumericProperty(1.0)




    def __init__(self, *args, **kw):
        super(PlaylistEditor, self).__init__(*args, **kw)
        self._track              = None
        self._waveform_generator = None
        self._wave_buffer        = []
        self._player             = pydjay.bootstrap.preview_player
        self._preview_player = self._player
        self._volume_control     = pydjay.bootstrap.volume_control
        self._save_monitor_volume = 1.0
        self._player.player.bind(on_end_of_stream = self._on_eos,
                                 track_duration   = self._update, #forward_track_duration,
                                 track_position   = self._update #forward_track_position
                      )
        self.bind(on_dismiss = lambda *a: self.stop())
        self.bind(volume = self._set_volume)
        self._duration = None
        #self.queue = queue
        #self.short_list = short_list
        Clock.schedule_once(self._post_init, -1)

    def _post_init(self, *a):
        pass

    def open(self):
        super(PlaylistEditor, self).open()
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self, 'text')
        self._keyboard.bind(on_key_down = self._on_keyboard_down)

    def dismiss(self):
        Window.release_keyboard(self)
        super(PlaylistEditor, self).dismiss()


    def _keyboard_closed(self):
        print('My keyboard have been closed!')
        self._keyboard.unbind(on_key_down = self._on_keyboard_down)
        self._keyboard = None


    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        #print('The key', keycode, 'have been pressed')
        #print(' - text is %r' % text)
        #print(' - modifiers are %r' % modifiers)

        key_seq = "+".join(modifiers+[keycode[1]])
        #print key_seq

        if key_seq == 'left': #activate previous cue point
            self.cue_point_window.previous_cue_point()
            pass
        elif key_seq == 'right': #activate next cue point
            self.cue_point_window.next_cue_point()
            pass
        elif key_seq == 'shift+left': #move start to previous cue point
            t = self.cue_point_window.get_cue_point_before(self.cut_window.track_start)
            self.cut_window.track_start = t

            #self.cut_window
            pass
        elif key_seq == 'shift+right': #move start to next cue point
            t = self.cue_point_window.get_cue_point_after(self.cut_window.track_start)
            self.cut_window.track_start = t

            pass
        elif key_seq == 'shift+ctrl+left': #move end to previous cue point
            t = self.cue_point_window.get_cue_point_before(self.cut_window.track_end)
            self.cut_window.track_end = t
            pass
        elif key_seq == 'shift+ctrl+right': #move end to next cue point
            t = self.cue_point_window.get_cue_point_after(self.cut_window.track_end)
            self.cut_window.track_end = t

            pass
        elif key_seq == 'backspace': #delete current cue point
            t = self.cue_point_window.current_cue_point()
            if t is not None:
                self.cue_point_window.remove_cue_point(t)

        elif key_seq == 'k': #move cue point to the left
            self.cue_point_window.modify_current_cue_point(-100000000)
            pass
        elif key_seq == 'l': #move cue point to the right
            self.cue_point_window.modify_current_cue_point(100000000)

        elif key_seq == 'shift+k': #move cue point to the left
            self.cue_point_window.modify_current_cue_point(-10000000)
        elif key_seq == 'shift+l': #move cue point to the right
            self.cue_point_window.modify_current_cue_point(10000000)
        elif key_seq == 'shift+ctrl+k': #move cue point to the left
            self.cue_point_window.modify_current_cue_point(-1000000000)
        elif key_seq == 'shift+ctrl+l': #move cue point to the right
            self.cue_point_window.modify_current_cue_point(1000000000)
        elif key_seq == 'c': #add cue point
            position = self._player.track_position or 0
            if position > 0:
                self.cue_point_window.add_cue_point(position)
            pass
        elif key_seq == 'escape':
            self.dismiss()

        elif key_seq == 'shift+s':
            #if self._current_selection is not None:
            self.short_list.add_shortlist_track(self._track)
            self.dismiss()
            #else:
            #    self.select(0)

        elif key_seq == 'shift+q':
            #if self._current_selection is not None:
            self.queue.add_track(self._track)
            self.dismiss()


        elif key_seq == 'enter': # start playback from current cue point
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
            x_factor    = float(self.cut_window.width) / self.cut_window.track_length if self.cut_window.track_length is not 0 else 1
            self.start_time_label.center_x = self.cut_window.track_start * x_factor if self.cut_window.track_start is not None else 0
            self.end_time_label.center_x   = self.cut_window.track_end * x_factor if self.cut_window.track_end is not None else self.width
        else:
            self.start_time_label.opacity = 0
            self.end_time_label.opacity = 0


    def apply_changes(self, *a):
        if self._track is not None:
            self._track.info.start_time = self.cut_window.track_start
            self._track.info.end_time = self.cut_window.track_end
        self.dismiss()


    #def _update_track_start(self, *a):
    #    if self._track is not None:
    #        self._track.info.start_time = self.cut_window.track_start
    #    self._update_track_labels()


    #def _update_track_end(self, *a):
    #    if self._track is not None:
    #        self._track.info.end_time = self.cut_window.track_end
    #    self._update_track_labels()

    def _on_eos(self, *a):
        self._duck_main_player = Animation(volume = self._save_monitor_volume,
                                           t = 'in_out_sine', duration = 0.65)
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
            self.title_label.text  = self._track.metadata.title
            self.album_label.text  = self._track.metadata.album
            if self._track.metadata.album_cover is not None:
                try:
                    self.album_cover.source = self._track.metadata.album_cover['small']#self.album_cover.memory_data = self._track.metadata.album_cover
                except:
                    self.album_cover.source = 'atlas://pydjay/gui/images/resources/default_album_cover'
            else:
                self.album_cover.source = 'atlas://pydjay/gui/images/resources/default_album_cover'


            if self._track.info.length is not None:
                self.waveform.max_value      = self._track.info.stream_length
                self.waveform.waveform.x_max = self._track.info.stream_length
                self.cut_window.track_length = self.cue_point_window.track_length = self._track.info.stream_length
                self.cut_window.track_start  = self.cue_point_window.track_start = self._track.info.start_time if self._track.info.start_time is not None else 0
                self.cut_window.track_end    = self.cue_point_window.track_end = self._track.info.end_time if self._track.info.end_time is not None else self._track.info.stream_length
                self.cue_point_window.clear_cue_points()
            try:
                f = open(self._track.metadata.waveform, 'rb')
                arr = array.array('f')
                num_points = int(f.readline().split('\n')[0])
                arr.fromfile(f, num_points)
                ll = arr.tolist()
                offset = 0
                points = [ll[offset:offset+2] for offset in range(0, len(ll) - 1, 2)]
                points = sorted(points, cmp = lambda x,y: cmp(x[0], y[0]))
                self.waveform.waveform.points =  points#self._track.metadata.waveform
            except EOFError:
                ll = arr.tolist()
                offset = 0
                points = [ll[offset:offset+2] for offset in range(0, len(ll) - 1, 2)]
                points = sorted(points, cmp = lambda x,y: cmp(x[0], y[0]))
                self.waveform.waveform.points =  points#self._track.metadata.waveform
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
                self.waveform.max_value      = self._duration
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
Factory.register('PlaylistEditor', PlaylistEditor)
