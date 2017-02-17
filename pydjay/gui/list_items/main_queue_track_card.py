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


from pydjay.utils.protocol import ControlServer
from pydjay.utils.protocol import ControlClient

from kivy.properties import ObjectProperty
from kivy.factory import Factory

from kivy.graphics import *

from pydjay.library.track import load_file
from kivy.core.image import Image as CoreImage
#from pydjay.gui.turntable import turntable
from pydjay.gui.utils import seconds_to_human_readable
from pydjay.uix.long_press_button import LongPressButtonBehaviour


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

from list_item_base import ListItemBase


kv_string_item = """
#$
#$<HDivider@Widget>
#    size_hint: 1, None
#    height: 1
#    canvas.after:
#        Color:
#            rgba: 1, 1, 1, .8
#        Line:
#            points: [self.pos[0],self.pos[1], self.pos[0] + self.width, self.pos[1]]
#
#<VDivider@Widget>
#    size_hint: None, 1
#    width: 1
#    canvas.after:
#        Color:
#            rgba: 1, 1, 1, .8
#        Line:
#            points: [self.pos[0], self.pos[1], self.pos[0], self.pos[1]+self.height]

<MasterQueueTrackCard>:
    orientation: 'horizontal'
    size_hint: 1, None
    bg: bg
    #height:    60
    title:     ""
    artist:    ""
    image:     'atlas://pydjay/gui/images/resources/default_album_cover'
    album_art: album_art
    #padding: [5,6,5,6]


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

            #Image:
            #    size_hint: None,None
            #    keep_ratio: True
            #    allow_stretch: True
            #    source: root.image #'pydjay/gui/default_album_cover.png'

            Image:
                id: album_art
                size_hint: 1,1
                keep_ratio: True
                allow_stretch: True
                source: root.image #'pydjay/gui/default_album_cover.png'
                on_touch_up: root._view.show_preview_player(root._item, self.to_window(*self.pos), self.size) \
                           if self.collide_point(*args[1].pos) else ""

            #BoxLayout:
            #    orientation: 'vertical'
            #    size_hint: 1,1
            #    #opacity: 0 if (root.track is not None and root.track.done) else 1 #0 if root.show_upload_progress else 1
            #    opacity: 1 if root.show_upload_progress else 0
            #    canvas.before:
            #        Color:
            #            rgba: .15, .15, .15, .95
            #        Rectangle:
            #            pos:  self.pos
            #            size: self.size

             #   Label:
             #       size_hint: 1,1
             #       font_size: 15
             #       #height: 15
             #       pos_hint: {'center_x':0.5, 'center_y': .5}
             #   
             #       text: "Uploading..."
             #   ProgressBar:
             #       size_hint: 1,1
             #       pos_hint: {'center_x':0.5, 'center_y': .5}
             #       min: 0
             #       max: 100
             #       value: root.upload_progress * 100

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
                #padding:[5,2,5,5]
                #canvas.before:
                #    Color:
                #        rgba: .15, .15, .15, .8
                #    Rectangle:
                #        pos:  self.pos
                #        size: self.size

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
            #BoxLayout:
            #    orientation: 'horizontal'
            #    size_hint: 1,1
            #    #padding:[5,0,9,2]
            #    Widget:
             #       size_hint: 1, None
            ##    Label:
            ##        text: "[i]GENRE: " + root.genre+"[/i]" if root.genre is not None else ""
            ##        color: .6,.6,.6,1
            ##        markup: True
            ##        text_size: self.size
            ##        halign: 'left'
            ##        valigh: 'middle'
            ##        font_size: 15
            ##        size_hint: 1, 1
            ##        shorten: True
            ##        ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}
            ##        height:15
            ##        #opacity: 0.2 if root.dimmed else 1
            #    Label:
            #        text: "[i]BPM: " + root.bpm+"[/i]" if root.bpm is not None else ""
            #        color: .6,.6,.6,1
            #        markup: True
            #        text_size: self.size
            #        halign: 'right'
            #        valigh: 'middle'
            #        font_size: 13
            #        size_hint: 1, 1
            #        shorten: True
            #        ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}
            #        height:15
            #        #opacity: 0.2 if root.dimmed else 1

"""

#class MasterQueueTrackCard(RelativeLayout):

#
 #   
 #   def add_track(self, track):
 #       pass



