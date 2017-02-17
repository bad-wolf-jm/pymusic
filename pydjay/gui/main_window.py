import os
import re
import mimetypes

from functools import partial
from threading import Thread
from os.path import getsize
from datetime import datetime


from kivy.core.window import Window
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


from kivy.properties import ObjectProperty
from kivy.factory import Factory

from pydjay.library.track import load_file
from pydjay.library import get_folders, get_master_playlist, get_playlists, get_sessions, get_session_by_name

from pydjay.gui.utils import seconds_to_human_readable
from pydjay.uix.clickable_area import ImageButton
from pydjay.uix.long_press_button import LongPressButtonBehaviour

#from pydjay.gui.preview_player import PreviewPlayer
from pydjay.gui.list_items.drag_item import DragItem


from kivy.graphics import *

win_str = """
<MainWindow>
    #list:list
    on_touch_move: self._on_touch_move(*args)
    on_touch_up: self._on_touch_up(*args)
    on_touch_down: self._on_touch_down(*args)
    #MasterList:
    #    id: list
    #    size_hint: 1,1
    #    window:root
"""

Builder.load_string(win_str)


class MainWindow(FloatLayout):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self._is_dragging = False
        self._drag_item = None
        self._drag_payload = None
        #Window.bind(on_keyboard = self._on_key_pressed_internal)
        #self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        #self._keyboard.bind(on_key_down = self._on_keyboard_down)

    #def _keyboard_closed(self):
    #    self._keyboard.unbind(on_key_down = self._on_keyboard_down)
    #    self._keyboard = None
    #    print 'Closed'

    #def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
    #    print str(keyboard)+' '+str(keycode[1])+' '+str(text)+' '+str(modifiers)
    #    #if keycode[1] == 'w':
    #    #    self.moveable.y += 1
    #
    #        if keycode[1] == 's':
    #            self.moveable.y -= 1
    #
    #        if keycode[1] == 'd':
    #            self.moveable.x += 1
    #
    #        if keycode[1] == 'a':
    #            self.moveable.x -= 1 

    #def _on_key_pressed_internal(self, w, key, scancode, codepoint, modifier):
    #    print w, key, scancode, codepoint, modifier


    def _on_touch_move(self, window, event):
        if self._is_dragging and self._drag_item is not None:
            #print "DRAGGING", self._is_dragging
            self._drag_item.center_x = event.pos[0]
            self._drag_item.center_y = event.pos[1]
            return True


    def _delete_all_drag_items(self):
        foo = []
        for x in self.children:
            if isinstance(x, DragItem):
                foo.append(x)
        for y in foo:
            self.remove_widget(y)        

    def drop(self):
        #self._is_dragging = False
        self._drag_item = None
        self._drag_payload = None
        #print "DROP"
        
    def _on_touch_up(self, window, event):
        #if self._drag_item is not None:
        #    self.remove_widget(self._drag_item)
            #self._is_dragging = False
            #return True

        #if self._drag_item is not None:
            #self.remove_widget(self._drag_item)
        self._is_dragging = False
        #return True
        self._delete_all_drag_items()
        #print [type(x) for x in self.children]
        
    def _on_touch_down(self, window, event):
        self._drag_payload = None
        self._delete_all_drag_items()
        #if self._drag_item is not None:
        #    self.remove_widget(self._drag_item)
#            #self._is_dragging = False
#            return True
    
    def start_drag(self, pos, track):
        #print "Start Drag"
        if not self._is_dragging:
            foo = DragItem(track)
            self._drag_payload = track
            self._drag_item = foo
            self.add_widget(foo)
            self._drag_item.center_x = pos[0]
            self._drag_item.center_y = pos[1]
            #Clock.schedule_once(partial(self._position_drag_widget, pos), 0)
            #self._drag_item.center_x = pos[0]
            #self._drag_item.center_y = pos[1]

            self._is_dragging = True
            
    #def _position_drag_widget(self, pos, *a):
    #    if self._drag_item is not None:
