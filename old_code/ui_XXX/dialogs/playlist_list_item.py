import os
#import io
#import re
#import mimetypes

from functools import partial
from threading import Thread
from os.path import getsize
from datetime import datetime

from kivy.clock import mainthread, Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.selectableview import SelectableView
from kivy.uix.button import Button
from kivy.uix.treeview import TreeViewNode


from kivy.properties import ObjectProperty
from kivy.factory import Factory

#from utils import seconds_to_human_readable
from pydjay.ui.elements.clickable_area import ImageButton
from pydjay.ui.behaviors.long_press_button import LongPressButtonBehaviour

from kivy.graphics import *

from list_item_base import ModalListItemBase

kv_string_item = """
<PlaylistItem>:
    album_art: album_art
    album_art_file:'atlas://pydjay/gui/images/resources/transparent_image'
    bg: bg
    size_hint: 1, None
    height:60
    bold: False
    color: .2,.2,.2,1
    n_color: .3,.3,.3,1
    on_touch_down: self._on_touch_down(*args)

    Widget:
        id: bg
        size_hint: 1,1
        on_pos:  root._update_background()
        on_size: root._update_background()#self.pos, self.size)

    BoxLayout:
        orientation: 'horizontal'
        size_hint: 1, 1
        #size_hint: 1,1
        padding:[10,3,15,3]
        spacing: 10

        RelativeLayout:
            size_hint: None, 1
            width: self.height

            ImageButton:
                id: album_art
                size_hint: (None, .6)
                pos_hint: {'center_x':.5, 'center_y':.5}
                width: self.height
                keep_ratio: True
                allow_stretch: True
                image: 'atlas://pydjay/gui/images/resources/precue'
                opacity: 0.2 if root.dimmed else 1
                on_press: root._view.show_preview_player(root._item, self.to_window(*self.pos), self.size)# \
                              # if self.collide_point(*args[1].pos) else "") if root._view is not None else None

        ListItemLabel:
            id:    title
            bold:  root.bold
            color: root.color if not root.is_selected else root.selected_text_color
            text: root.name
            opacity: 0.2 if root.dimmed else 1

        ListItemLabel:
            id: number_of_tracks
            bold: root.bold
            color: root.n_color if not root.is_selected else root.selected_text_color
            text: root.number_of_tracks
            halign: 'right'
            size_hint: None, 1
            width: 160    #self.texture_size[0]+10 #, self.texture_size[1]
            opacity: 0.2 if root.dimmed else 1
"""


class PlaylistItem(ModalListItemBase):
    name = StringProperty("")
    number_of_tracks = StringProperty("")
    duration = StringProperty("")

    def refresh_view_attrs(self, rv, data):
        self.__initialize__(data['row'], data['item'], data['view'],
                            data['drag_context'], data['is_selected'])

    def __initialize__(self, row=None, item=None, view=None, drag_context=None, is_selected=False, *args, **kwargs):
        self.row = row
        #self._album_art = None
        self._item_data = item
        self._view = view
        self._item = self._item_data.track if self._item_data is not None else None
        #self._drag_context = drag_context
        #self._long_press_threshold = .25
        #self._preview_player_button = None
        self.is_selected = is_selected
        #self.bind(on_long_press = self._start_dragging)

        # print self._items

        if self._item_data is not None:
            self._update_background()
            self._item_data.bind(is_available=self._update_background)

        if self._item is not None:
            self.name = unicode(
                self._item['list'].name) if self._item['list'].name is not None else "N/A"
            self.number_of_tracks = str(len(self._item['list'])) + ' tracks'


Builder.load_string(kv_string_item)
Factory.register('PlaylistItem', PlaylistItem)
