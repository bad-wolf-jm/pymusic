import os
#import re
#import mimetypes

#from functools import partial
#from threading import Thread
from os.path import getsize
from datetime import datetime

from kivy.event import EventDispatcher
from kivy.clock import mainthread, Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
#from kivy.uix.floatlayout import FloatLayout
#from kivy.uix.relativelayout import RelativeLayout
#from kivy.uix.selectableview import SelectableView
#from kivy.uix.treeview import TreeViewNode
#from kivy.adapters.simplelistadapter import SimpleListAdapter
#from kivy.adapters.listadapter import ListAdapter


#from kivy.properties import ObjectProperty
from kivy.factory import Factory

from pydjay.library.track import load_file
#from pydjay.library import get_folders, get_master_playlist, get_playlists, get_sessions, get_session_by_name

from pydjay.gui.utils import seconds_to_human_readable
from pydjay.uix.clickable_area import ImageButton
from pydjay.uix.long_press_button import LongPressButtonBehaviour

#from pydjay.gui.preview_player import PreviewPlayer

#from kivy.graphics import *

#from pydjay.uix import screen, paged_grid, paged_display
#from pydjay.uix import clickable_area
#from pydjay.uix import long_press_button
#from pydjay.uix import screen

#from pydjay.gui.files_screen import file_browser, location_browser
#from mediacentre.skins.default.theme import get_path

#from pydjay.gui.master_list.list_item import MasterListTrackItem
#from pydjay.gui.master_list.shortlist_item import MasterListShortlistItem
#from pydjay.gui.master_list.sidetree_items import FolderLabel, PlaylistLabel, SessionLabel
#from pydjay.gui.main_window import MainWindow
#from pydjay.gui.list_items.drag_item import DragItem
from pydjay.gui.list_items.simple_detailed_list_item import SimpleDetailedListItem
#from pydjay.gui.track_list import TrackList
#from pydjay.gui.preview_player import PreviewPlayer
#from pydjay.uix.side_panel import NavigationDrawer

from pydjay.gui.utils import seconds_to_human_readable



from kivy.core.window import Window


#import pydjay.core_logic.keyboard
from pydjay.gui import large_track_list
from track_list_behaviour import TrackListBehaviour


kv_string = """
#:import label kivy.uix.label
#:import sla kivy.adapters.simplelistadapter
#:import SimpleDetailedListItem pydjay.gui.list_items.simple_detailed_list_item.SimpleDetailedListItem
#:import SimpleTrackCardItem pydjay.gui.list_items.simple_track_card_item.SimpleTrackCardItem
<TrackShortList>:
    orientation: 'horizontal'
    size_hint: 1,1
    #master_list: master_list
    #preview_player: preview_player
    short_list: short_list
    sl_track_count:sl_track_count
    button_size: 45
    BoxLayout:
        orientation: 'vertical'
        size_hint: .30, 1
        BoxLayout:
            orientation: 'vertical'
            size_hint: 1, None
            height:55
            padding: [10,0,10,0]

            canvas.before:
                Color: 
                    rgba: (.3, .3, .3, 1) if root.has_focus else (0.1, 0.1, 0.1, 1)
                Rectangle:
                    pos: self.pos
                    size: self.size

            Label:
                text: "SHORT LIST"
                halign: 'center'
                valign: 'bottom'
                font_size: 18
                bold: True
                size_hint: 1, None
                text_size: self.size
                height:30#

            Label:
                id: sl_track_count
                size_hint: 1, 1
                markup:True
                text: ""
                bold: True
                halign: 'center'
                valign: "top"
                text_size: self.size
                font_size: 15
                #size_hint: None, None
                #size: self.texture_size
                height:30#


        #HDivider:
       
        LargeTrackList: #ScrollView:
            id: short_list
            size_hint: 1,1
            item_class: SimpleTrackCardItem
            item_convert: root._convert_sl
            on_touch_up: root._on_touch_up(*args)
            on_touch_down: root._on_list_touch_down(*args)

        #HDivider:
        #PreviewPlayer:
        #    id: preview_player
        #    size_hint: 1, None
        #    height: 150 
"""

class DragContext:
    def __init__(self, drag, drop):
        self.drag = drag
        self.drop = drop


