import os
import io
import re
import mimetypes

from functools import partial
from threading import Thread
from os.path import getsize
from datetime import datetime

from kivy.clock import mainthread, Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.selectableview import SelectableView
from kivy.uix.treeview import TreeViewNode
from kivy.adapters.simplelistadapter import SimpleListAdapter
from kivy.adapters.listadapter import ListAdapter

from kivy.core.image import Image as CoreImage


from kivy.properties import ObjectProperty
from kivy.factory import Factory

#from pydjay.library.track import load_file
#from pydjay.library import get_folders, get_master_playlist, get_playlists, get_sessions, get_session_by_name

#from pydjay.gui.utils import seconds_to_human_readable
from pydjay.ui.elements.clickable_area import ImageButton
from pydjay.ui.behaviors.long_press_button import LongPressButtonBehaviour

#from pydjay.gui.preview_player import PreviewPlayer

from kivy.graphics import *
#from pydjay.uix import recycleview


from track_list_item_base import TrackListItemBase

kv_string_shortlist_item = """
<SimpleTrackCardItem>:
    orientation: 'horizontal'
    size_hint: 1, None
    height:90
    bg:bg
    title: ""
    artist: ""
    image: 'atlas://pydjay/gui/images/resources/default_album_cover'
    album_art:album_art

    on_touch_down: self._on_touch_down(*args)
    on_touch_up: self._on_touch_up(*args)

    Widget:
        id: bg
        size_hint: 1,1
        on_pos:  root._update_background()
        on_size: root._update_background()#self.pos, self.size)

    BoxLayout:
        orientation: 'horizontal'
        size_hint: 1, None
        size_hint: 1,1
        pos_hint: {'x': 0, 'y': 0}
        padding:[10,5,5,5]
        spacing: 8


        RelativeLayout:
            size_hint: (None, 0.9)
            width: self.height
            pos_hint: {'center_y': 0.5}


            Image:
                id: album_art
                size_hint: None, None
                size: 35,35
                pos_hint: {'center_x': .5, 'center_y': 0.5}
                keep_ratio: True
                allow_stretch: True
                source: 'atlas://pydjay/gui/images/resources/precue' #root.image #'pydjay/gui/default_album_cover.png'
                opacity: 0.2 if root.dimmed else 1
                on_touch_up: root._view.preview_track(root._item) \
                           if self.collide_point(*args[1].pos) else ""


        BoxLayout:
            orientation: 'vertical'
            size_hint: 1,.8
            pos_hint: {'center_y': 0.5}

            BoxLayout:
                orientation: 'horizontal'
                size_hint: 1,1

                BoxLayout:
                    orientation: 'vertical'
                    size_hint: 1,1
                    #height: will_play.height
                    #padding:[5,5,5,5]

                    Label:
                        font_size:15
                        text: root.title #"Title"
                        text_size: self.size
                        halign: 'left'
                        valign:'middle'
                        size_hint: 1, 1
                        shorten: True
                        ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}
                        opacity: 0.2 if root.dimmed else 1

                    Label:
                        text: root.artist  #"Artist"
                        color: .6,.6,.6,1
                        text_size: self.size
                        halign: 'left'
                        valigh: 'bottom'
                        font_size: 15
                        size_hint: 1, 1
                        shorten: True
                        ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}
                        height:15
                        opacity: 0.2 if root.dimmed else 1

                Label:
                    font_size:15
                    padding_x:5
                    text: root.length
                    text_size: self.size
                    halign: 'right'
                    valign: 'middle'
                    size_hint: None, 1
                    width: 60 #self.texture_size[0]
                    height:15
                    opacity: 0.2 if root.dimmed else 1
"""


class SimpleTrackCardItem(TrackListItemBase):
    pass


Builder.load_string(kv_string_shortlist_item)
Factory.register('SimpleTrackCardItem', SimpleTrackCardItem)
