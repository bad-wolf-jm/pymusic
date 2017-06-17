import os
import re
import mimetypes

from functools import partial
from threading import Thread
from os.path import getsize
from datetime import datetime

from kivy.event import EventDispatcher
from kivy.clock import mainthread, Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.selectableview import SelectableView
from kivy.uix.treeview import TreeViewNode
from kivy.uix.label import Label
from kivy.adapters.simplelistadapter import SimpleListAdapter
from kivy.adapters.listadapter import ListAdapter


#from kivy.properties import ObjectProperty
from kivy.factory import Factory

#from pydjay.gui.utils import seconds_to_human_readable
#from pydjay.uix.clickable_area import ImageButton
from pydjay.ui.behaviors.long_press_button import LongPressButtonBehaviour

from kivy.graphics import *

#from pydjay.gui.main_window import MainWindow
from drag_item import DragItem

from utils import seconds_to_human_readable


kv_string_item = """
<DefaultTrackItemView>:
    #album_art: album_art
    #album_art_file:'atlas://pydjay/gui/images/resources/transparent_image'
    bg: bg
    size_hint: 1, None
    height:35
    bold: False
    color: 1,1,1,1

    on_touch_down: self._on_touch_down(*args)

    #on_pos:  self.update_bg()
    #on_size: self.update_bg()

    Widget:
        id: bg
        size_hint: 1,1
        on_pos:  root._update_background()
        on_size: root._update_background()#self.pos, self.size)

    BoxLayout:
        orientation: 'horizontal'
        size_hint: 1, None
        #size_hint: 1,1 
        padding:[10,1,10,1]
        spacing: 10
        height:35
        Label:
            id: index
            bold: root.bold
            color: root.color
            font_size:15
            text: root.idx
            text_size: self.size
            halign: 'left'
            valign: 'middle'
            size_hint: None, 1
            width: 30
            shorten: True
            ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}
            #opacity: 0.2 if root.dimmed else 1

        Label:
            id: title
            bold: root.bold
            color: root.color
            font_size:15
            text: root.tr_title
            text_size: self.size
            halign: 'left'
            valign: 'middle'
            size_hint: 1, 1
            shorten: True
            ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}
            #opacity: 0.2 if root.dimmed else 1
        Label:
            id: length
            bold: root.bold
            color: root.color
            font_size:15
            text: root.length
            text_size: self.size
            halign: 'right'
            valign: 'middle'
            size_hint: None, 1
            width: 75
            shorten: True
            ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}
            #opacity: 0.2 if root.dimmed else 1
"""


class DefaultTrackItemView(RelativeLayout):
    idx = StringProperty("")
    album_art_file = ObjectProperty(None)
    favorite = BooleanProperty(False)
    has_waveform = BooleanProperty(False)
    tr_title = StringProperty("")
    artist = StringProperty("")
    album = StringProperty("")
    bpm = StringProperty("")
    length = StringProperty("")
    bg = ObjectProperty(None)
    dimmed = BooleanProperty(True)

    def __init__(self, row=None, item=None, view=None, window=None, *args, **kwargs):
        super(DefaultTrackItemView, self).__init__(*args, **kwargs)
        self.row = row
        self._album_art = None
        self._item_data = item
        self._view = view
        self._item = self._item_data.track if self._item_data is not None else None
        self._window = window
        self._long_press_threshold = .25
        self.bind(on_long_press=self._start_dragging)

        if self._item_data is not None:
            self._update_background()
            self._update_availability()
            self._item_data.bind(is_selected=self._update_background,
                                 is_available=self._update_background)

        if self._item is not None:
            self.idx = str(self.row + 1) + '.'
            self.tr_title = "%s - %s" % (unicode(self._item.metadata.title),
                                         unicode(self._item.metadata.artist))
            self.length = seconds_to_human_readable(int(self._item.info.length / 1000000000))
        else:
            self.title = ""
            self.artist = ""
            self.album = ""
            self.bpm = ""
            self.length = ""

    def _update_availability(self, *args):  # win, value):
        pass

    def _update_background(self, *value):
        value = self._item_data.is_selected if self._item_data is not None else False
        self.bold = value
        self.bg.canvas.clear()
        if value:
            with self.bg.canvas:
                Color(0, .3, .7, 1)
                Rectangle(size=self.bg.size, pos=self.bg.pos)
        else:
            with self.bg.canvas:
                if self.row is not None:
                    with self.bg.canvas:
                        if self.row % 2 == 0:
                            Color(0, 0, 0, 0.8)
                        else:
                            Color(.1, .1, .1, .8)
                        Rectangle(pos=self.bg.pos, size=self.bg.size)

        if self._item_data is not None and not self._item_data.is_available:
            self.dimmed = True  # opacity = 0.1
        else:
            self.dimmed = False
        self.update_album_art(33, 33)

    def _start_dragging(self, foo, x, y):
        if self._window is not None:
            try:
                self._window.start_drag(self.to_window(x, y), self._item)
            except Exception, details:
                print details

    def update_bg(self, *args):
        if self.row is not None:
            self.bg.canvas.clear()
            with self.bg.canvas:
                if self.row % 2 == 0:
                    Color(0, 0, 0, 0.8)
                else:
                    Color(.1, .1, .1, .8)
                Rectangle(pos=self.bg.pos, size=self.bg.size)

    def update_album_art(self, w, h):
        if self._album_art is not None:
            self.album_art.texture = self._album_art.texture

    def _on_touch_down(self, window, event):
        pass


Builder.load_string(kv_string_item)
Factory.register('DefaultTrackItemView', DefaultTrackItemView)