class MasterQueueTrackCard(ListItemBase): #LongPressButtonBehaviour, RelativeLayout, recycleview.RecycleViewMixin):
    #album_art = ObjectProperty(None)
    #album_art_file = ObjectProperty(None)
    #title     = StringProperty("")
    #artist    = StringProperty("")
    #album     = StringProperty("")
    #bpm       = StringProperty("")
    #length    = StringProperty("")
    #genre     = StringProperty("")
    #bg        = ObjectProperty(None)
    #track     = ObjectProperty(None)
    play_time = StringProperty("")
    ##show_upload_progress = BooleanProperty(False)
    #upload_progress = BooleanProperty(False)

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
        
        #for key, value in data.items():
        #    setattr(self, key, value)
        self.__initialize__(data['row'], data['item'], data['view'], data['drag_context'], data['is_selected'])
        #self.album_art = 'pydjay/gui/default_album_cover.png'

    def __initialize__(self, row = None, item = None, view = None, drag_context = None, is_selected = False, *args, **kwargs):
        super(MasterQueueTrackCard, self).__initialize__(row, item, view, drag_context, is_selected)
        #self.row = row
        #self._album_art = None
        #self._item = item.track if item is not None else None
        #self.track = item
        #self._item_data = item
        #self._window = drag_context
        #self._view = view

        #if self._item_data is not None:
        #    print self._item_data
        #    self._update_background()#None, self._item_data.is_selected)
        #    self._update_availability()#None, self._item_data.is_available)
        #    self._item_data.bind(is_selected  = self._update_background) #,
        #                         #upload_progress  = self._update_upload_progress,
        #                         #done  = self._show_upload_progress)#

        #self._show_upload_progress()
            #is_available = self._update_background)
        #print kwargs
        #$row  = kwargs['row']
        #$item = kwargs['item']
        #print row, item
        if self._item is not None:
            #self.title  = unicode(self._item.metadata.title)
            #self.artist = unicode(self._item.metadata.artist)
            #self.album  = unicode(self._item.metadata.album)
            #self.bpm    = str(self._item.metadata.bpm)
            #self.genre    = str(self._item.metadata.genre)
            #self.length = seconds_to_human_readable(int(self._item.info.length /1000000000))
            self.play_time = self._item_data.play_time
            self._item_data.bind(play_time = self._play_time_change)

            if self._item.metadata.album_cover is not None:
                try:
                    self.album_art.source = self._item.metadata.album_cover['small']
                except Exception, details:
                    print details
                    self.album_art.source = 'atlas://pydjay/gui/images/resources/default_album_cover'
                #im_type = self._item.metadata.album_cover[0]
                #im_data = self._item.metadata.album_cover[1]
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

        #self._long_press_threshold = .25
        #self.bind(on_long_press = self._start_dragging)


    """
    def _update_availability(self, *args):#win, value):
        pass


    def _show_upload_progress(self, *a):
        #print self.track.track, self.track.done
        self.show_upload_progress = not self.track.done
        
    def _update_upload_progress(self, *a):
        #print self.track.track, self.track.done
        self.upload_progress = self.track.upload_progress
    
    def _update_background(self, *value):
        #print "UPDATE BACKGROUND AVAILABILITY"
        value = self._item_data.is_selected if self._item_data is not None else False
        self.bold = value
        self.bg.canvas.clear()
        if value:
            with self.bg.canvas:
                
                if self._view.has_focus:
                    Color(0,.3,.7,1)
                else:
                    Color(0,.3,.7,.3)
                #Color(0,.3,.7,1)
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
        
        #if self._item_data is not None and not self._item_data.is_available:
        #    self.opacity = 0.1
        #else:
        #    self.opacity = 1
        self.update_album_art(33,33)

    """    
    def _play_time_change(self, obj, new_value):
        #print "PLAY TIME CHANGED", self._item_data.play_time
        self.play_time = new_value

        
    """
    def _start_dragging(self, foo, x, y):
        if self._window is not None:
            try:
                self._window.start_drag(self.to_window(x,y), self._item)
                #print "REMOVING", self._item.location, 
                #self._view._queued_tracks.discard(self._item.location)
                #print "removed from queue"
                self._view.remove_track(self._item_data)

                #print "DONE"#self._item.location
            except Exception, details:
                print details


    def _on_touch_up(self, window, event):
        if self.collide_point(*event.pos):
            if self._window is not None and self._window._drag_payload is not None:
                if event.pos[1] - self.pos[1] < self.height / 2:
                    self._view.add_track(self._window._drag_payload, self.row + 1)
                else:
                    self._view.add_track(self._window._drag_payload, self.row)
                self._window.drop()

    #def update_bg(self, *args):
    #    self.update_album_art(33,33)
        
    def update_album_art(self, w, h):
        if self._album_art is not None:
            self.album_art.texture = self._album_art.texture


    def _on_touch_down(self, window, event):
        if self.collide_point(*event.pos):
            try:
                #if event.is_double_tap:
                #    self._view.add_shortlist_track(self._item)
                #else:
                #self._view.preview_player.set_track(self._item)
                #self._item_data.is_selected = True
                self._view.select(self.row)
            except Exception, details:
                print details, self._item
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
#        print window, event
#        if self.collide_point(*event.pos):
#            print "XXX", self.title
#            return False
"""
  

Builder.load_string(kv_string_item)
Factory.register('MasterQueueTrackCard', MasterQueueTrackCard)
 
