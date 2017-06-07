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
from elements import waveform_seekbar#screen, paged_grid, paged_display
from elements.utils import seconds_to_human_readable
from kivy.animation import Animation
import pydjay.bootstrap
import pydjay.ui.track_short_list_modal


kv_string = """
<DialogBase>:
    size_hint: .4,.95
    short_list: short_list

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
        TrackShortListModal:
            #orientation: 'vertical'
            size_hint: 1, 1
            id: short_list
            window:root
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
                text: "Remove unavailable Tracks"
                on_press: root.remove_unavailable_tracks()
"""

class DialogBase(ModalView):
    short_list     = ObjectProperty(None)
    sl_track_count = ObjectProperty(None)

    def __init__(self, *args, **kw):
        super(DialogBase, self).__init__(*args, **kw)
        Clock.schedule_once(self._post_init, -1)

    def _post_init(self, *a):
        pass

    def open(self):
        super(DialogBase, self).open()

    def dismiss(self):
        super(PlaylistChooser, self).dismiss()

Builder.load_string(kv_string)
Factory.register('DialogBase', DialogBase)
