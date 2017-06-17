#import os
#import io
#import re
#import mimetypes

#from functools import partial
#from threading import Thread
#from os.path import getsize
#from datetime import datetime

from kivy.clock import mainthread, Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty, ListProperty
#from kivy.uix.boxlayout import BoxLayout
#from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
#from kivy.uix.selectableview import SelectableView
#from kivy.uix.button import Button
#from kivy.uix.treeview import TreeViewNode
#from kivy.adapters.simplelistadapter import SimpleListAdapter
#from kivy.adapters.listadapter import ListAdapter

#from kivy.core.image import Image as CoreImage


from kivy.properties import ObjectProperty
from kivy.factory import Factory

#from pydjay.library.track import load_file
#from pydjay.library import get_folders, get_master_playlist, get_playlists, get_sessions, get_session_by_name

from utils import seconds_to_human_readable
#from pydjay.gui.hover_switch import HoverSwitch
#from pydjay.uix.clickable_area import ImageButton
from pydjay.ui.behaviors.long_press_button import LongPressButtonBehaviour

#from pydjay.gui.preview_player import PreviewPlayer

from kivy.graphics import *
#import pydjay.gui.hover_switch

from pydjay.ui.elements import list_view


class ListItemBase(RelativeLayout,  # LongPressButtonBehaviour,
                   list_view.RecycleViewMixin):
    #    album_art      = ObjectProperty(None)
    #    favorite       = BooleanProperty(False)
    #    has_waveform   = BooleanProperty(False)
    #    title          = StringProperty("")
    #    artist         = StringProperty("")
    #    album          = StringProperty("")
    #    bpm            = StringProperty("")
    #    length         = StringProperty("")
    #    genre          = StringProperty("")
    #    rating         = NumericProperty(0)
    #   style          = StringProperty("")
    bg = ObjectProperty(None)
    dimmed = BooleanProperty(True)
    is_selected = BooleanProperty(False)
    even_color = ListProperty([0, 0, 0, 0.8])
    odd_color = ListProperty([0.1, 0.1, 0.1, 0.8])
    selected_color_focus = ListProperty([0, .3, .7, 1])
    selected_color_no_focus = ListProperty([0, .3, .7, .3])
    selected_text_color = ListProperty([1,1,1, .9])

#
    def __init__(self, row=None, item=None, view=None, drag_context=None, *args, **kwargs):
        super(ListItemBase, self).__init__(*args, **kwargs)
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

        self._initialize_(data['row'], data['item'], data['view'],
                          data['drag_context'], data['is_selected'])

    def _initialize_(self, row=None, item=None, view=None, drag_context=None, is_selected=False, *args, **kwargs):
        pass
#        self.row = row
#        self._album_art = None
#        self._item_data = item
#        self._view = view
#        self._item = self._item_data.track if self._item_data is not None else None
#        self._drag_context = drag_context
#        self._long_press_threshold = .25
#        self._preview_player_button = None
#        self.is_selected = is_selected
#        self.bind(on_long_press = self._start_dragging)
#
#        if self._item_data is not None:
#            self._update_background()
#            self._item_data.bind(is_available = self._update_background)
#
#        if self._item is not None:
#            self.title  = unicode(self._item.metadata.title)
#            self.artist = unicode(self._item.metadata.artist)
#            self.album  = unicode(self._item.metadata.album)
#            self.rating = self._item.metadata.rating if self._item.metadata.rating is not None else 0
#            self.genre  = unicode(self._item.metadata.genre) if self._item.metadata.genre is not None else ""
#            self.style  = unicode(self._item.metadata.style) if self._item.metadata.style is not None else ""
#            self.bpm    = str(self._item.metadata.bpm) if self._item.metadata.bpm is not None else ""
#            self.length = seconds_to_human_readable(int(self._item.info.length /1000000000))
#            self.has_waveform =  self._item.metadata.waveform is not None
#            self.rating = self._item.metadata.rating if self._item.metadata.rating is not None else 0
#            self.favorite = self._item.metadata.loved if self._item.metadata.loved is not None else False
#
#
#            try:
#                self._item.bind(waveform = self._update_waveform_availability)
#            except:
#                pass
#        else:
#            self.title    = ""
#            self.artist   = ""
#            self.album    = ""
#            self.bpm      = ""
#            self.genre    = ""
#            self.style    = ""
#            self.length   = ""
#            self.favorite = False

    def _update_background(self, *value):
        value = self._item_data.is_selected if self._item_data is not None else False
        self.bg.canvas.clear()
        if value:
            #self.color =
            with self.bg.canvas:
                if self._view.has_focus:
                    Color(*self.selected_color_focus)  # 0,.3,.7,1)
                else:
                    Color(*self.selected_color_no_focus)  # 0,.3,.7,.3)
                Rectangle(size=self.bg.size, pos=self.bg.pos)
        else:
            with self.bg.canvas:
                if self.row is not None:
                    with self.bg.canvas:
                        if self.row % 2 == 0:
                            Color(*self.even_color)  # 0,0,0,0.8)
                        else:
                            Color(*self.odd_color)  # .1,.1,.1,.8)
                        Rectangle(pos=self.bg.pos, size=self.bg.size)

        if self._item_data is not None and not self._item_data.is_available:
            self.dimmed = True
        else:
            self.dimmed = False

    def _start_dragging(self, foo, x, y):
        if self._drag_context is not None:
            try:
                self._drag_context.drag(self.to_window(x, y), self._item_data)
            except Exception, details:
                print 'BAR', details

    def _on_touch_down(self, window, event):
        if self.collide_point(*event.pos):
            try:
                self._view.select(self.row)
            except Exception, details:
                print 'foo', details, self._item

    def _on_touch_up(self, window, event):
        if self.collide_point(*event.pos) and self._drag_context.drop is not None:
            if event.pos[1] - self.pos[1] < self.height / 2:
                self._drag_context.drop(self.row + 1)
            else:
                self._drag_context.drop(self.row)
