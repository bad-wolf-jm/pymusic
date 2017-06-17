# import os
# import re
# import mimetypes
# import array
# from functools import partial
# from threading import Thread
# from os.path import getsize
# from datetime import datetime
# from kivy.core.window import Window
# from kivy.graphics import Mesh, Color, Rectangle, Line, RoundedRectangle, Ellipse, Triangle
from kivy.clock import Clock
from kivy.lang import Builder
# from kivy.properties import ObjectProperty
# from kivy.uix.boxlayout import BoxLayout
# from kivy.uix.relativelayout import RelativeLayout
# from kivy.uix.widget import Widget
# from kivy.uix.label import Label
from kivy.properties import ObjectProperty, StringProperty
from kivy.factory import Factory
# from kivy.uix.popup import Popup
from kivy.uix.modalview import ModalView
# from elements import waveform_seekbar#screen, paged_grid, paged_display
# from elements.utils import seconds_to_human_readable
# from kivy.animation import Animation
import pydjay.bootstrap
# import pydjay.ui.track_short_list_modal
import pydjay.ui.dialogs.track_list


kv_string = """
#:import PlaylistList pydjay.ui.dialogs.playlist_list.PlaylistList
<PlaylistSelector>:
    size_hint: .3,.6
    short_list: short_list
    title: ""
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
                text: root.title

        ModalHDivider:
        PlaylistList:
            size_hint: 1, 1
            id: short_list
            window:root
        ModalHDivider:
        Label:
            canvas.before:
                Color:
                    rgba: 0.5,0.5,0.5,.98
                Rectangle:
                    size: self.size
                    pos: self.pos
            size_hint: 1, None
            height:30
            font_size:15
            text:root.item_count
            valign:"middle"
            halign:'center'
            color: .2,.2,.2,1
"""

class PlaylistSelector(ModalView):
    short_list = ObjectProperty(None)
    item_count = StringProperty("")

    def __init__(self, *args, **kw):
        """Doc."""
        super(PlaylistSelector, self).__init__(*args, **kw)
        self._drag_payload = None
        self.register_event_type('on_playlist_selected')
        Clock.schedule_once(self._post_init, -1)

    def _post_init(self, *a):
        pass

    def on_playlist_selected(self, *a):
        """Doc."""
        pass

    def open(self, title, pl_list):
        """Doc."""
        super(PlaylistSelector, self).open()
        self.title = title
        self.short_list.set_track_list(pl_list, sort=False)
        N = len(pl_list)
        if N == 1:
            self.item_count = "1 item"
        else:
            self.item_count = "%s items"%N
        self.short_list.set_keyboard_handlers({'enter': self._select_playlist})
        self.short_list.focus()

    def dismiss(self):
        """Doc."""
        super(PlaylistSelector, self).dismiss()

    def _select_playlist(self):
        """Doc."""
        # print self.short_list.current_selection
        self.dispatch('on_playlist_selected', self.short_list.current_selection['item'].track)
        self.dismiss()

    # def do_filter(self, window, text):
    #    self.short_list.short_list.do_filter(text)

    def _keyboard_closed(self):
        """Doc."""
        self._keyboard.unbind(on_key_down = self._on_keyboard_down)
        self._keyboard = None

    def request_focus(self, *a):
        """Doc."""
        pass

    # def remove_unavailable_tracks(self, *a):
    #    foo = RemoveUnavailableDialog(self)
    #    foo.open()
    #
    #    def do_remove_unavailable_tracks(self):
    #        tracks = [x for x in pydjay.bootstrap.get_short_list() if pydjay.bootstrap.track_is_available(x)]
    #        pydjay.bootstrap.set_short_list(tracks)
    #        self.short_list.focus()


Builder.load_string(kv_string)
Factory.register('PlaylistSelector', PlaylistSelector)
