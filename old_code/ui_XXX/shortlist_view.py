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
from elements import waveform_seekbar  # screen, paged_grid, paged_display
from elements.utils import seconds_to_human_readable
from kivy.animation import Animation
import pydjay.bootstrap
import pydjay.ui.track_short_list_modal


kv_remove_unavailable_string = """
<RemoveUnavailableDialog>:
    size_hint: .35,.25

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
                text: "REMOVE UNAVAILABLE TRACKS?"

        BoxLayout:
            orientation: 'horizontal'
            size_hint: 1, 1
            height: 65
            padding: [30,0,30,0]
            spacing: 20

            Image:
                size_hint: None, None
                size: 75,75
                pos_hint:{'center_y':.5}
                source: 'atlas://pydjay/gui/images/resources/icon-warning'

            Label:
                size_hint: 1,1
                height: 25
                font_size: 18
                markup: True
                color: .3,.3,.3,1
                halign: 'justify'
                valign: 'middle'
                text_size: self.size
                multiline: True
                text: "Press 'YES' to remove all tracks in the short list that are currently marked as played."

        BoxLayout:
            orientation: 'horizontal'
            size_hint: 1, None
            height: 75
            spacing: 20
            padding: [20,15,20,7]
            Button:
                size_hint: 0.75, 1
                pos_hint: {'center_x':.5}
                text: "YES"
                on_press: root.remove_unavailable_tracks()
            Button:
                size_hint: 0.75, 1
                pos_hint: {'center_x':.5}
                text: "NO"
                on_press: root.dismiss()


"""


class RemoveUnavailableDialog(ModalView):
    short_list = ObjectProperty(None)
    sl_track_count = ObjectProperty(None)

    def __init__(self, parent, *args, **kw):
        super(RemoveUnavailableDialog, self).__init__(*args, **kw)
        self._parent = parent

    def remove_unavailable_tracks(self):
        self._parent.do_remove_unavailable_tracks()
        self.dismiss()


Builder.load_string(kv_remove_unavailable_string)
Factory.register('RemoveUnavailableDialog', RemoveUnavailableDialog)


kv_string = """
<ShortListView>:
    size_hint: .4,.95
    short_list: short_list
    sl_track_count:sl_track_count

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

            BoxLayout:
                orientation: 'vertical'
                spacing:2
                Label:
                    size_hint: 1,None
                    height: 25
                    font_size: 25
                    markup: True
                    halign: 'left'
                    valign: 'middle'
                    text_size: self.size
                    text: "SHORT LIST"

                Label:
                    id: sl_track_count
                    size_hint: 1, None
                    height: 20
                    markup:True
                    text: ""
                    #bold: True
                    halign: 'left'
                    valign: "top"
                    text_size: self.size
                    font_size: 17
                    #size_hint: None, None
                    #size: self.texture_size
                    height:30#

            BoxLayout:
                orientation: 'horizontal'
                size_hint: 1, None
                pos_hint: {'center_y': .5}
                height: 30
                spacing: 0
                canvas.before:
                    Color:
                        rgba: .2,.2,.2,1
                    Rectangle:
                        pos:self.pos
                        size: self.size

                TextInput:
                    id:search_filter
                    size_hint: 1,1
                    multiline: False
                    text_size: self.width - 30, self.height
                    hint_text: "Filter list..."
                    foreground_color: 1,1,1,.8
                    background_color: 0,0,0,0
                    on_text: root.do_filter(*args)

                ImageButton:
                    size_hint: None, None
                    #pos_hint: {'center_y': .5}
                    size: 30,30
                    image:'atlas://pydjay/gui/images/resources/clear-filter'
                    on_press: search_filter.text = ''
        ModalHDivider:
        PreviewPlayer:
            id: preview_player
            size_hint: 1, None
            height: 85
            title_color: .1,.1,.1,1
            artist_color: .3,.3,.3,1
            time_color: .2,.2,.2,1

        ModalHDivider:
        TrackShortListModal:
            #orientation: 'vertical'
            size_hint: 1, 1
            id: short_list
            window:root
            #queue: master_queue
            preview_player: preview_player
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
                text: "Remove unavailable Tracks"
                on_press: root.remove_unavailable_tracks()
"""


class ShortListView(ModalView):
    short_list = ObjectProperty(None)
    sl_track_count = ObjectProperty(None)

    def __init__(self, *args, **kw):
        super(ShortListView, self).__init__(*args, **kw)
        self.bind(on_dismiss=lambda *a: pydjay.bootstrap.preview_player.stop())
        self._drag_payload = None
        Clock.schedule_once(self._post_init, -1)

    def _post_init(self, *a):
        self.short_list.short_list.adapter.bind(data=self._update_sl_track_count)
        pass

    def open(self):
        super(ShortListView, self).open()
        self.short_list.set_track_list(pydjay.bootstrap.get_short_list(), sort=False)
        self._update_sl_track_count()
        self.short_list.focus()

    def dismiss(self):
        pydjay.bootstrap.set_short_list(self.short_list.short_list.get_full_track_list())
        super(ShortListView, self).dismiss()

    def do_filter(self, window, text):
        self.short_list.short_list.do_filter(text)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _update_sl_track_count(self, *args):
        num = len(self.short_list.short_list.adapter.data)
        time = 0

        for t in self.short_list.short_list.adapter.data:
            try:
                time += t['item'].track.info.length
            except:
                pass
        track_count_text = "[color=#ffffff]" + str(num) + " tracks " + "[/color]" + \
            "[color=#999999] | [/color]" + \
            "[color=#cccccc]" + \
            seconds_to_human_readable(time / 1000000000) + "[/color]"
        self.sl_track_count.text = track_count_text

    def request_focus(self, *a):
        pass

    def remove_unavailable_tracks(self, *a):
        foo = RemoveUnavailableDialog(self)
        foo.open()

    def do_remove_unavailable_tracks(self):
        tracks = [x for x in pydjay.bootstrap.get_short_list(
        ) if pydjay.bootstrap.track_is_available(x)]
        pydjay.bootstrap.set_short_list(tracks)
        self.short_list.set_track_list(pydjay.bootstrap.get_short_list(), sort=False)
        self._update_sl_track_count()
        self.short_list.focus()


Builder.load_string(kv_string)
Factory.register('ShortListView', ShortListView)