#kv_string = """
#
#<MasterQueue>:
#    list_view: list_view
#    orientation: 'vertical'
#    size_hint: 1,1
#    #deck: deck
#    #display: display
#    current_session: current_session
#    on_touch_up: self._on_touch_up(*args)
#    #
#
#    #MainPlayerDisplay:
#    #    id: display
#    #    size_hint: 1, None
#    #    height: 150
##
##    HDivider:
##    MainPlayerDeck:
##        id: deck
##        current_session_list: current_session
##        size_hint: (1, None)
##        queue: root
##        height: 100
#
##    HDivider:
#    BoxLayout:
#        orientation: 'vertical'
#        padding: [7,7,7,7]
#        size_hint: 1, None
#        height: 55
#        spacing: 4
#
#        canvas.before:
#            Color:
#                rgba: .1,.1,.1, 1
#            Rectangle:
#                pos: self.pos
#                size: self.size
#
#        #BoxLayout:
#        #    orientation: 'horizontal'
#        #    size_hint: 1, 1
#        #    #height: 55
#        Label:
#            size_hint: 1,1
#            text: "QUEUE"
#            #width: 100
#            halign: 'center'
#            valign: 'middle'
#            font_size: 18
#            #size_hint: None, None
#            #size: self.texture_size
#            text_size: self.size
#            #height:35#
#            #Widget:
#            #    size_hint: None, None
#            #    width: 20
#            #Label:
#            #    size_hint: 1,1
#            #    text: str(len(root.adapter.data))+" tracks"
#            #    color: .7,.7,.7,1
#            #    halign: 'left'
#            #    valign: 'bottom'
#            #    font_size: 25
#            #    #size_hint: None, None
#            #    #size: self.texture_size
#            #    text_size: self.size
#            ##    #height:45#
#
#            #Widget:
#            #    size_hint: 1, None
#
#        #BoxLayout:
#        #    orientation: 'horizontal'
#        #    size_hint: 1, 1
#        #    #height: 20
#        #    spacing: 10
#
#            #Label:
#            #    text: root.queue_end_time #"Queue ends at:"
#            #    #color: .6,.6,.6,1
#            #    #halign: 'right'
#            #    font_size: 20
#            #    markup: True
#            #    size_hint: 1, 1
#            #    #size: self.texture_size
#            #    text_size: self.size
#            #    valign: 'bottom'
#            #    halign: 'right'
#            #    #height:20#
#            #Label:
#            #    text: root.queue_end_time
#            #    halign: 'right'
#            #    valigh: 'bottom'
#            #    font_size: 30
#            #    size_hint: 1, None
#            #    size: self.texture_size
#            #    text_size: self.size
#            #    valign: 'bottom'
#            #    #halign: 'bottom'
#            #    #height:25#
#
#
 #       BoxLayout:
 #           orientation: 'horizontal'
 #           size_hint: 1, 1
 #           #height: 20
 #           spacing: 10
 #           Label:
 #               text: root.queue_time #"Total time:"
 #               #color: .6,.6,.6,1
 #               #halign: 'right'
 #               font_size: 15
 #               valign: 'middle'
 #               markup: True
 #               size_hint: 1, 1
 #               #size: self.texture_size
 #               text_size: self.size
 #               valign: 'bottom'
 #               halign: 'left'
 #               #height:25#
#
#            #Label:
#            #    text: root.play_time #"Total time:"
#            #    #color: .6,.6,.6,1
#            #    #halign: 'right'
#            #    font_size: 20
#            #    markup: True
#            #    size_hint: 1, 1
#            #    #size: self.texture_size
#            #    text_size: self.size
#            #    valign: 'bottom'
#             #   halign: 'left'
#             #   #height:25#
#
#            Label:
#                text: root.queue_end_time #"Queue ends at:"
#                #color: .6,.6,.6,1
#                #halign: 'right'
#                font_size: 15
#                valign: 'middle'
#                markup: True
#                size_hint: 1, 1
#                #size: self.texture_size
#                text_size: self.size
#                valign: 'bottom'
#                halign: 'right'
#                #height:20#
#            #Label:
#            #    text: root.queue_end_time
#            #    halign: 'right'
#            #    valigh: 'bottom'
#            #    font_size: 30
#            #    size_hint: 1, None
#            #    size: self.texture_size
#            #    text_size: self.size
#            #    valign: 'bottom'
#            #    #halign: 'bottom'
#            #    #height:25#
#
#
#
#
 #   HDivider:
 ##$   RelativeLayout:
 ##$       id: deck
 ##$       size_hint: (1, None)
 ##       height: 350
 ##       width: self.height * 1.4