class TrackShortList(BoxLayout, TrackListBehaviour):
    #has_focus       =  BooleanProperty(False)
    master_list = ObjectProperty(None)
    tree_view   = ObjectProperty(None)
    short_list  = ObjectProperty(None)
    #queue       = ObjectProperty(None)
    #window      = ObjectProperty(None)
    main_player = ObjectProperty(None)
    preview_player = ObjectProperty(None)
    search_filter = ObjectProperty(None)
    total_track_count = StringProperty("")
    title = StringProperty("")
    
    def __init__(self, *args, **kwargs):
        super(TrackShortList, self).__init__(*args, **kwargs)
        Clock.schedule_once(self._post_init,-1)
        self.drag_context_sl = DragContext(self._start_drag_sl, self._drop_sl)
        self.has_focus = False
        self._current_selection = None
        self.set_keyboard_handlers({'shift+up': self._move_selection_up,
                                    'shift+down': self._move_selection_down,
                                    'shift+t': self._move_selection_to_top,
                                    'shift+backspace': self._delete_selection,
                                    'shift+q': self._add_selection_to_queue})

        
    def _post_init(self, *args):
        self.short_list.adapter.bind(data = self._update_sl_track_count)
        self.short_list.bind(adapter = self._update_sl_track_count)
        self.queue.queue_view.adapter.bind(data = self._update_availability)
        self.main_player.bind(on_unavailable_added = self._update_availability)
        self.preview_player.window = self.window
        self.preview_player.player = self.window._preview_player
        self.preview_player.volume_controls = self.window._volume_control
        self.adapter = self.short_list.adapter
        self.list_view = self.short_list.list_view
        self.list_view.layout_manager.default_size = 60
        #self.preview_player.player = self.window._

    def _update_availability(self, *args):
        self.short_list.update_availability(self._track_is_available)

    def show_preview_player(self, track, pos, size):
        self.window.show_preview_player(track, pos, size, 'left')


    def preview_track(self, track):
        #self.preview_player.set_track(track)
        self.preview_player.play(track)
        #self.window.preview_track(track)



    #def focus(self):
    #    self.has_focus = True
    #    self._keyboard = Window.request_keyboard(self._keyboard_closed, self, 'text')
    #    self._keyboard.bind(on_key_down = self._on_keyboard_down)
    #    if self._current_selection is not None:
    #        row = self._current_selection
    #        row = max(min(row, len(self.short_list.adapter.data) - 1), 0)
    #        try:
    #            v = self.short_list.adapter.get_view(self._current_selection)
    #            if v is not None:
    #                v._update_background()
    #            self._current_selection = row
    #        except IndexError:
    #            self._current_selection = None
            
    #def unfocus(self):
    #    self.has_focus = False
    #    if self._keyboard is not None:
    #        self._keyboard.release()
    #    if self._current_selection is not None:
    #        row = self._current_selection
    #        row = max(min(row, len(self.short_list.adapter.data) - 1), 0)
    #        row = self._current_selection
    #        row = max(min(row, len(self.short_list.adapter.data) - 1), 0)
    #        try:
    #            v = self.short_list.adapter.get_view(self._current_selection)
    #            if v is not None:
    #                v._update_background()
    #            self._current_selection = row
    #        except IndexError:
    #            self._current_selection = None
#
##            #self.short_list.adapter.get_view(self._current_selection)._update_background()
            #self._current_selection = row

#    def _keyboard_closed(self):
#        #print('My keyboard have been closed!')
#        self._keyboard.unbind(on_key_down = self._on_keyboard_down)
#        self._keyboard = None

#    @property
#    def current_selection(self):
#        if self._current_selection is not None:
#            try:
#                return self.short_list.adapter.data[self._current_selection]
#            except:
#                return None
#        return None

