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
from kivy.uix.button import Button
from kivy.uix.treeview import TreeViewNode
from kivy.adapters.simplelistadapter import SimpleListAdapter
from kivy.adapters.listadapter import ListAdapter

from kivy.core.image import Image as CoreImage


from kivy.properties import ObjectProperty
from kivy.factory import Factory

from pydjay.library.track import load_file
from pydjay.library import get_folders, get_master_playlist, get_playlists, get_sessions, get_session_by_name

from pydjay.gui.utils import seconds_to_human_readable
#from pydjay.gui.hover_switch import HoverSwitch
from pydjay.uix.clickable_area import ImageButton
from pydjay.uix.long_press_button import LongPressButtonBehaviour

#from pydjay.gui.preview_player import PreviewPlayer

from kivy.graphics import *
#import pydjay.gui.hover_switch

#from pydjay.uix import recycleview

from list_item_base import ListItemBase

kv_string_item = """
<SimpleDetailedListItem>:
    album_art: album_art
    album_art_file:'atlas://pydjay/gui/images/resources/transparent_image'
    bg: bg
    size_hint: 1, None
    height:60
    bold: False
    color: 1,1,1,1

    #canvas.before:
    #    Color:
    #        rgba: 1, .3, .8, .7
    #    Rectangle:
    #        pos:  self.pos
    #        size: self.size


    on_touch_down: self._on_touch_down(*args)
    #on_long_press: self._start_dragging()

    #on_pos:  self.update_bg()
    #on_size: self.update_bg()

    Widget:
        id: bg
        size_hint: 1,1
        on_pos:  root._update_background()
        on_size: root._update_background()#self.pos, self.size)
        
        #canvas.before:
        #    Color:
        #        rgba: 1, .3, .8, .7
        #    Rectangle:
        #        pos:  self.pos
        #        size: self.size


    BoxLayout:
        orientation: 'horizontal'
        size_hint: 1, 1
        #size_hint: 1,1 
        padding:[10,3,10,3]
        spacing: 10
#height:35

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
                #on_size: root.update_album_art(*self.size)
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
                #on_touch_down: root._drag_context.show_preview_player(root._item, self.to_window(*self.pos), self.size)
                on_press: root._view.show_preview_player(root._item, self.to_window(*self.pos), self.size)# \
                              # if self.collide_point(*args[1].pos) else "") if root._view is not None else None

            #Button:
            #    size_hint: 1,1

        ListItemLabel:
            id:    title
            bold:  root.bold
            color: root.color
            #font_size:15
            text: root.title
            #text_size: self.size
            #halign: 'left'
            #valign: 'middle'
            #size_hint: 1, 1
            #shorten: True
            #ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}
            opacity: 0.2 if root.dimmed else 1


        ListItemLabel:
            id: artist
            bold: root.bold
            color: root.color
            text: root.artist
            #text_size: self.size
            #halign: 'left'
            #valign: 'middle'
            #font_size: 15
            #size_hint: 1, 1
            #height:15
            #shorten: True
            #ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}
            opacity: 0.2 if root.dimmed else 1

        #ListItemLabel:
        #    id: album
        #    text: root.album
        #    bold: root.bold
        #    color: root.color
        #    #text_size: self.size
        #    #halign: 'left'
        #    #valign: 'middle'
        #    #font_size: 15
        #    #size_hint: 1, 1
        #    #height:15
        #    #shorten: True
        #    #ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}
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
                #on_touch_down: root._drag_context.show_preview_player(root._item, self.to_window(*self.pos), self.size)
                #on_press: root._view.show_preview_player(root._item, self.to_window(*self.pos), self.size)# \
                #               #if self.collide_point(*args[1].pos) else "") if root._view is not None else None

            #Button:
            #    size_hint: 1,1



        #ListItemLabel:
        #    id: genre
        #    text: root.genre if root.genre is not None else ""
        #    bold: root.bold
        #    color: root.color
        #    #text_size: self.size
        #    #halign: 'left'
        #    #valign: 'middle'
        #    #font_size: 15
        #    size_hint: .4, 1
        #    #height:15
        #    #shorten: True
        #    #ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}
        #    opacity: 0.2 if root.dimmed else 1

        #ListItemLabel:
        #    id: style
        #    text: root.style if root.style is not None else ""
        #    bold: root.bold
        #    color: root.color
        #    #text_size: self.size
        #    #halign: 'left'
        #    #valign: 'middle'
        #    #font_size: 15
        #    size_hint: .3, 1
        #    #height:15
        #    #shorten: True
         #   #ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}
         #   opacity: 0.2 if root.dimmed else 1


        ListItemLabel:
            id: bpm
            text: root.bpm
            bold: root.bold
            color: root.color
            #text_size: self.size
            halign: 'right'
            #valign: 'middle'
            #font_size: 15
            size_hint: None, 1
            width:40
            #shorten: True
            #ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}
            opacity: 0.2 if root.dimmed else 1


        ListItemLabel:
            id: length
            bold: root.bold
            color: root.color
            text: root.length
            #text_size: self.texture_size
            halign: 'right'
            #font_size: 15
            size_hint: None, 1
            width: 60    #self.texture_size[0]+10 #, self.texture_size[1]
            opacity: 0.2 if root.dimmed else 1
"""