##
##        Widget:
##            size_hint: 1,1
##            canvas.before:
##                Color:
##                    rgba: .2, .2, .2, 1
##                Rectangle:
##                    size: self.size
##                    pos:  self.pos
##
##        ImageButton:
##            size_hint: None, None
##            size: 85,41
##            pos: 0, root.height - 41
##            background_normal: "atlas://pydjay/gui/images/resources/keyboard-btn-next" #'/Users/jihemme/Python/DJ/pydjay/gui/keyboard-btn-next.png'
##            background_down:   "atlas://pydjay/gui/images/resources/keyboard-btn-next-focus" #'/Users/jihemme/Python/DJ/pydjay/gui/keyboard-btn-next-focus.png'
##            on_press: root.skip_to_next()#
#
##        MainPlayerDeck:
##            id: turntable
##            pos: 25,5##
##
#
##        #XSlider:
##        #    orientation: 'vertical'
##        #    size_hint: None, None
##        #    height:225
##3        #    width: 100
##        #    min: 0
##        #    max: 2
###        #    step: 0.01
##        #    value: 1
##        #    value_track: True
##        #    value_track_color: 1,1,1,1
##        #    pos:  self.parent.width - 160, 100
##        #    on_value: root._player.set_volume(self.value)
##        #    background_vertical: 'atlas://pydjay/gui/images/resources/volume-slider-bg'
##        #    cursor_image:'atlas://pydjay/gui/images/resources/volume-slider-knob'
##        #    #cursor_disabled_image: '/Users/jihemme/Python/DJ/pydjay/gui/volume-slider-knob.png'
##        #    #cursor_image: '/Users/jihemme/Python/DJ/pydjay/gui/volume-slider-knob.png'
##
##
# #       Label:
# #           id: stopping_message
# #           size_hint: None, None
# #           halign: 'center'
# #           size: 125,75
# #           text_size: self.size
# #           text: ''
# #           font_size: 15
# #           pos: self.parent.width - 130, 65
# #       Button:
# #           id: start_queue_button
# #           size_hint: None, None
# #           size: 125,50
# #           text: ''
# #           font_size: 30
# #           on_press: root.start_queue() #_start_play()
# #           pos: self.parent.width - 130, 10
# #   HDivider:
# #   #ScrollView:
# #   #    size_hint: 1,1
#    ListView:
#        id: list_view
#        orientation: 'vertical'
#        size_hint: 1,1
#        padding:5
#        spacing:5
#        on_touch_down: root._on_touch_down(*args)
#        #height:self.minimum_height
#    HDivider:
#    CurrentSessionList:
#        id: current_session
#        #item_class: DefaultTrackItemView
 #       size_hint: 1, .75
#
#"""

#class TrackData(EventDispatcher):
#    play_time       = StringProperty("")
#    is_selected     = BooleanProperty(False)
#    track           = ObjectProperty(None)
#    upload_progress = NumericProperty(1)
#    ready           = BooleanProperty(True)
 #   
 #   def __init__(self, track):
 #       super(TrackData, self).__init__()
 #       self.track = track


#class UploadCancelled(Exception):
#    pass

        
#class UploadTrack(EventDispatcher):
#    track    = ObjectProperty(None)
#    progress = NumericProperty(0)
#    done     = BooleanProperty(False)
#
#    def __init__(self, track, to_ip, to_port):
#        super(UploadTrack, self).__init__()
#        self._track = track
#        self._completed_callbacks = []
#        self._cancelled_callbacks = []
#        self._to_ip = to_ip
#        self._to_port = to_port
#        self._total_size = 0
#        self._uploading_thread = None
#        self._uploading = False
#
#    @mainthread
#    def _progress(self, bytes_read):
#        #print bytes_read
#        self.progress = float(bytes_read) / self._total_size
#
#    @mainthread
#    def _track_data(self, data):
#        self.track = data
#
#    @mainthread
#    def _done(self):
#        self.done = True
 #       
 #   @mainthread
 #   def completed(self, t):
 #       for x in self._completed_callbacks:
 #           try:
 #               x(self._track.track)
 #           except Exception, details:
 #               print details
 #       self._done()
#
#    @mainthread
#    def cancelled(self):
#        for x in self._cancelled_callbacks:
#            try:
#                x(self._track.track)
#            except Exception, details:
#                print details
#        #self._done()
#
#    def add_completion_callback(self, callback):
#        if callback is not None:
#            if not callback in self._completed_callbacks:
#                self._completed_callbacks.append(callback)
#
#    def remove_completion_callback(self, callback):
#        #if callback is not None:
#        if callback in self._completed_callbacks:
#            self._completed_callbacks.remove(callback)
#
#
#    def add_cancelled_callback(self, callback):
#        if callback is not None:
#            if not callback in self._cancelled_callbacks:
#                self._cancelled_callbacks.append(callback)#
#
#    def remove_cancelled_callback(self, callback):
#        #if callback is not None:
#        if callback in self._cancelled_callbacks:
#            self._cancelled_callbacks.remove(callback)
#
#
#
#    def _upload_file(self, filename, sock):
#        Logger.info('MainQueue: Uploading <%s>', filename)
#        f = open(filename, 'rb')
#        data = f.read(4096)
#        bytes_ = 0
#        while data != '' and self._uploading:
#            sock.sendall(data)
#            bytes_ += len(data)
#            self._progress(bytes_)
#            data = f.read(4096)
#        if not self._uploading:
#            print "cancelling"
#            raise UploadCancelled()    
#
#    def _upload_track_process(self):
#        if None not in [self._to_ip, self._to_port]:
#            #sock = socket.socket
#            #self._uploading = True
#            #track_data = {}
#            t = time.time()
#
#            local_file = self._track.track.location
#            album_art = None
#            if self._track.track.metadata.album_cover is not None:
#                album_art = self._track.track.metadata.album_cover['original']
#
 #           local_file_size = os.path.getsize(local_file)
 #           if album_art is not None:
 #               album_art_size  = os.path.getsize(album_art)
 #           else:
 #               album_art_size  = 0
