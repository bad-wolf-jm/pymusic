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

from pydjay.library.track import load_file
from pydjay.library import get_folders, get_master_playlist, get_playlists, get_sessions, get_session_by_name

from pydjay.gui.utils import seconds_to_human_readable
from pydjay.uix.clickable_area import ImageButton
from pydjay.uix.long_press_button import LongPressButtonBehaviour

#from pydjay.gui.preview_player import PreviewPlayer

from kivy.graphics import *
#from pydjay.uix import recycleview


from list_item_base import ListItemBase

kv_string_shortlist_item = """
#<HDivider@Widget>
#    size_hint: 1, None
 #   height: 1
 #   canvas.after:
 #       Color:
 #           rgba: 1, 1, 1, .8
 #       Line:
 #           points: [self.pos[0],self.pos[1], self.pos[0] + self.width, self.pos[1]]
#
#<VDivider@Widget>
#    size_hint: None, 1
#    width: 1
#    canvas.after:
#        Color:
#            rgba: 1, 1, 1, .8
#        Line:
#            points: [self.pos[0], self.pos[1], self.pos[0], self.pos[1]+self.height]

<SimpleTrackCardItem>:
    orientation: 'horizontal'
    size_hint: 1, None
    height:90
    bg:bg
    title: ""
    artist: ""
    image: 'atlas://pydjay/gui/images/resources/default_album_cover'
    album_art:album_art

    #on_pos:  root.update_bg()#self.pos, self.size)
    #on_size: root.update_bg()#self.pos, self.size)
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
                #on_touch_down: root._view.show_preview_player(root._item, self.to_window(*self.pos), self.size)
#                on_touch_up: root._view.show_preview_player(root._item, self.to_window(*self.pos), self.size) \
#                           if self.collide_point(*args[1].pos) else ""
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

                        #height:will_play.height
                    #Widget:
                    #    size_hint: 1, 1


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
                   # canvas.before:
                   #     Color:
                   #         rgba: .1, .1, .1, .8
                   #     Rectangle:
                   #         pos:  self.pos
                   #         size: self.size

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
            #BoxLayout:
            #    orientation: 'horizontal'
            #    size_hint: 1,.5
            #    padding: [0,0,4,0]
            #    Label:
            #        text: "[i]GENRE: " + root.genre+"[/i]" if root.genre is not None else ""
            #        color: .6,.6,.6,1
            #        markup: True
            #        text_size: self.size
            #        halign: 'left'
            #        valign: 'middle'
            #        font_size: 12
            #        size_hint: 1, None
            #        shorten: True
            #        ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}
            #        height:15
            #        opacity: 0.2 if root.dimmed else 1
            #    Label:
            #        text: "[i]BPM: " + root.bpm +"[/i]" if root.bpm is not None else ""
            #        color: .6,.6,.6,1
            #        markup: True
            #        text_size: self.size
            #        halign: 'right'
            #        valign: 'middle'
            #        font_size: 12
            #        size_hint: 1, None
            #        shorten: True
            #        ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}
            #        height:15
            #        opacity: 0.2 if root.dimmed else 1


"""


class SimpleTrackCardItem(ListItemBase):
    pass