#    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
#        #print('The key', keycode, 'have been pressed')
#        #print(' - text is %r' % text)
#        #print(' - modifiers are %r' % modifiers)
#        key_seq = "+".join(modifiers+[keycode[1]])
#        #print key_seq
#        if key_seq == 'down':
#            if self._current_selection is not None:
#                #if self._current_selection < len(self.short_list.adapter.data) - 1:
#                self.select(self._current_selection + 1)
#            else:
#                self.select(0)
#        elif key_seq == 'up':
#            if self._current_selection is not None:
#                #if self._current_selection > 0:
#                self.select(self._current_selection - 1)
#                #else:
#                #    self.select(None)
#            else:
#                self.select(0)
#        elif key_seq == 'shift+u':
#            #self.main_player.add_unavailable()
#            #if self._current_selection is not None:
#            item = self.current_selection #short_list.adapter.data[self._current_selection]
#            if item is not None:
#                self.main_player.add_unavailable(item.track.location)#
#
#        elif key_seq == 'shift+a':
#            #self.main_player.add_unavailable()
#            #if self._current_selection is not None:
#            item = self.current_selection #short_list.adapter.data[self._current_selection]
#            if item is not None:
#                self.main_player.remove_unavailable(item.track.location)
#                #self.add_shortlist_track(item.track, self._current_selection - 1)
#                #self.select(self._current_selection - 1)

    def _move_selection_up(self):
        #print self._current_selection
        #if self._current_selection is not None:
        item = self.current_selection #short_list.adapter.data[self._current_selection]
        if item is not None:
            self.short_list.remove_track(item['item'])
            self.add_shortlist_track(item['item'].track, self._current_selection - 1)
            self.select(self._current_selection - 1)

    def _move_selection_down(self):
        #print self._current_selection
        #if self._current_selection is not None:
        item = self.current_selection #short_list.adapter.data[self._current_selection]
        if item is not None:
            self.short_list.remove_track(item['item'])
            self.add_shortlist_track(item['item'].track, self._current_selection + 1)
            self.select(self._current_selection + 1)

            #        elif key_seq == 'shift+t':
    def _move_selection_to_top(self):
        #print self._current_selection
        #if self._current_selection is not None:
        item = self.current_selection #short_list.adapter.data[self._current_selection]
        if item is not None:
            self.short_list.remove_track(item['item'])
            self.add_shortlist_track(item['item'].track, 0)
            self.select(self._current_selection)

            #        elif key_seq == 'shift+backspace':
    def _delete_selection(self):
        #if self._current_selection is not None:
        item = self.current_selection #short_list.adapter.data[self._current_selection]
        if item is not None:
            self.short_list.remove_track(item['item'])
            #self.add_shortlist_track(item.track, 0)
            self.select(self._current_selection)

            #        elif key_seq == 'shift+q':
    def _add_selection_to_queue(self):
        #if self._current_selection is not None:
        item = self.current_selection #short_list.adapter.data[self._current_selection]
        if item is not None:
            self.short_list.remove_track(item['item'])
            self.queue.add_track(item['item'].track)

                