#
#            if self._track.track.metadata.waveform  is not None:
#                waveform_size  = os.path.getsize(self._track.track.metadata.waveform)
#            else:
#                waveform_size  = 0
#
 #           self._track_data(self._track.track)#
#
#            if self._track.track.metadata.waveform is not None:
#                wf = open(self._track.track.metadata.waveform).read()
#
#            track_data = json.dumps({'title': self._track.track.metadata.title,
#                                     'artist': self._track.track.metadata.artist,
#                                     'album': self._track.track.metadata.album,
#                                     'location': self._track.track.location,
#                                     'waveform': self._track.track.metadata.waveform,
#                                     'cover': album_art})
#            track_data_length = len(track_data)
 ##           self._total_size = track_data_length + local_file_size + waveform_size + album_art_size
 #           
 #           sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 #           sock.connect((self._to_ip, self._to_port))
 #           dat = "%s:%s:%s:%s\n"%(track_data_length, album_art_size, waveform_size, local_file_size)
 #           sock.sendall(dat)
 #           sock.sendall(track_data)
 #           self._progress(len(track_data))
 #           try:
 #               if album_art is not None:
 #                   self._upload_file(album_art, sock)##
#
#                if self._track.track.metadata.waveform is not None:
#                    self._upload_file(self._track.track.metadata.waveform, sock)
 #           
 #               self._upload_file(local_file, sock)
 #               self._progress(1)
 #               self._uploading = False
 #               t2 = time.time()
 #               self.completed(t2-t)
 #           except UploadCancelled:
 #               self.cancelled()
 #               pass
 #           finally:
 #               sock.close()
  #              
   #         
    #            
    #def start(self):
    #    self._uploading = True
    #    self._uploading_thread = threading.Thread(target = self._upload_track_process)
    #    self._uploading_thread.start()

    #def cancel(self):
    #    Logger.info("MainQueue: Cancelled upload of '%s' to the remote database", self._track)
    #    self._uploading = False
    #    self._uploading_thread.join()
    #    self._uploading_thread = None

        
