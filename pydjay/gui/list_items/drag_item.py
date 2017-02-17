import os
import re
import io
import mimetypes

from functools import partial
from threading import Thread
from os.path import getsize
from datetime import datetime

from kivy.clock import mainthread, Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
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

#from pydjay.uix import screen, paged_grid, paged_display



kv_drag_widget= """
<DragItem>:
    orientation: 'horizontal'
    size_hint: None, None
    size: 350,75
    title: ""
    artist: ""
    image: 'atlas://pydjay/gui/images/resources/default_album_cover'
    album_art:album_art

    on_pos:  root.update_bg()#self.pos, self.size)
    on_size: root.update_bg()#self.pos, self.size)
    #on_touch_down: self._on_touch_down(*args)

    canvas:
        Color:
            rgba:.5,.5,.5,1
        Rectangle:
            pos:  0,0
            size: self.size

    BoxLayout:
        orientation: 'horizontal'
        size_hint: 1, None
        size_hint: 1,1 
        pos_hint: {'x': 0, 'y': 0}
        padding:[5,5,5,7]
        spacing: 8
        Image:
            id: album_art
            size_hint: (None, 1)
            width: self.height
            keep_ratio: True
            allow_stretch: True
            source: root.image #'pydjay/gui/default_album_cover.png'

        BoxLayout:
            orientation: 'vertical'
            size_hint: 1,1
            #height: will_play.height
            padding:[5,5,5,5]
      
            Label:
                font_size: 15
                color: .1,.1,.1,1
                text: root.title #"Title"
                text_size: self.size
                halign: 'left'
                valign: 'middle'
                size_hint: 1, 1
                shorten: True
                ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}

                #height:will_play.height

            Label:
                text: root.artist  #"Artist"
                color: .3,.3,.3,1
                text_size: self.size
                halign: 'left'
                valigh: 'middle'
                font_size: 15
                size_hint: 1, 1
                shorten: True
                ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}
               

        #Label:
        #    canvas.before:
        #        Color:
        #            rgba: .2, .2, .2, .8
        #        Rectangle:
        #            pos:  self.pos
        #            size: self.size
#
#            font_size:15
#            padding_x:5
#            text: root.play_time
#            text_size: self.size
#            halign: 'right'
#            valign: 'middle'
#            size_hint: None, 1
#            width: 60 #self.texture_size[0]
#            height:15
"""

#class MasterQueueTrackCard(RelativeLayout):

#
 #   
 #   def add_track(self, track):
 #       pass



class DragItem(LongPressButtonBehaviour, RelativeLayout, SelectableView):
    album_art = ObjectProperty(None)
    album_art_file = ObjectProperty(None)
    title     = StringProperty("")
    artist    = StringProperty("")
    album     = StringProperty("")
    bpm       = StringProperty("")
    length    = StringProperty("")
    bg        = ObjectProperty(None)
    track     = ObjectProperty(None)
    play_time = StringProperty("")

    def __init__(self, item = None, *args, **kwargs):
        super(DragItem, self).__init__(*args, **kwargs)
        #self.album_art = 'pydjay/gui/default_album_cover.png'
        #self.row = row
        self._album_art = None
        self._item = item
        self.track = item
        #self._view = view
        #print "ITEM:::  ",
        #print item
        #print kwargs
        #$row  = kwargs['row']
        #$item = kwargs['item']
        #print row, item
        if item is not None:
            self.title  = unicode(item.metadata.title)
            self.artist = unicode(item.metadata.artist)
            self.album  = unicode(item.metadata.album)
            self.bpm    = str(item.metadata.bpm)
            #self.length = seconds_to_human_readable(int(item.info.length /1000))



            if item.metadata.album_cover is not None:
                try:
                    self.album_art.source = item.metadata.album_cover['small']
                except:
                    self.album_art.source = 'atlas://pydjay/gui/images/resources/default_album_cover'
                #im_type = item.metadata.album_cover[0]
                #im_data = item.metadata.album_cover[1]
                ##print im_type
                #ext = {'image/jpeg': 'jpg','image/png': 'png'}.get(im_type, None)
                #if ext is not None:
                #    data = io.BytesIO(im_data)
                #    im   = CoreImage(data, ext = ext)
                #    self._album_art = im
                #    #print im.texture.size
            else:
                self.album_art.source = 'atlas://pydjay/gui/images/resources/default_album_cover'
        else:
            self.title  = ""#unicode(item.metadata.title)
            self.artist = ""#unicode(item.metadata.artist)
            self.album  = ""#unicode(item.metadata.album)
            self.bpm    = ""#str(item.metadata.bpm)
            self.length = ""#seconds_to_human_readable(int(item.info.length /1000))
            #self.album_art.source = 'pydjay/gui/default_album_cover.png'


                #self.update_bg()
    def update_bg(self, *args):
        pass
        #print self.row, self.bg.pos, self.bg.size, self.album_art.size
        #if self.row is not None:
        #    #print 'changing canvas color'
        #    self.bg.canvas.clear()
        #    with self.bg.canvas:
        #        if self.row % 2 == 0:
        #            Color(0,0,0,0.8)
        #        else:
        #            Color(.1,.1,.1,.8)
        #        Rectangle(pos=self.bg.pos, size=self.bg.size)
        #self.update_album_art(33,33)
        
    def update_album_art(self, w, h):
       # print "updating", w, h
        #if self._item.metadata.album_cover is not None:
        #    im_type = self._item.metadata.album_cover[0]
        #    im_data = self._item.metadata.album_cover[1]
        #        #print im_type
        #    ext = {'image/jpeg': 'jpg','image/png': 'png'}.get(im_type, None)
        #    if ext is not None:
        #        data = io.BytesIO(im_data)
        #        im   = CoreImage(data, ext = ext)
        #        self._album_art = im
        if self._album_art is not None:
    #        #self._album_art.texture.size = self.album_art.size
            self.album_art.texture = self._album_art.texture



#    def update_bg(self, *args):
#        #print self.row, self.bg.pos, self.bg.size, self.album_art.size
#        if self.row is not None:
#            #print 'changing canvas color'
#            self.bg.canvas.clear()
#            with self.bg.canvas:
#                if self.row % 2 == 0:
#                    Color(0,0,0,0.8)
#                else:
#                    Color(.1,.1,.1,.8)
#                Rectangle(pos=self.bg.pos, size=self.bg.size)
#        self.update_album_art(33,33)
        
#    def update_album_art(self, w, h):
#       # print "updating", w, h
#        if self._album_art is not None:
#    #        #self._album_art.texture.size = self.album_art.size
#            self.album_art.texture = self._album_art.texture

#    #def _select_me(self):
#    #    print "FOO", self.title
#    #    self.is_selected = True

#    def select(self, *args):
#        print "SELECT"

#    def _on_touch_down(self, window, event):
#        #print window, event
#        if self.collide_point(*event.pos):
#            self._view.preview_player.set_track(self.track)
#            if event.is_double_tap:
#                self._view.enqueue_track(self.track)
#            #else:
#            #    self.

  



Builder.load_string(kv_drag_widget)
#Factory.register('DragItem', DragItem)