#        elif key_seq == 'enter':
#            #if self._current_selection is not None:
#            item = self.short_list.adapter.data[self._current_selection]
#            if item is not None:
#                self.preview_player.play(item.track)
#        else:
#            pydjay.core_logic.keyboard.key_map.key_pressed(keycode, modifiers)
#        pass
#
#        # Keycode is composed of an integer + a string
#        # If we hit escape, release the keyboard
#        #if keycode[1] == 'escape':
#        #    keyboard.release()##
#
#        # Return True to accept the key. Otherwise, it will be used by
#        # the system.
#        return True


        
#    def _toggle_keyboard_shortcuts(self, *a):
#        #print self.search_filter.focus
#        if not self.search_filter.focus:
#            if self.has_focus:
#                self.focus()
#            #pydjay.core.keyboard.enable_keyboard_shortcuts()
#        else:
#            pass
#            #pydjay.core.keyboard.disable_keyboard_shortcuts()


        
    def _start_drag(self, coords, item):
        self.window.start_drag(coords, item)

    def _start_drag_sl(self, coords, item):
        if self.window is not None:
            try:
                self.window.start_drag(coords, item.track)
                self.short_list.remove_track(item)
            except Exception, details:
                print details

    def _drop_sl(self, row):
        if self.window is not None and self.window._drag_payload is not None:
            self.add_shortlist_track(self.window._drag_payload, row)
            self.window.drop()

    def do_filter(self, window, text):
        self.master_list.do_filter(text) #self._unfiltered_list

    #def _track_is_available(self, track):
    #    try:
    #        is_available = True
    #        if self.queue is not None:
    #            is_available = is_available and not self.queue.contains(track.location)
    #        if self.main_player is not None:
    #            is_available = is_available and not self.main_player.has_played(track.location) #or  self.main_player.has_played(x.location)
    #        return is_available
    #    except Exception, details:
    #        print details
    #        return True
    
    def _on_touch_up(self, window, event):
        if self.short_list.list_view.collide_point(*event.pos):
            if len(self.short_list.adapter.data) == 0 or \
               (event.pos[1] < self.short_list.list_view.height - self.short_list.list_view.container.height + self.short_list.list_view.pos[1]):
                if self.window is not None and self.window._drag_payload is not None:
                    self.add_shortlist_track(self.window._drag_payload)
                    self.window.drop()

    def add_shortlist_track(self, track, index = None):
        self.short_list.add_track(track, index, self._track_is_available)
            
    #def enqueue_track(self, track_data):
    #    self.queue.enqueue(track_data.track)
    #    self.shortlist_adapter.data.remove(track_data)

    def _convert_sl(self, row, item):
        #print {'row': row,
        #        'item': item,
        #        'view':self,
        #        'drag_context':self.drag_context_sl,
        #        'is_selected': False}
        return {'row': row,
                'item': item,
                'view':self,
                'drag_context':self.drag_context_sl,
                'is_selected': False}

    def _update_sl_track_count(self, *args):
        num = len(self.short_list.adapter.data)
        time = 0

        track_count_text = self.title
        if num > 0 and track_count_text != "":
            track_count_text += " - " 
        #else:
        for t in self.short_list.adapter.data:
            try:
                time += t.track.info.length
            except:
                pass
        track_count_text += "[color=#ffffff]" + str(num) + " tracks " + "[/color]" + \
                            "[color=#444444] | [/color]"+ \
                            "[color=#888888]" + seconds_to_human_readable(time / 1000000000) + "[/color]"
        self.sl_track_count.text = track_count_text
        return True

    def _on_list_touch_down(self, window, event):
        pass
        #if self.short_list.collide_point(*event.pos):
        #    if not event.is_mouse_scrolling:
        #        for data in self.short_list.adapter.data:
        #            data.is_selected = False


    #def select(self, row):
    #    #print self._current_selection
    #    if len(self.short_list.adapter.data) == 0:
    #        self._current_selection = None
    #        return 
     #   
     #   row = max(min(row, len(self.short_list.adapter.data) - 1), 0)
     #   if self._current_selection is not None:
     #       try:
     #           item = self.short_list.adapter.data[self._current_selection]
     #           item.is_selected = False
     #       except IndexError:
     #           pass
      #      
      #      #self.master_list.adapter.get_view(self._current_selection)._update_background()
      #  try:
      #      item = self.short_list.adapter.data[row]
      #      #self.short_list.list_view.layout_manager.show_index_view(row)
      #      item.is_selected = True
      #      #self.master_list.adapter.get_view(row)._update_background()
      #      self._current_selection = row
      #      self.window.request_focus(self)
      #  except IndexError:
      #      self._current_selection = None
            
    def set_track_list(self, list, sort = True):
        self.short_list.set_track_list(list, sort, self._track_is_available)
        self._update_sl_track_count()
        num = len(self.short_list.adapter.data)
        time = 0
        if num == 0:
            self.total_track_count = ""
        else:
            for t in self.short_list.adapter.data:
                try:
                    time += t.track.info.length
                except:
                    pass
                #[color=#<color>][/color]
            self.total_track_count = "[color=#ffffff]" + str(num) + " tracks " + "[/color]" + \
                                     "[color=#444444] | [/color]"+ \
                                     "[color=#888888]" + seconds_to_human_readable(time / 1000) + "[/color]"

        
Builder.load_string(kv_string)
Factory.register('TrackShortList', TrackShortList)





if __name__ == '__main__':
    from kivy.base import runTouchApp
    #from mediacentre.database.TVShows import database_pickle
    from kivy.core.window import Window
    from kivy.clock import Clock
    from kivy.uix.button import Button


    #from pydjay.library import init
    ## red background color
    #from jmc.gui import config
    #print(kivy.__version__)
    Window.clearcolor = (0,0,0, 1)
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
    #init("/Users/jihemme/.pydjay")
    
    foo = TrackShortList()
    bar = MainWindow()#Builder.load_string(kv_string)#FilesScreen(size_hint = (1,1))#size = (450,550))
    #print "FOO", bar.adapter
    bar.add_widget(foo)
    foo.window = bar

    #foo.master_list. = bar.list.adapter
    #foo.master_list.window = bar

    ll = []
    root = os.path.abspath(os.path.expanduser('~/Dropbox/DJ/test_audio'))
    for xx in os.listdir(root):
        yy = os.path.join(root, xx)
        zz = load_file(yy)
        if zz is not None:
            ll.append(zz)


    
    foo.set_track_list(ll)#range(15000)
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