"""
class MasterQueue(BoxLayout):
#    remote_connection = BooleanProperty(False)
    is_connected_to   = StringProperty("")
    connected_ip      = StringProperty("")
    connected_host    = StringProperty("")
    connected_port    = NumericProperty(0) 
    list_view         = ObjectProperty(None)
    window            = ObjectProperty(None)
    track_list        = ListProperty()
    card_list         = ListProperty()
    queue_time        = StringProperty()
    play_time         = StringProperty()
    queue_end_time    = StringProperty()
    queue_changed     = BooleanProperty(False)
    uploading_track   = ObjectProperty(None)
    player            = ObjectProperty(None)
    deck            = ObjectProperty(None)
    preview_player    = ObjectProperty(None)
    

    def __init__(self, *args, **kwargs):
        super(MasterQueue, self).__init__(*args, **kwargs)
        self._queued_tracks = set([])
        self.adapter = ListAdapter(
            cls = MasterQueueTrackCard,
            data = [],
            selection_mode = 'none',
            allow_empty_selection = False,
            args_converter = self._convert
        )
        self._control_client   = None
        self._files_port       = None
        self._uploading_track  = None
        self._uploading_thread = None
        self._uploading        = False
        self._is_connected     = False
        self._play_time        = 0
        self._total_queue_time = 0
        #self.upload_manager    = TrackUploadQueue(self.adapter)
        Clock.schedule_once(self._post_init,0)
        #self.adapter.bind(data)
        #self._remote_files = {}
        #self._upload_jobs  = {}
        #self.bind(remote_connection = self._switch_to_remote_connection)


    #def disconnect_from_remote(self):
    #    #if self._control_client is not None:
    #    #self._control_client.shutdown()
    #    self._control_client = None
    #    self.connected_ip = ""
    #    self._files_port = None
    #    self.upload_manager.disconnect_from_remote()

#    def connect_to_remote(self, ip, port, abort = None):
    #def connect_to_remote(self, ip, port):
    #    #self._control_client = control_client
    #    self.connected_ip = ip
    #    self._files_port = port
    #    #self._upload_queue_head()
    #    self.upload_manager.connect_to_remote(ip, port)
    #    self._is_connected = True
    #    #for t in self.adapter.data:
    #    #    t.done = False
    #    Logger.info("MainQueue: Connected to <%s> port <%s>", ip, port)
        #self._control_client.add_command_handler(self)
        #if not self.remote_connection:
#        if self._control_client is not None:
#            self._control_client.shutdown()
#        self._control_client = ControlClient(ip_address = ip, port = port, command_listener = self)
#        self._control_client.bind(is_connected = self.set_is_connected,
#                                  is_connected_to = self.set_is_connected_to)
#        self._control_client.connect(abort)
#        self._port = port

    def show_preview_player(self, track, pos, size):
        #self.window.show_preview_player(track, pos, size)
        #self.short_list.preview_track(track)
        self.preview_player.set_track(track)
        self.preview_player.play()


    
        
    #@mainthread
    #def handle_HOST(self, name, ip, files):
    #    self.connected_host  = name
    #    self.connected_ip    = ip
    #    self._files_port     = int(files)
    #    Logger.info("MainQueue: Connected to host '%s' at '%s', file upload server at %s:%s",
    #                self.is_connected_to,
    #                self.connected_ip,
    #                self.connected_ip,
    #                self._files_port)


    #@mainthread
    #def handle_UPLOAD_COMPLETED(self, filename, time_):
    #    #filename = filename.decode('utf-8') #json.loads(filename)
    #    Logger.info("MainQueue: Upload of '%s' reported as finished by %s after %s seconds", filename, self.connected_ip, time_)
    #    #print filename, self._uploading_track.location, type(filename), type(self._uploading_track.location)
    #    #if filename == self._uploading_track._track.track.location.decode('utf-8'):
    #    Logger.info("MainQueue: Adding track data for '%s' to the remote database", self._uploading_track._track.track )
    #    t = time.time()
    #    track_data = {}
    #    track_data['location'] = self._uploading_track._track.track.location
    #    track_data['title']    = self._uploading_track._track.track.metadata.title
    #    track_data['artist']   = self._uploading_track._track.track.metadata.artist
    #    track_data['cover']    = None
    #    #track_data['waveform'] = self._uploading_track.metadata.waveform
    #    if self._uploading_track._track.track.metadata.album_cover is not None:
    #        #Logger.info("MainQueue: Uploading file '%s'", self._uploading_track.metadata.album_cover['original'])
    #        #self._upload_file(self._uploading_track.metadata.album_cover['original'])
    #        track_data['cover'] = self._uploading_track._track.track.metadata.album_cover['original']
    #    self._control_client.send_command('ADD_TRACK', json.dumps(track_data))
    #    t2 = time.time()
    #    t = t2-2
    #    #if self._uploading_track is not None: # and self._upload_complete_callback is not None:
    #    self._uploading_track.completed()
    #        #self._uploading_track = None
    #            #self._upload_complete_callback(float(time_)+t)

    #def _upload_file(self, filename):
    #    #Logger.info('MainQueue: Uploading %s to the re', filename)
    #    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #    #print (self.connected_ip, self._files_port)
    #    sock.connect((self.connected_ip, self._files_port))
    #    sock.sendall(urllib.quote(filename,"") + '\n')
    #    f = open(filename, 'rb')
    #    data = f.read(4096)
    #    while data != '' and self._uploading:
    #        #print 'read', len(data)
    #        sock.sendall(data)
    #        data = f.read(4096)
    #    #self._uploading = False
    #    f.close()
    #    sock.close()
    #    Logger.info('MainQueue: Done uploading %s', filename)

    #def _upload_track_process(self):
    #    if None not in [self.connected_ip, self._files_port]:
    #        #sock = socket.socket
    #        self._uploading = True
    #        #track_data = {}
    #        t = time.time()
    #        Logger.info("MainQueue: Uploading file '%s'", self._uploading_track._track.track.location)
    #        self._upload_file(self._uploading_track._track.track.location)
    #        if self._uploading_track._track.track.metadata.album_cover is not None:
    #            Logger.info("MainQueue: Uploading file '%s'", self._uploading_track._track.track.metadata.album_cover['original'])
    #            self._upload_file(self._uploading_track._track.track.metadata.album_cover['original'])
    #        t2 = time.time()
    #        try:
    #            self.handle_UPLOAD_COMPLETED(self._uploading_track._track.track.location, t2-t)
    #            self._uploading_thread = None
    #            self._uploading_track = None
    #            self._upload_complete_callback = None
    #        except Exception, details:
    #            print details, "FOO"
    #            #track_data['cover'] = self._uploading_track.metadata.album_cover['original']
    #        #if self._upload_complete_callback is not None:
    #        #    self._upload_complete_callback()
                
    #def _cancel_upload(self):
    #    if self._uploading_track is not None:
    #        Logger.info("MainQueue: Cancelled upload of '%s' to the remote database", self._uploading_track._track.track)
    #        self._uploading_track.remove_completion_callback(self._done_uploading)
    #        self._uploading_track.remove_completion_callback(self._upload_queue_head)
    #        self._uploading_track.cancel()
    #        self._uploading_track = None
    
    #def _upload_track(self, track):
    #    if self._uploading_track is not None:
    #        Logger.info("MainQueue: Cancelling upload of '%s' to the remote player", self._uploading_track._track.track)
    #        self._cancel_upload()
    #    #if not (self.ready or self._uploading):
    #    Logger.info("MainQueue: Uploading '%s' to the remote database", track.track)
    #    self._uploading_track = UploadTrack(track, self.connected_ip, self._files_port)
    #    self._uploading_track.add_completion_callback(self._done_uploading)
    #    self._uploading_track.start()
    #    self.uploading_track = self._uploading_track
    #    #self._uploading = True
    #    #self._uploading_thread = threading.Thread(target = self._upload_track_process)
    #    #self._uploading_thread.start()

    #def _done_uploading(self, *a):
    #    self._uploading_track = None
            
        
    #@mainthread
    #def set_is_connected(self, foo, value):
     #   self.is_connected = value
     #   #if not value:
     #   #    self._cancel_upload()
     #   #else:
     #   #    self._upload_queue_head()

    #@mainthread
    #def set_is_connected_to(self, foo, value):
    #    self.is_connected_to = value

        

    def contains(self, location):
        return location in self._queued_tracks
        
    def _post_init(self, *args):
        self.list_view.adapter = self.adapter
        #self.display.queue = self
        self.play_time = "[color=#bbbbbb]Play time:[/color] " + \
                         "[color=#ffffff]" + \
                         seconds_to_human_readable(self._play_time) + \
                         "[/color]"


        self.queue_time = "[color=#bbbbbb]Total time:[/color] " + \
                          "[color=#ffffff]" + \
                          seconds_to_human_readable(0) + \
                          "[/color]"
        current_time = time.time()
        #current_time += total_length / 1000
        self.queue_end_time = "[color=#bbbbbb]Queue ends at:[/color] " + \
                              "[color=#ffffff]" + \
                              time.strftime("%H:%M", time.localtime(current_time)) + \
                              "[/color]"  #time.ctime(current_time)

        
        #print "POST INIT", self.deck._player
        #self.deck.bind(on_queue_started = self._start_play_time_monitor,
        #               on_queue_stopped = self._stop_play_time_monitor)

        Clock.schedule_interval(self._update_queue_times, 1)
        #self.deck._player.bind(remaining_time = self._update_queue_time)
        self.update_labels()
        
        #self.bind(player = self._update_player)
        #self.deck._player = self.player

    #def _start_play_time_monitor(self, *a):
    #    Clock.schedule_interval(self._update_play_time, 1)
     #   pass

    #def _stop_play_time_monitor(self, *a):
    #    #print 'queue stopped'
    #    Clock.unschedule(self._update_play_time)
    #    pass

    ##def _update_play_time(self, *a):
     #   self._play_time += 1
     #   #self.play_time = "[color=#bbbbbb]Play time:[/color] " + \
     #   #                 "[color=#ffffff]" + \
     #   #                 seconds_to_human_readable(self._play_time) + \
     #   #                 "[/color]"



    def set_player(self, p):
        #print 'NEW PLAYER'
        self.player = p


    #def _upload_queue_head(self, *a):
    #    if self._control_client is not None:
    #        if not self.is_empty:
    #            self._upload_track(self.adapter.data[0])


        
    def dequeue(self, incomplete = None):
        self.update_labels()
        self._queued_tracks.discard(self.adapter.data[0].track.location)
        t_track = self.adapter.data.pop(0)
        #if not self._is_connected:
        #self.upload_manager.dequeue()
        #self.upload_manager
        #if self._control_client is not None:
        #    if self._uploading_track and t_track.track.location == self._uploading_track._track.track.location:
        #        self._uploading_track.add_completion_callback(self._upload_queue_head)
        #        return self._uploading_track
        #    else:
        #        self._upload_queue_head()
        #        return t_track.track
        #else:
        #    return t_track.track
            
        #self.update_labels()
        return t_track

    def remove_track(self, track):
        self._queued_tracks.discard(track.track.location)
        idx = self.adapter.data.index(track)
        self.adapter.data.remove(track)
        #self.upload_manager.remove_track(track)
        #if idx == 0:
        #    #self._cancel_upload()
        #    self._upload_queue_head()
        self.update_labels()
    
    def top(self):
        t_track = self.adapter.data[0]
        return t_track

    @property
    def is_empty(self):
        return len(self.adapter.data) == 0

    def _convert(self, row, item):
        return {'row': row, 'item': item, 'view':self, 'window':self.window}

    
    def add_track(self, track, index = None):
        new_track = DelayedTrack(track)
        #if self._is_connected:
        #new_track.done = self.upload_manager.is_available(new_track.track)
        #else:
        #    new_track.done = True
        #new_track.done = not self._is_connected
        self._queued_tracks.add(track.location)
        #self.upload_manager.add_track(new_track, index)
        if index is None:
            self.adapter.data.append(new_track)#TrackData(track))
        else:
            self.adapter.data.insert(index, new_track)#TrackData(track))
        
        #if len(self.adapter.data) == 1:
        #    if self._uploading_track is not None:
        #        #self._cancel_upload()
        #        #self._upload_queue_head()
        #        self._uploading_track.add_completion_callback(self._upload_queue_head)
        #    else:
        #        self._upload_queue_head()
        #elif len(self.adapter.data) > 1 and index == 0:
        #    if self._uploading_track is not None:
        #        #self._cancel_upload()
        #        self._upload_queue_head()
        #        self._uploading_track.add_completion_callback(self._upload_queue_head)
        #    else:
        #        self._upload_queue_head()
                
        self.update_labels()

    enqueue = add_track

    def set_track_list(self, list):
        ll = [DelayedTrack(track) for track in list]
        for t in ll:
            #t.done = self.upload_manager.is_available(t.track)
            #print t, t.done
            #self.upload_manager.add_track(t)
            self.adapter.data.append(t)
        #print self.upload_manager._upload_queue
        #print self.adapter.data

        #self.adapter.data = [x for x in ll]
        self._queued_tracks = set([track.location for track in list])
        #self._cancel_upload()
        #self._upload_queue_head()
        self.update_labels()


    def _update_queue_times(self, *a):

        pl_remaining_time = self.deck._player.remaining_time if self.deck._player is not None else 0
        total_length = 0
        for track in self.adapter.data:#track_list:
            total_length += track.track.info.length + 5000000000
        total_length = max(total_length - 5000000000, 0)
        total_length += (pl_remaining_time)
        self.queue_time = "[color=#bbbbbb]Total time:[/color] " + \
                          "[color=#ffffff]" + \
                          seconds_to_human_readable(total_length / 1000000000) + \
                          "[/color]"
        current_time = time.time()
        current_time += total_length / 1000000000
        self.queue_end_time = "[color=#bbbbbb]Queue ends at:[/color] " + \
                              "[color=#ffffff]" + \
                              time.strftime("%H:%M", time.localtime(current_time)) + \
                              "[/color]"  #time.ctime(current_time)
        #self._play_time += 1
        self.play_time = "[color=#bbbbbb]Play time:[/color] " + \
                         "[color=#ffffff]" + \
                         seconds_to_human_readable(self._play_time) + \
                         "[/color]"

    def update_labels(self):
        total_length = 0
        for track in self.adapter.data:#track_list:
            total_length += track.track.info.length + 5000000000
        total_length = max(total_length - 5000000000, 0)
        self._total_queue_time = total_length
        self._update_queue_times()
        current_time = time.time()
        for card in self.adapter.data:
            play_time = time.strftime("%H:%M", time.localtime(current_time))
            #print card, play_time
            card.play_time = play_time
            current_time += card.track.info.length / 1000000000 + 5
            


    def _on_touch_up(self, window, event):
        #print "TOUCH UP", event
        #print window, event, self._window
        #if len(self.short_list.adapter.data) == 0:
        if self.list_view.collide_point(*event.pos):
            #print 'touch up in queue short list'
            if self.is_empty or (event.pos[1] < self.list_view.height - self.list_view.container.height + self.list_view.pos[1]):
                #print 'event in right place'
                if self.window is not None and self.window._drag_payload is not None:
                    
                    self.add_track(self.window._drag_payload)
                    self.window.drop()
                    #print "dropped payload"
        #else:
        #    print event.pos


    def _on_touch_down(self, window, event):
        
        if self.list_view.collide_point(*event.pos):
            #pass
            #print 'touch down in list'
            if not event.is_mouse_scrolling:
                for data in self.adapter.data:
                    data.is_selected = False

    def shutdown(self):
        self.deck.shutdown()
        #self.upload_manager.shutdown()

Builder.load_string(kv_string)
Factory.register('MasterQueue', MasterQueue)
"""



