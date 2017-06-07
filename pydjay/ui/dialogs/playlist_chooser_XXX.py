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
#from elements import waveform_seekbar#screen, paged_grid, paged_display
#from elements.utils import seconds_to_human_readable
from kivy.animation import Animation
import pydjay.bootstrap
import pydjay.ui.dialogs.track_list



kv_string = """
#:import PlaylistList pydjay.ui.dialogs.playlist_list.PlaylistList
<PlaylistChooser>:
    size_hint: .3,.6
    short_list: short_list
    #sl_track_count:sl_track_count

    canvas:
        Color:
            rgba: 0.7,0.7,0.7,.98
        Rectangle:
            size: self.size
            pos: self.pos

    BoxLayout:
        orientation: 'vertical'

        BoxLayout:
            orientation: 'horizontal'
            size_hint: 1, None
            height: 65
            padding: [10,0,10,0]
            canvas.before:
                Color:
                    rgba: 0.3,0.3,0.3,.98
                Rectangle:
                    size: self.size
                    pos: self.pos
            Label:
                size_hint: 1,1
                height: 25
                font_size: 25
                markup: True
                halign: 'center'
                valign: 'middle'
                text_size: self.size
                text: "PLAYLISTS"

        ModalHDivider:
        PlaylistList:
            #orientation: 'vertical'
            size_hint: 1, 1
            id: short_list
            window:root
            #item_class: PlaylistItem
            #queue: master_queue
            #preview_player: preview_player
            #main_player: deck

        BoxLayout:
            orientation: 'vertical'
            size_hint: 1, None
            height: 75
            spacing: 20
            padding: [20,15,20,7]
            Button:
                size_hint: 0.75, 1
                pos_hint: {'center_x':.5}
                text: "Create new playlist"
                on_press: root.remove_unavailable_tracks()
"""

class PlaylistChooser(ModalView):
    short_list     = ObjectProperty(None)
    #sl_track_count = ObjectProperty(None)

    def __init__(self, *args, **kw):
        super(PlaylistChooser, self).__init__(*args, **kw)
        self.bind(on_dismiss = lambda *a: pydjay.bootstrap.preview_player.stop())
        self._drag_payload = None
        Clock.schedule_once(self._post_init, -1)

    def _post_init(self, *a):
        #self.short_list.short_list.adapter.bind(data = self._update_sl_track_count)
        pass

    def open(self):
        super(PlaylistChooser, self).open()
        self.short_list.set_track_list(pydjay.bootstrap.get_all_playlists())
        #self.short_list.set_track_list(pydjay.bootstrap.get_short_list(), sort = False)
        #self._update_sl_track_count()
        self.short_list.focus()

    def dismiss(self):
        #pydjay.bootstrap.set_short_list(self.short_list.short_list.get_full_track_list())
        super(PlaylistChooser, self).dismiss()

    #def do_filter(self, window, text):
    #    self.short_list.short_list.do_filter(text)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down = self._on_keyboard_down)
        self._keyboard = None

    #def _update_sl_track_count(self, *args):
    #    num = len(self.short_list.short_list.adapter.data)
    #    time = 0

#        for t in self.short_list.short_list.adapter.data:
#            try:
#                time += t['item'].track.info.length
#            except:
#                pass
#        track_count_text = "[color=#ffffff]" + str(num) + " tracks " + "[/color]" + \
#                            "[color=#999999] | [/color]"+ \
#                            "[color=#cccccc]" + seconds_to_human_readable(time / 1000000000) + "[/color]"
#        #self.sl_track_count.text = track_count_text

    def request_focus(self, *a):
        pass

    #def remove_unavailable_tracks(self, *a):
    #    foo = RemoveUnavailableDialog(self)
    #    foo.open()

    #def do_remove_unavailable_tracks(self):
    #    tracks = [x for x in pydjay.bootstrap.get_short_list() if pydjay.bootstrap.track_is_available(x)]
    #    pydjay.bootstrap.set_short_list(tracks)
    #    self.short_list.set_track_list(pydjay.bootstrap.get_short_list(), sort = False)
    #    self._update_sl_track_count()
    #    self.short_list.focus()


Builder.load_string(kv_string)
Factory.register('PlaylistChooser', PlaylistChooser)
