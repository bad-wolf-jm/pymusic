import os
import re
import mimetypes

from functools import partial
from threading import Thread
from os.path import getsize
from datetime import datetime

from kivy.event import EventDispatcher
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


#from kivy.properties import ObjectProperty
from kivy.factory import Factory

from pydjay.library.track import load_file
from pydjay.library import get_folders, get_master_playlist, get_playlists, get_sessions, get_session_by_name

from pydjay.gui.utils import seconds_to_human_readable
from pydjay.uix.clickable_area import ImageButton
from pydjay.uix.long_press_button import LongPressButtonBehaviour

#from pydjay.gui.preview_player import PreviewPlayer

from kivy.graphics import *

#from pydjay.uix import screen, paged_grid, paged_display
#from pydjay.uix import clickable_area
#from pydjay.uix import long_press_button
#from pydjay.uix import screen

#from pydjay.gui.files_screen import file_browser, location_browser
#from mediacentre.skins.default.theme import get_path

#from pydjay.gui.master_list.list_item import MasterListTrackItem
#from pydjay.gui.master_list.shortlist_item import MasterListShortlistItem
#from pydjay.gui.master_list.sidetree_items import FolderLabel, PlaylistLabel, SessionLabel
from pydjay.gui.main_window import MainWindow
from pydjay.gui.list_items.drag_item import DragItem
#from pydjay.gui.simple_detailed_list_item import SimpleDetailedListItem
#from pydjay.gui.track_list import TrackList
#from pydjay.uix.side_panel import NavigationDrawer

from pydjay.gui.utils import seconds_to_human_readable








kv_string = """
#:import label kivy.uix.label
#:import sla kivy.adapters.simplelistadapter
#:import DefaultTrackItemView pydjay.gui.list_items.default_track_list_item.DefaultTrackItemView
<CurrentSessionList>:
    orientation: 'horizontal'
    size_hint: 1,1
    #master_list: master_list
    short_list: short_list
    sl_track_count:sl_track_count
    button_size: 45
    BoxLayout:
        orientation: 'vertical'
        size_hint: 1, 1
        BoxLayout:
            orientation: 'horizontal'
            size_hint: 1, None
            height:25
            padding: [10,0,10,0]
            Label:
                text: "CURRENT SESSION"
                halign: 'left'
                valign: 'middle'
                font_size: 15
                bold: True
                size_hint: 1, 1
                text_size: self.size
                height:30#

            Label:
                id: sl_track_count
                size_hint: 1, 1
                markup:True
                text: ""
                bold: True
                halign: 'right'
                valign: "middle"
                text_size: self.size
                font_size: 15
                #size_hint: None, None
                #size: self.texture_size
                height:30#


        HDivider:
       
        TrackList: #ScrollView:
            id: short_list
            size_hint: 1,1
            item_class: DefaultTrackItemView
            item_convert: root._convert_sl
            on_touch_up: root._on_touch_up(*args)
            on_touch_down: root._on_list_touch_down(*args)
"""

class DragContext:
    def __init__(self, drag, drop):
        self.drag = drag
        self.drop = drop


class CurrentSessionList(BoxLayout):
    master_list = ObjectProperty(None)
    tree_view   = ObjectProperty(None)
    short_list  = ObjectProperty(None)
    queue       = ObjectProperty(None)
    window      = ObjectProperty(None)
    main_player = ObjectProperty(None)
    search_filter = ObjectProperty(None)
    total_track_count = StringProperty("")
    title = StringProperty("")
    
    def __init__(self, *args, **kwargs):
        super(CurrentSessionList, self).__init__(*args, **kwargs)
        Clock.schedule_once(self._post_init,-1)
        self.drag_context_sl = DragContext(self._start_drag_sl, self._drop_sl)

    def _post_init(self, *args):
        self.short_list.adapter.bind(data = self._update_sl_track_count)
        self.short_list.bind(adapter = self._update_sl_track_count)
        #self.queue.adapter.bind(data = self._update_availability)

    def _update_availability(self, *args):
        self.short_list.update_availability(self._track_is_available)

    def show_preview_player(self, track, pos, size):
        self.window.show_preview_player(track, pos, size, 'left')
        
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

    def _track_is_available(self, track):
        try:
            is_available = True
            if self.queue is not None:
                is_available = is_available and not self.queue.contains(track.location)
            if self.main_player is not None:
                is_available = is_available and not self.main_player.has_played(track.location) #or  self.main_player.has_played(x.location)
            return is_available
        except Exception, details:
            print details
            return True
    
    def _on_touch_up(self, window, event):
        if self.short_list.list_view.collide_point(*event.pos):
            if len(self.short_list.adapter.data) == 0 or \
               (event.pos[1] < self.short_list.list_view.height - self.short_list.list_view.container.height + self.short_list.list_view.pos[1]):
                if self.window is not None and self.window._drag_payload is not None:
                    self.add_shortlist_track(self.window._drag_payload)
                    self.window.drop()

    def add_track(self, track, index = None):
        self.short_list.add_track(track, index, self._track_is_available)
            
    def enqueue_track(self, track_data):
        self.queue.enqueue(track_data.track)
        self.shortlist_adapter.data.remove(track_data)

    def _convert_sl(self, row, item):
        return {'row': row, 'item': item, 'view':self, 'drag_context':self.drag_context_sl}

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
        if self.short_list.collide_point(*event.pos):
            if not event.is_mouse_scrolling:
                for data in self.short_list.adapter.data:
                    data.is_selected = False

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
Factory.register('CurrentSessionList', CurrentSessionList)





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
