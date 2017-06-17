# import os
# import re
# import mimetypes
# import array
# from functools import partial
# from threading import Thread
# from os.path import getsize
# from datetime import datetime
# from kivy.core.window import Window
# from kivy.graphics import Color, Line, RoundedRectangle, Ellipse
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty
# from kivy.uix.boxlayout import BoxLayout
# from kivy.uix.relativelayout import RelativeLayout
# from kivy.uix.widget import Widget
# from kivy.uix.label import Label
# from kivy.properties import ObjectProperty, NumericProperty
from kivy.factory import Factory
# from kivy.uix.popup import Popup
from kivy.uix.modalview import ModalView
# from elements import waveform_seekbar#screen, paged_grid, paged_display
# from elements.utils import seconds_to_human_readable
# from kivy.animation import Animation
import pydjay.bootstrap
import pydjay.ui.track_short_list_modal


kv_string = """
<DialogBase>:
    size_hint: None, None
    prompt: "Please enter some text:"
    text_input: text_input
    canvas:
        Color:
            rgba: 0.7,0.7,0.7,.98
        Rectangle:
            size: self.size
            pos: self.pos

    BoxLayout:
        orientation: 'vertical'
        Label:
            size_hint: 1,1
            height: 25
            font_size: 25
            markup: True
            halign: 'left'
            valign: 'middle'
            text_size: self.size
            text: root.prompt

    BoxLayout:
        orientation: 'horizontal'
        TextInput:
            id:text_input
            size_hint: 1,1
            multiline: False
            text_size: self.width - 30, self.height
            hint_text: root.filter_text
            foreground_color: root.foreground_color
            background_color: root.background_color
            on_text: root.do_filter(*args)
            on_text_validate: root.do_filter(*args)

        ImageButton:
            size_hint: None, None
            #pos_hint: {'center_y': .5}
            size: 30,30
            image:'atlas://pydjay/gui/images/resources/clear-filter'
            on_press: search_filter.text = ''
"""


class InputDialog(ModalView):
    short_list = ObjectProperty(None)
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
