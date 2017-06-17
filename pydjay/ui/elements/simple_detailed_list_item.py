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
from clickable_area import ImageButton
from pydjay.ui.behaviors.long_press_button import LongPressButtonBehaviour

from kivy.graphics import *

from track_list_item_base import TrackListItemBase

kv_string_item = """
<SimpleDetailedListItem>:
    album_art: album_art
    album_art_file:'atlas://pydjay/gui/images/resources/transparent_image'
    bg: bg
    size_hint: 1, None
    height:60
    bold: False
    color: 1,1,1,1
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
        padding:[10,3,10,3]
        spacing: 10

        RelativeLayout:
            size_hint: None, 1
            width: 20
            Image:
                #id: album_art
                bold: root.bold
                color: root.color
                size_hint: (None, None)
                size: 12,12
                pos_hint: {'center_x':.5, 'center_y':.5}
                #width: self.height
                keep_ratio: True
                allow_stretch: True
                source: 'atlas://pydjay/gui/images/resources/love-focus' if root.favorite else 'atlas://pydjay/gui/images/resources/love'
                opacity: 0.2 if (root.dimmed or not root.favorite) else 1

        RelativeLayout:
            size_hint: None, 1
            width: self.height

            ImageButton:
                id: album_art
                #bold: root.bold
                #color: root.color
                #size_hint: 1,1
                size_hint: (None, .6)
                #pos_hint: {'center_y': .5}
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
            color: root.color
            text: root.title
            opacity: 0.2 if root.dimmed else 1


        ListItemLabel:
            id: artist
            bold: root.bold
            color: root.color
            text: root.artist
            opacity: 0.2 if root.dimmed else 1

        ListItemLabel:
            id: genre
            size_hint: .4,1
            bold: root.bold
            color: root.color
            text: root.genre
            opacity: 0.2 if root.dimmed else 1

        #ListItemLabel:
        #    id: style
        #    size_hint: .4,1
        #    bold: root.bold
        #    color: root.color
        #    text: root.style
        #    opacity: 0.2 if root.dimmed else 1



        RelativeLayout:
            size_hint: None, 1
            width: 60 #self.height

            Image:
                id: rating
                bold: root.bold
                color: root.color
                #size_hint: 1,1
                size_hint: (None, .6)
                #pos_hint: {'center_y': .5}
                pos_hint: {'center_x':.5, 'center_y':.5}
                width: 60
                keep_ratio: True
                allow_stretch: True
                source: 'atlas://pydjay/gui/images/resources/rating%s'%root.rating
                opacity: 0.2 if root.dimmed else 1

        ListItemLabel:
            id: bpm
            text: root.bpm
            bold: root.bold
            color: root.color
            halign: 'right'
            size_hint: None, 1
            width:40
            opacity: 0.2 if root.dimmed else 1


        ListItemLabel:
            id: length
            bold: root.bold
            color: root.color
            text: root.length
            halign: 'right'
            size_hint: None, 1
            width: 60    #self.texture_size[0]+10 #, self.texture_size[1]
            opacity: 0.2 if root.dimmed else 1
"""


class SimpleDetailedListItem(TrackListItemBase):
    pass


Builder.load_string(kv_string_item)
Factory.register('SimpleDetailedListItem', SimpleDetailedListItem)
