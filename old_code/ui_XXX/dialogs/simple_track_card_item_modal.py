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
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty
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

from pydjay.ui.elements.utils import seconds_to_human_readable
from pydjay.ui.elements.clickable_area import ImageButton
from pydjay.ui.behaviors.long_press_button import LongPressButtonBehaviour

#from pydjay.gui.preview_player import PreviewPlayer

from kivy.graphics import *
#from pydjay.uix import recycleview


from list_item_base import ModalListItemBase

kv_string_shortlist_item = """
<SimpleTrackCardItemModal>:
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
                        color: .1,.1,.1,1
                        halign: 'left'
                        valign:'middle'
                        size_hint: 1, 1
                        shorten: True
                        ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}
                        opacity: 0.2 if root.dimmed else 1

                    Label:
                        text: root.artist  #"Artist"
                        color: .3,.3,.3,1
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
                    color: .1,.1,.1,1
                    text: root.length
                    text_size: self.size
                    halign: 'right'
                    valign: 'middle'
                    size_hint: None, 1
                    width: 60 #self.texture_size[0]
                    height:15
                    opacity: 0.2 if root.dimmed else 1
"""


class SimpleTrackCardItemModal(ModalListItemBase):
    album_art = ObjectProperty(None)
    favorite = BooleanProperty(False)
    has_waveform = BooleanProperty(False)
    title = StringProperty("")
    artist = StringProperty("")
    album = StringProperty("")
    bpm = StringProperty("")
    length = StringProperty("")
    genre = StringProperty("")
    rating = NumericProperty(0)
    style = StringProperty("")
    pass

    def refresh_view_attrs(self, rv, data):
        '''Called by the :class:`RecycleAdapter` when the view is initially
        populated with the values from the `data` dictionary for this item.
        :Parameters:
            `rv`: :class:`RecycleView` instance
                The :class:`RecycleView` that caused the update.
            `data`: dict
                The data dict used to populate this view.
        '''

        self.__initialize__(data['row'], data['item'], data['view'],
                            data['drag_context'], data['is_selected'])

    def __initialize__(self, row=None, item=None, view=None, drag_context=None, is_selected=False, *args, **kwargs):
        self.row = row
        self._album_art = None
        self._item_data = item
        self._view = view
        self._item = self._item_data.track if self._item_data is not None else None
        self._drag_context = drag_context
        self._long_press_threshold = .25
        self._preview_player_button = None
        self.is_selected = is_selected
        self.bind(on_long_press=self._start_dragging)

        if self._item_data is not None:
            self._update_background()
            self._item_data.bind(is_available=self._update_background)

        if self._item is not None:
            self.title = unicode(self._item.metadata.title)
            self.artist = unicode(self._item.metadata.artist)
            self.album = unicode(self._item.metadata.album)
            self.rating = self._item.metadata.rating if self._item.metadata.rating is not None else 0
            self.genre = unicode(
                self._item.metadata.genre) if self._item.metadata.genre is not None else ""
            self.style = unicode(
                self._item.metadata.style) if self._item.metadata.style is not None else ""
            self.bpm = str(self._item.metadata.bpm) if self._item.metadata.bpm is not None else ""
            self.length = seconds_to_human_readable(int(self._item.info.length / 1000000000))
            self.has_waveform = self._item.metadata.waveform is not None
            self.rating = self._item.metadata.rating if self._item.metadata.rating is not None else 0
            self.favorite = self._item.metadata.loved if self._item.metadata.loved is not None else False

            try:
                self._item.bind(waveform=self._update_waveform_availability)
            except:
                pass
        else:
            self.title = ""
            self.artist = ""
            self.album = ""
            self.bpm = ""
            self.genre = ""
            self.style = ""
            self.length = ""
            self.favorite = False


Builder.load_string(kv_string_shortlist_item)
Factory.register('SimpleTrackCardItemModal', SimpleTrackCardItemModal)