if __name__ == '__main__':
    from kivy.base import runTouchApp
    #from mediacentre.database.TVShows import database_pickle
    from kivy.core.window import Window
    from kivy.uix.button import Button
    ## red background color
    #from jmc.gui import config

    Window.clearcolor = (0.1,0.1,0.1, 1)
    #Window.width = 350
    #Window.height = 475
    #index = 0
    #def add_item(*a):
    #    global index
    #    index += 1
    #    #print index
    #    item = Button(text= '%s'%index)
    #    bar.add_page(item)
        
    #def _foo(*a):
    #    Clock.schedule_interval(add_item, 1)
    #db = database_pickle.Database('/Users/jihemme/mediaserver_data')
    #from kivy.clock import Clock
    #foo = AnchorLayout(size_hint = (1,1), anchor_x = 'center', anchor_y = 'center')
    #init_gui()
        
    
    bar = MasterQueue()

    #fol = '/Users/jihemme/Python/DJ/test_audio'
    #for f in os.listdir(fol):
    #    f_n = os.path.join(fol, f)
    #    t_c = load_file(f_n)
    #    bar.add_track(t_c)



    bar.size = 300, 600#Builder.load_string(kv_string)#FilesScreen(size_hint = (1,1))#size = (450,550))
    #bar.location_browser.set_default_locations()
    #bar.set_list(locations)
    #add_item()
    #add_item()
    
    #add_item()
    
    #add_item()
    
    #add_item()
    #Clock.schedule_once(add_item, 5)
    #button = Button(test="FOO",size_hint = (1,1))
    #bar.set_seasons(12)
    #bar.set_episodes(123, 45)
    #foo.add_widget(bar)
    #foo.add_widget(button)
    #button.bind(on_press = lambda *x: 
    #bar.set_show(db.get_tv_show('stargate-sg-1'))#db.get_tv_shows())
    runTouchApp(bar)#size=(400,200)))#, size_hint = (None, None)))
    bar.unload()
