import os
import re
import io
import mimetypes
import time
import threading
import socket
import urllib
import json

from functools import partial
from threading import Thread
from os.path import getsize
from datetime import datetime

from kivy.event import EventDispatcher
from kivy.clock import mainthread, Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty, ListProperty, BooleanProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget
from kivy.uix.selectableview import SelectableView
from kivy.adapters.listadapter import ListAdapter


#from pydjay.utils.protocol import ControlServer
#from pydjay.utils.protocol import ControlClient

from kivy.properties import ObjectProperty
from kivy.factory import Factory

from kivy.graphics import *

#from pydjay.library.track import load_file
#from kivy.core.image import Image as CoreImage
#from pydjay.gui.turntable import turntable
from utils import seconds_to_human_readable
from pydjay.ui.behaviors.long_press_button import LongPressButtonBehaviour


from kivy.logger import Logger

#from pydjay.uix import recycleview
#import player_deck
#import player_display
#from track_upload_queue import TrackUploadQueue
#from pydjay.uix import screen, paged_grid, paged_display
#from pydjay.uix import clickable_area
#from pydjay.uix import long_press_button
#from pydjay.uix import screen

#from pydjay.gui.files_screen import file_browser, location_browser
#from mediacentre.skins.default.theme import get_path
#from track_upload import DelayedTrack
#from current_session_list import CurrentSessionList

from track_list_item_base import TrackListItemBase


kv_string_item = """
<MasterQueueTrackCard>:
    orientation: 'horizontal'
    size_hint: 1, None
    bg: bg
    title:     ""
    artist:    ""
    image:     'atlas://pydjay/gui/images/resources/default_album_cover'
    album_art: album_art
    on_pos:  root._update_background()#self.pos, self.size)
    on_size: root._update_background()#self.pos, self.size)
    on_touch_up: self._on_touch_up(*args)
    on_touch_down: self._on_touch_down(*args)

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
        padding:[10,5,7,5]
        spacing: 8
        RelativeLayout:
            size_hint: (None, .8)
            width: self.height
            pos_hint: {'center_y': 0.5}

            Image:
                id: album_art
                size_hint: 1,1
                keep_ratio: True
                allow_stretch: True
                source: root.image #'pydjay/gui/default_album_cover.png'
                on_touch_up: root._view.show_preview_player(root._item, self.to_window(*self.pos), self.size) \
                           if self.collide_point(*args[1].pos) else ""

        BoxLayout:
            orientation: 'vertical'
            size_hint: 1,.85
            pos_hint: {'center_y': 0.5}

            BoxLayout:
                orientation: 'horizontal'
                size_hint: 1,1
                #height: will_play.height
                #padding:[5,5,5,2]

                Label:
                    font_size:15
                    bold: True
                    text: root.title #"Title"
                    text_size: self.size
                    halign: 'left'
                    valign: 'middle'
                    size_hint: 1, 1
                    shorten: True
                    ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}

                    #height:will_play.height

                Label:
                    font_size:15
                    bold:True
                    padding_x:5
                    text: root.length
                    text_size: self.size
                    halign: 'right'
                    valign: 'middle'
                    size_hint: None, 1
                    width: 60 #self.texture_size[0]
                    height:15


            BoxLayout:
                orientation: 'horizontal'
                size_hint: 1, 1
                width:65

                Label:
                    text: root.artist  #"Artist"
                    color: .6,.6,.6,1
                    text_size: self.size
                    halign: 'left'
                    valign: 'top'
                    font_size: 15
                    size_hint: 1, 1
                    shorten: True
                    ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}
                    height:15

                Label:
                    font_size:13
                    color: .6,.6,.6,1
                    padding_x:5
                    text: root.play_time
                    text_size: self.size
                    halign: 'right'
                    valign: 'top'
                    size_hint: None, 1
                    width: 60 #self.texture_size[0]
                    height:13
"""



class MasterQueueTrackCard(TrackListItemBase):
    play_time = StringProperty("")

    def __init__(self, row = None, item = None, view = None, drag_context = None, *args, **kwargs):
        super(MasterQueueTrackCard, self).__init__(*args, **kwargs)
        self.__initialize__(row, item, view, drag_context)

    def refresh_view_attrs(self, rv, data):
        '''Called by the :class:`RecycleAdapter` when the view is initially
        populated with the values from the `data` dictionary for this item.
        :Parameters:
            `rv`: :class:`RecycleView` instance
                The :class:`RecycleView` that caused the update.
            `data`: dict
                The data dict used to populate this view.
        '''

        self.__initialize__(data['row'], data['item'], data['view'], data['drag_context'], data['is_selected'])

    def __initialize__(self, row = None, item = None, view = None, drag_context = None, is_selected = False, *args, **kwargs):
        super(MasterQueueTrackCard, self).__initialize__(row, item, view, drag_context, is_selected)
        if self._item is not None:
            self.play_time = self._item_data.play_time
            self._item_data.bind(play_time = self._play_time_change)

            if self._item.metadata.album_cover is not None:
                try:
                    self.album_art.source = self._item.metadata.album_cover['small']
                except Exception, details:
                    print details
                    self.album_art.source = 'atlas://pydjay/gui/images/resources/default_album_cover'
            else:
                self.album_art.source = 'atlas://pydjay/gui/images/resources/default_album_cover'
        else:
            self.title  = ""
            self.artist = ""
            self.album  = ""
            self.bpm    = ""
            self.length = ""

    def _play_time_change(self, obj, new_value):
        #print "PLAY TIME CHANGED", self._item_data.play_time
        self.play_time = new_value


Builder.load_string(kv_string_item)
Factory.register('MasterQueueTrackCard', MasterQueueTrackCard)
