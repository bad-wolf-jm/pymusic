import os
import re
import time
import mimetypes

from functools import partial
from threading import Thread
from os.path import getsize
from datetime import datetime

from kivy.clock import mainthread, Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout

from kivy.properties import ObjectProperty
from kivy.factory import Factory

from kivy.uix.popup import Popup

import main_queue
#import master_list
import player_display
import pydjay.uix.clickable_area


#from pydjay.uix import screen, paged_grid, paged_display
#from pydjay.uix import clickable_area
#from pydjay.uix import long_press_button
#from pydjay.uix import screen
from kivy.animation import Animation

from pydjay.gui.main_window import MainWindow #file_browser, location_browser
from pydjay.gui.modules.track_editor import TrackEditor
from pydjay.gui.modules.preview_player import PreviewPlayer
#from mediacentre.skins.default.theme import get_path

from main_track_list import MainTrackList
from track_short_list import TrackShortList


kv_string = """
<MainScreen>:
    master_queue: master_queue
    master_list: master_list
    short_list: short_list
    precue_player: preview_player
    #main_player: main_player
    size_hint: 1,1
    current_date:""
    current_time:""

    Widget:
        canvas:
            Color:
                rgba: 0.03,0.03,0.03,1
            Rectangle:
                size:self.size
                pos:self.pos
        size_hint: 1,1 
        pos_hint: {'x': 0, 'y': 0}
        #keep_ratio: False

    BoxLayout:
        orientation: 'vertical'
        size_hint: 1,1

        BoxLayout:
            orientation: 'horizontal'
            size_hint: 1, None
            height: 150 #time_label.height+date_label.height
            padding: [0,0,0,0]
            MainPlayerDisplay:
                id: display
                size_hint: 1, 1
                height: 150
                queue: master_queue
                deck: deck

            VDivider:
            BoxLayout:
                orientation: 'vertical'
                size_hint: .5,1

                BoxLayout:
                    orientation: 'horizontal'
                    size_hint: 1, None
                    height: 30 #time_label.height+date_label.height
                    padding: [10,0,10,0]
                    Label:
                        id: time_label
                        text: root.current_date #"Monday, November 23"
                        halign: 'left'
                        valign:"middle"
                        font_size: 15
                        size_hint: 1, 1
                        width: self.texture_size[0]
                        #size: self.texture_size
                        text_size: self.size
                    Label:
                        id:date_label
                        color: .6,.6,.6,1
                        text: root.current_time 
                        halign: 'right'
                        valign: "middle" 
                        font_size: 15
                        size_hint: 1, 1
                        #width:200
                        size: self.texture_size
                        text_size: self.size
                        #height:15#           

                HDivider:

                MainPlayerDeck:
                    id: deck
                    #current_session_list: current_session
                    size_hint: (1, 1)
                    queue: master_queue
                    window: root
                    current_session_list: master_queue.current_session
                    height: 150

            VDivider:
            PreviewPlayer:
                id: preview_player
                size_hint: 1, 1
                height: 150 
        HDivider:

        BoxLayout:
            orientation: 'horizontal'
            BoxLayout:
                orientation: 'horizontal'
                MainTrackList:
                    id: master_list
                    window: root
                    queue: master_queue
                    short_list: short_list
                    main_player: deck
                    preview_player: preview_player
                    size_hint: (1.0, 1.0)
                    #text: "Browser goes here"
                VDivider:
                TrackShortList:
                    #orientation: 'vertical'
                    size_hint: .5, 1
                    id: short_list
                    window:root
                    queue: master_queue
                    preview_player: preview_player
                    main_player: deck

            VDivider:
            MasterQueue:
                window:root
                preview_player: master_list.short_list.preview_player
                id: master_queue
                short_list: short_list
                preview_player: preview_player
                deck: deck
                size_hint: (.32, 1.0)
                #text: "Queue goes here"
       
"""

from pydjay.core.keyboard import key_map