#import io

#data = io.BytesIO(open("image.png", "rb").read())
#im = CoreImage(data, ext="png", filename="image.png")


    

class SimpleDetailedListItem(ListItemBase):
    pass



"""
class FOOBAR (LongPressButtonBehaviour, RelativeLayout,
                             recycleview.RecycleViewMixin):#,
                             #recycleview.LayoutSelectionMixIn):
    album_art      = ObjectProperty(None)
    album_art_file = ObjectProperty(None)
    favorite       = BooleanProperty(False)
    has_waveform   = BooleanProperty(False)
    title          = StringProperty("")
    artist         = StringProperty("")
    album          = StringProperty("")
    bpm            = StringProperty("")
    length         = StringProperty("")
    genre          = StringProperty("")
    rating         = NumericProperty(0)
    style          = StringProperty("")
    bg             = ObjectProperty(None)
    dimmed         = BooleanProperty(True)
    is_selected       = BooleanProperty(False)

    @classmethod
    def get_header(cls):
        foo = cls()
        #print foo
        foo.size_hint = (1,1)
        foo.bold   = True
        foo.album_art.disabled = True
        foo.title  = "TITLE"#unicode(item.metadata.title)
        foo.artist = "ARTIST"#unicode(item.metadata.artist)
        foo.album  = "ALBUM"#unicode(item.metadata.album)
        foo.bpm    = "BPM"#str(item.metadata.bpm)
        foo.genre  = "GENRE"#str(item.metadata.bpm)
        foo.style  = "STYLE"#str(item.metadata.bpm)
        foo.rating = 0#str(item.metadata.bpm)
        foo.length = "TIME"#seconds_to_human_readable(int(item.info.length /1000))
        return foo

    def __init__(self, row = None, item = None, view = None, drag_context = None, *args, **kwargs):
        super(SimpleDetailedListItem, self).__init__(*args, **kwargs)
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
        
        #self.album_art = 'pydjay/gui/default_album_cover.png'
        self.row = row
        self._album_art = None
        self._item_data = item
        self._view = view
        self._item = self._item_data.track if self._item_data is not None else None
        self._drag_context = drag_context
        self._long_press_threshold = .25
        self._preview_player_button = None
        self.is_selected = is_selected
        self.bind(on_long_press = self._start_dragging)

        

        
        if self._item_data is not None:
            self._update_background()#None, self._item_data.is_selected)
            self._update_availability()#None, self._item_data.is_available)
            self._item_data.bind(#is_selected  = self._update_background,
                                 is_available = self._update_background)
            
        if self._item is not None:
            self.title  = unicode(self._item.metadata.title)
            self.artist = unicode(self._item.metadata.artist)
            self.album  = unicode(self._item.metadata.album)
            #self.genre  = unicode(self._item.metadata.genre) if self._item.metadata.genre is not None else ""
            self.rating = self._item.metadata.rating if self._item.metadata.rating is not None else 0
            
            self.genre  = unicode(self._item.metadata.genre) if self._item.metadata.genre is not None else ""
            self.style  = unicode(self._item.metadata.style) if self._item.metadata.style is not None else ""
            self.bpm    = str(self._item.metadata.bpm) if self._item.metadata.bpm is not None else ""
            self.length = seconds_to_human_readable(int(self._item.info.length /1000000000))
            self.has_waveform =  self._item.metadata.waveform is not None
            self.rating = self._item.metadata.rating if self._item.metadata.rating is not None else 0
            self.favorite = self._item.metadata.loved


            try:
                # JUST SO I DON'T FORGET
                self._item.bind(waveform = self._update_waveform_availability)
            except:
                pass

            
            #if self._item.metadata.album_cover is not None:
            #    try:
            #        self.album_art.source = self._item.metadata.album_cover['tiny']
            #    except:
            #        self.album_art.source = 'atlas://pydjay/gui/images/resources/default_album_cover'
                #im_type = self._item.metadata.album_cover[0]
                #im_data = self._item.metadata.album_cover[1]
                #ext = {'image/jpeg': 'jpg','image/png': 'png'}.get(im_type, None)
                #if ext is not None:
                #    data = io.BytesIO(im_data)
                #    im   = CoreImage(data, ext = ext)
                #    self._album_art = im
            #else:
            #    self.album_art.source = 'atlas://pydjay/gui/images/resources/default_album_cover'
        else:
            #self.album_art.source = 'pydjay/gui/transparent_image.png'
            self.title    = ""#unicode(item.metadata.title)
            self.artist   = ""#unicode(item.metadata.artist)
            self.album    = ""#unicode(item.metadata.album)
            self.bpm      = ""#str(item.metadata.bpm)
            self.genre    = ""#str(item.metadata.bpm)
            self.style    = ""#str(item.metadata.bpm)
            self.length   = ""#seconds_to_human_readable(int(item.info.length /1000))
            self.favorite = False
            #self.album_art.source = 'pydjay/gui/default_album_cover.png'


                #self.update_bg()

    def _update_availability(self, *args):#win, value):
        pass

    def on_motion_catch(self, *args):
        print args

    def show_preview_player_button(self, window, event):
        #print event
        if self.collide_point(*event.pos):
            if self._preview_player_button is None:
                self._preview_player_button = Button(size = self.album_art.size,
                                                     pos = self.album_art.pos)
                self.add_widget(self._preview_player_button)
        else:
            if self._preview_player_button is not None:
                self.remove_widget(self._preview_player_button)
                self._preview_player_button = None
                
    
    def _update_background(self, *value):
        #print "UPDATE BACKGROUND AVAILABILITY"
        #value = self._item_data.is_selected if self._item_data is not None else False
        value = self._item_data.is_selected if self._item_data is not None else False
        
        #self.bold = value
        self.bg.canvas.clear()
        if value:
            with self.bg.canvas:
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
            self.dimmed = False
        self.update_album_art(33,33)
        
    def _start_dragging(self, foo, x, y):
        #print 'start_drag', self._drag_context
        if self._drag_context is not None:
            try:
                self._drag_context.drag(self.to_window(x,y), self._item)
            except Exception, details:
                print details
                
    def update_bg(self, *args):
        if self.row is not None:
            self.bg.canvas.clear()
            with self.bg.canvas:
                if self.row % 2 == 0:
                    Color(0,0,0,0.8)
                else:
                    Color(.1,.1,.1,.8)
                Rectangle(pos=self.bg.pos, size=self.bg.size)
        
        
    def update_album_art(self, w, h):
        if self._album_art is not None:
            self.album_art.texture = self._album_art.texture

    #def select(self, *args):
    #    print "SELECT"

    def _on_touch_down(self, window, event):
        if self.collide_point(*event.pos):
            try:
                
                #    if event.is_double_tap:
                #        self._view.add_shortlist_track(self._item)
                #    else:
                #self._view.preview_player.set_track(self._item)
                self._view.select(self.row)
                #self._item_data.is_selected = True #not self._item_data.is_selected #True
                #self._update_background()
            except Exception, details:
                print details, self._item
"""                

Builder.load_string(kv_string_item)
Factory.register('SimpleDetailedListItem', SimpleDetailedListItem)

#_item_pool = []
#for x in range(100):
#    print x
#    _item_pool.append(SimpleDetailedListItem_internal())


#def SimpleDetailedListItem(row = None, item = None, view = None, drag_context = None, *args, **kwargs):
#    global _item_pool
#    if len(_item_pool) > 0:
#        item = _item_pool.pop()
#        item.__initialize__(row, item, view, drag_context)
#    else:
#        item = SimpleDetailedListItem_internal(row, item, view, drag_context, *args, **kwargs)
#    return item