"""
class FOOBAR(LongPressButtonBehaviour, RelativeLayout,
             recycleview.RecycleViewMixin):
    album_art = ObjectProperty(None)
    album_art_file = ObjectProperty(None)
    title          = StringProperty("")
    artist         = StringProperty("")
    album     = StringProperty("")
    bpm       = StringProperty("")
    length    = StringProperty("")
    genre    = StringProperty("")
    bg        = ObjectProperty(None)
    track     = ObjectProperty(None)
    play_time = StringProperty("")
    bg             = ObjectProperty(None)
    dimmed             = BooleanProperty(None)

    
    def __init__(self, row = None,  item = None, view = None, drag_context = None, *args, **kwargs):
        super(SimpleTrackCardItem, self).__init__(*args, **kwargs)
        #self.height = 90
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
        
        #for key, value in data.items():
        #    setattr(self, key, value)
        self.__initialize__(data['row'], data['item'], data['view'], data['drag_context'], data['is_selected'])

    def __initialize__(self, row = None, item = None, view = None, drag_context = None, is_selected = False, *args, **kwargs):        
        self.row = row
        self._album_art = None
        self._item_data = item
        self._item = self._item_data.track if self._item_data is not None else None #item.track
        self.track = self._item_data.track if self._item_data is not None else None #item.track
        self._view = view
        #self._add_item = add_item
        #self._remove_item = remove_item
        self._drag_context = drag_context

        self._long_press_threshold = .25
        self.bind(on_long_press = self._start_dragging)

        if self._item_data is not None:
            Clock.schedule_once(self._update_background, -1)#None, self._item_data.is_selected)
            self._update_availability()#None, self._item_data.is_available)
            self._item_data.bind(is_selected  = self._update_background,
                                 is_available = self._update_background)

        if self._item is not None:
            self.title  = unicode(self._item.metadata.title)
            self.artist = unicode(self._item.metadata.artist)
            self.album  = unicode(self._item.metadata.album)
            self.bpm    = str(self._item.metadata.bpm)
            self.genre  = str(self._item.metadata.genre)
            self.length = seconds_to_human_readable(int(self._item.info.length /1000000000))
            #if self._item.metadata.album_cover is not None:
            #    try:
            #        self.image = self._item.metadata.album_cover['small']
            #    except:
            #        self.image = 'atlas://pydjay/gui/images/resources/default_album_cover'
            #    #im_type = self._item.metadata.album_cover[0]
            #    #im_data = self._item.metadata.album_cover[1]
            #    #ext = {'image/jpeg': 'jpg','image/png': 'png'}.get(im_type, None)
            #    #if ext is not None:
            #     #   data = io.BytesIO(im_data)
            #     #   im   = CoreImage(data, ext = ext)
            #     #   self._album_art = im
            #else:
                #self.image = 'atlas://pydjay/gui/images/resources/default_album_cover'
        else:
            self.title  = ""#unicode(item.metadata.title)
            self.artist = ""#unicode(item.metadata.artist)
            self.album  = ""#unicode(item.metadata.album)
            self.bpm    = ""#str(item.metadata.bpm)
            self.length = ""#seconds_to_human_readable(int(item.info.length /1000))


    def _update_availability(self, *args):#win, value):
        pass
    
    def _update_background(self, *value):
        #print "UPDATE BACKGROUND AVAILABILITY"
        value = self._item_data.is_selected if self._item_data is not None else False
        self.bold = value
        self.bg.canvas.clear()
        if value:
            with self.bg.canvas:
                #Color(0,.3,.7,1)
                
                if self._view.has_focus:
                    Color(0,.3,.7,1)
                else:
                    Color(0,.3,.7,.3)
                Rectangle(size = self.bg.size, pos = self.bg.pos)
        else:
            with self.bg.canvas:
                if self.row is not None:
                    with self.bg.canvas:
                        if self.row % 2 == 0:
                            Color(0,0,0,0.8)
                        else:
                            Color(.1,.1,.1,.8)
                        Rectangle(pos=self.bg.pos, size=self.bg.size)
        
        if self._item_data is not None and not self._item_data.is_available:
            self.dimmed = True#opacity = 0.1
        else:
            self.dimmed = False #opacity = 1
        #self.update_album_art(33,33)

            
    def _start_dragging(self, foo, x, y):
        self._drag_context.drag(self.to_window(x,y), self._item_data)
            
                #self.update_bg()
    def update_bg(self, *args):
        self.update_album_art(33,33)
        
    def update_album_art(self, w, h):
        if self._album_art is not None:
            self.album_art.texture = self._album_art.texture

    def _on_touch_down(self, window, event):
        if self.collide_point(*event.pos):
            #self._view.preview_player.set_track(self.track)
            #self._item_data.is_selected = True
            self._view.select(self.row)
            #if event.is_double_tap:
            #    self._view.enqueue_track(self._item_data)
                

    def _on_touch_up(self, window, event):
        if self.collide_point(*event.pos):
            #if self._window is not None and self._window._drag_payload is not None:
            if event.pos[1] - self.pos[1] < self.height / 2:
                #self._add_item(self._window._drag_payload, self.row + 1)
                self._drag_context.drop(self.row + 1)

                #self._view.add_shortlist_track(self._window._drag_payload, )
            else:
                #self._add_item(self._window._drag_payload, self.row + 1)
                self._drag_context.drop(self.row)
                #
                #self._window.drop()
            #else:
            #    print "NOT ADDING", self._window, self._window._is_dragging
"""

Builder.load_string(kv_string_shortlist_item)
Factory.register('SimpleTrackCardItem', SimpleTrackCardItem)