class MainScreen(MainWindow):
    def __init__(self, main_player, preview_player, volume_control, *args, **kwargs):
        super(MainScreen, self).__init__(*args, **kwargs)
        self.m_p = main_player
        #self.preview_player = PreviewPlayer(preview_player, volume_control,  self)
        #self.preview_player.size_hint = (None, None)
        #self.preview_player.size = (950, 375)
        Clock.schedule_once(self._post_init, -1)
        Clock.schedule_interval(self._update_time, 1)
        self._preview_player_visible = False
        self._anim = None
        self._volume_control = volume_control
        self._preview_player = preview_player

        key_map.bind(on_edit_track = self._show_track_editor)
        self._focusable_elements = []


        
    def _post_init(self, *args):
        #self.preview_player.queue = self.master_queue
        #self.preview_player.short_list = self.master_list.short_list
        #self.preview_player.window = self
        self.master_queue.deck.connect_player(self.m_p)
        self.master_queue.deck.set_volume_control(self._volume_control)
        popup = TrackEditor(self._preview_player, self._volume_control, self)
        popup.bind(on_dismiss = self.restore_focus)
        popup.size_hint = (None, None)
        popup.size = [1300,650]
        popup.queue = self.master_queue
        popup.short_list = self.short_list
        popup.window = self
        #popup.set_track(track)
        #popup.open()
        self.preview_popup = popup
        self._focus = 0
        self._focusable_elements = [self.master_list,
                                    self.short_list,
                                    self.master_queue]

        self.master_list.focus()



    def request_focus(self, w):
        try:
            i = self._focusable_elements.index(w)
        except ValueError:
            i = None
        if i is not None:
            self._focusable_elements[self._focus].unfocus()
            self._focus = i
            self._focusable_elements[self._focus].focus()
        
    def cycle_focus(self, _, i):
        self._focusable_elements[self._focus].unfocus()
        self._focus = (self._focus + i) % len(self._focusable_elements)
        self._focusable_elements[self._focus].focus()
        
    def restore_focus(self, *a):
        self._focusable_elements[self._focus].focus()

    def suspend_focus(self):
        self._focusable_elements[self._focus].unfocus()
        
        
    def _update_time(self, *args):
        #t = time.localtime()
        self.current_date = time.strftime('%a, %b %d %Y')
        self.current_time = time.strftime('%H:%M:%S')


    def _show_track_editor(self, *a):
        t = self._preview_player._track
        if t is not None:
            self.show_preview_player(t, 0,0)
        
    def show_preview_player(self, track, pos, size, rel = 'right'):
        """
        x,y      = pos
        w, h     = size
        player_w, player_h = self.preview_player.size
        window_w, window_h = self.size


        if rel == 'right':
            # check the left
            if x+w+player_w <= window_w-5:
                player_x = x+w+5
            else:
                # check the right
                if x-player_w-5 >= 0:
                    player_x = x-player_w-5
                else:
                    # check the middle
                    if x + w/2 + (player_w / 2) <= window_w:
                        player_x = x + w/2 + (player_w / 2)
                    else:
                        player_x = max(x,0)

            # try to center the y coordinate
            if (y + h/2 + player_h / 2 <= window_h) and (y + h/2 - player_h/2 >= 0):
                player_y = y + w/2 - player_h / 2
            else:
                #if :
                #    player_y = y+h - player_h / 2
                #else:
                player_y = max(y, 0)
        elif rel == 'left':
            if x-player_w-5 >= 0:
                player_x = x-player_w-5

            else:
                # check the right
                if x+w+player_w <= window_w-5:
                    player_x = x+w+5
                else:
                    # check the middle
                    if x + w/2 + (player_w / 2) <= window_w:
                        player_x = x + w/2 + (player_w / 2)
                    else:
                        player_x = max(x,0)

            # try to center the y coordinate
            if (y + h/2 + player_h / 2 <= window_h) and (y + h/2 - player_h/2 >= 0):
                player_y = y + w/2 - player_h / 2
            else:
                #if :
                #    player_y = y+h - player_h / 2
                #else:
                player_y = max(y, 0)

            pass
        

        
        self.preview_player.set_track(track)
        if not self._preview_player_visible:
            self.add_widget(self.preview_player)
            self._preview_player_visible = True
            self.preview_player.pos = (player_x, player_y)
        else:
            if self._anim is not None:
                self._anim.cancel(self.preview_player)
            self._anim = Animation(pos=(player_x,player_y), duration=.2)
            self._anim.start(self.preview_player)
            self._anim.bind(on_complete = self._completed_animation)
            #self.preview_player.pos =
"""

        def _foo(*a):
            #popup = PreviewPlayer(self._preview_player, self._volume_control, self)
            #popup.size_hint = (None, None)
            #popup.size = [1300,650]
            #popup.queue = self.master_queue
            #popup.short_list = self.master_list.short_list
            #popup.window = self
            self.preview_popup.set_track(track)
            self.preview_popup.open()
            #self.cancel_drag()
        Clock.schedule_once(_foo, 0)

    def _completed_animation(self, *args):
        #self._anim.unbind(self._completed_animation)
        self._anim = None

    def dismiss_preview_player(self):
        if self._preview_player_visible:
            self.remove_widget(self.preview_player)
            self._preview_player_visible = False
            self.preview_player.stop()
            #self.preview_player.pos = (x,y)

        
    
    def shutdown(self):
        #self.main_player.shutdown()
        self.master_queue.shutdown()

        pass


Builder.load_string(kv_string)

