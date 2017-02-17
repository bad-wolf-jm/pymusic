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
from pydjay.library import get_folders, get_master_playlist, get_playlists, get_sessions, get_session_by_name, get_filters

from pydjay.gui.utils import seconds_to_human_readable
from pydjay.uix.clickable_area import ImageButton
from pydjay.uix.long_press_button import LongPressButtonBehaviour

#from pydjay.gui.preview_player import PreviewPlayer

from kivy.graphics import *

#from pydjay.uix import screen, paged_grid, paged_display
#from pydjay.uix import clickable_area
#from pydjay.uix import long_press_button
from pydjay.uix import widgets

#from pydjay.gui.files_screen import file_browser, location_browser
#from mediacentre.skins.default.theme import get_path

#from pydjay.gui.master_list.list_item import MasterListTrackItem
#from pydjay.gui.master_list.shortlist_item import MasterListShortlistItem
from pydjay.gui.main_window import MainWindow
from pydjay.gui.list_items.drag_item import DragItem
from pydjay.gui.list_items.simple_detailed_list_item import SimpleDetailedListItem
from pydjay.gui.track_list import TrackList
#from pydjay.uix.side_panel import NavigationDrawer

from pydjay.gui.utils import seconds_to_human_readable


from pydjay.gui import large_track_list
#import pydjay.core_logic.keyboard
#from kivy.core.window import Window

#from track_short_list import TrackShortList
#from sidetree_items import PlaylistItem, SessionItem
from track_list_behaviour import TrackListBehaviour


kv_string = """
#:import label kivy.uix.label
#:import sla kivy.adapters.simplelistadapter
#:import SimpleDetailedListItem pydjay.gui.list_items.simple_detailed_list_item.SimpleDetailedListItem
#:import SimpleTrackCardItem pydjay.gui.list_items.simple_track_card_item.SimpleTrackCardItem
<MainTrackList>:
    orientation: 'horizontal'
    size_hint: 1,1
    master_list: master_list
    #tree_view:tree_view
    #short_list: short_list
    search_filter:search_filter
    track_count:track_count
    button_size: 45
    #side_view: side_view

    StencilView:
        size_hint: 1,1
        RelativeLayout:
            size: self.parent.size
            pos: self.parent.pos
            #NavigationDrawer:
            #    id: side_view
            #    size_hint: 1,1
            #    side_panel_darkness: 1
            #    side_panel_opacity: 0
            #    side_panel_width: 0
            #    main_panel_final_offset:1
            #    main_panel_darkness:.7
            #    separator_image_width:0 
            #    top_panel: 'side'
            #    ScrollView:
            #        size_hint:1,1
            #        #width: 700
            #        TreeView:
            #            id: tree_view
            #            size_hint: 1,1
            #            text: "Remove"
            #            size_hint_y: None
            #            height: self.minimum_height

            BoxLayout:
                orientation: 'vertical'
                size_hint: 1,1
                RelativeLayout:
                    size_hint: 1, None
                    height: 55

                    BoxLayout:
                        orientation: 'horizontal'
                        size_hint: 1, 1
                        padding:[0,0,10,0]
                        spacing: 10
                        canvas.before:
                            Color: 
                                rgba: (.3,.3,.3,1) if root.has_focus else (0.1,0.1,0.1,1)
                            Rectangle:
                                pos: self.pos
                                size: self.size

                        ImageButton:
                            size_hint: None, None
                            size: root.button_size,root.button_size
                            pos_hint: {'center_y':.5}
                            #on_press: root.show_side_view()
                            image: 'atlas://pydjay/gui/images/resources/show-list'
                        BoxLayout:
                            orientation: 'vertical'
                            size_hint: .75, 1
                            #height: 
                            Label:
                                size_hint: 1,1
                                text: root.playlist_title  #"PLAYLIST TITLE"
                                bold: True
                                halign: 'left'
                                valign: "bottom"
                                text_size: self.size
                                font_size: 18
                                #size_hint: None, None
                                #size: self.texture_size
                                height:45#
                            Label:
                                size_hint: 1,1
                                text: root.total_track_count
                                markup: True
                                halign: 'left'
                                valign: "top"
                                text_size: self.size
                                font_size: 15
                                #size_hint: None, None
                                #size: self.texture_size
                                height:45#

                        BoxLayout:
                            orientation: 'horizontal'
                            size_hint: 1, None
                            pos_hint: {'center_y': .5}
                            height: 30
                            spacing: 0
                            canvas.before:
                                Color:
                                    rgba: .2,.2,.2,1
                                Rectangle:
                                    pos:self.pos
                                    size: self.size

                            TextInput:
                                id:search_filter
                                size_hint: 1,1
                                multiline: False
                                text_size: self.width - 30, self.height
                                hint_text: "Filter list..."
                                foreground_color: 1,1,1,.8
                                background_color: 0,0,0,0
                                on_text: root.do_filter(*args)

                            ImageButton:
                                size_hint: None, None 
                                #pos_hint: {'center_y': .5}
                                size: 30,30
                                image:'atlas://pydjay/gui/images/resources/clear-filter'
                                on_press: search_filter.text = ''
                                #text:'Clear'

                HDivider:

                LargeTrackList:
                    id: master_list
                    size_hint: 1,1
                    player: root.main_player
                    item_class: SimpleDetailedListItem
                    item_convert: root._convert
                HDivider:
                Label:
                    id: track_count
                    size_hint: 1, None
                    markup:True
                    height: 25
                    text: ""
                    bold: True
                    halign: 'center'
                    valign: "middle"
                    text_size: self.size
                    font_size: 15
                    #size_hint: None, None
                    #size: self.texture_size
                    #height:45#
                    on_touch_down: root._on_list_touch_down(*args)

    #VDivider:
    #BoxLayout:
    #    orientation: 'vertical'
    #    size_hint: 0.5, 1
    #    TrackShortList:
    #        #orientation: 'vertical'
    #        size_hint: 1, 1
    #        id: short_list
    #        window:root.window
    #        queue: root.queue
    #        preview_player: root.preview_player
"""


#class TrackData(EventDispatcher):
#    pass

#tv_session_label_layout = """
#<CategoryLabel>
#    orientation: 'horizontal'
#    height: 35
#
#    on_is_open: self._open_me()
#    padding: [5,5,5,5]
#    spacing: 10
#    #on_is_selected: self._select_me()
#
#    Image:
#        size_hint: None,1
#        #color: [0,0,0,0]
#        #height: 
#        width: self.height
#        keep_ratio: True
#        allow_stretch: True
#        source: root.icon
#    Label:
#        size_hint: 1,1
#        text: root.text
#        text_size: self.size
#        halign: 'left'
#        valign: 'middle'
#        shorten: True
#        ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}
#"""

"""
class CategoryLabel(BoxLayout, TreeViewNode):
    icon = StringProperty('')#/Users/jihemme/Python/DJ/pydjay/gui/default_album_cover.png')
    text = StringProperty("N/A")


    def __init__(self, name, path, view, file_list, populate, *args, **kw):
        super(CategoryLabel, self).__init__(*args, **kw)
        self._name      = name
        self._path       = path
        self._view      = view
        #self._playlist  = playlist
        self._file_list = file_list
        self.populate = populate
        self.is_leaf = False
        #if self._path is not None:
        
            #self._name = os.path.basename(self._path)
        self.text = self._name
        self.icon = 'atlas://pydjay/gui/images/resources/default_album_cover'

    def _open_me(self, *args):
        #print 'open me'
        #if not os.path.exists(self._path) or self.nodes:
        #    return

        try:
            foo = self.populate()#os.listdir(self._path)
        except Exception, details:
            print details
            foo = []
        #children = []
        #if len(foo) > 0:
            #bar = self.vie
            #foo = []

        bar = []
        for node in self._view.iterate_all_nodes(self):
            #print node
            if node != self:
                bar.append(node)

        for x in bar:
            self._view.remove_node(x)

        for x in foo:
            self._view.add_node(x, self)

    def _select_me(self):
        #self._file_list.side_view.anim_to_state('closed')

        if self.is_selected:
            #print "self.path:", self._path
            self._file_list.set_track_list(get_session_by_name(self._path), False)
            #foo = os.listdir(self._path)
            #children = []
            #if len(foo) > 0:
            #    for x in foo:
            #        if os.path.isfile(os.path.join(self._path, x)):
            #            children.append(os.path.join(self._path, x))

            #if len(children) > 0:
            #    self._file_list.set_file_list(children)
Builder.load_string(tv_session_label_layout)
"""

class DragContext:
    def __init__(self, drag, drop):
        self.drag = drag
        self.drop = drop


class MainTrackList(BoxLayout, TrackListBehaviour):
    #has_focus         = BooleanProperty(False)
    master_list       = ObjectProperty(None)
    #tree_view   = ObjectProperty(None)
    short_list        = ObjectProperty(None)
    #queue             = ObjectProperty(None)
    #window            = ObjectProperty(None)
    main_player       = ObjectProperty(None)
    preview_player    = ObjectProperty(None)
    search_filter     = ObjectProperty(None)
    total_track_count = StringProperty("")
    playlist_title    = StringProperty("")
    title             = StringProperty("")
    
    def __init__(self, *args, **kwargs):
        super(MainTrackList, self).__init__(*args, **kwargs)
        self._focus = False
        self._keyboard = None
        Clock.schedule_once(self._post_init,-1)
        self.drag_context = DragContext(self._start_drag, None)
        self._current_selection = None
        self.set_keyboard_handlers({'ctrl+f':  self._focus_filter,
                                    'shift+q': self._add_selection_to_queue,
                                    'shift+s': self._add_selection_to_short_list})
        #self.focus()
        
    def _post_init(self, *args):
        self.search_filter.bind(focus = self._toggle_keyboard_shortcuts)
        self.master_list.adapter.bind(data = self._update_track_count)
        self.master_list.bind(adapter = self._update_track_count)
        self.main_player.bind(track = self._update_availability,
                              on_unavailable_added = self._update_availability)
        #self.tree_view.root.bold = True
        #self.tree_view.root.font_size = 20
        #self.tree_view.root.text = "LIBRARY"
        #foo = PlaylistItem("ALL TRACKS", get_master_playlist(), self.side_view, self)
        #self.tree_view.add_node(foo)
        #foo = CategoryLabel("FILTERS", None, self.tree_view, self, self._populate_filters)
        #self.tree_view.add_node(foo)
        #foo = CategoryLabel("PLAYLISTS", None, self.tree_view, self, self._populate_playlists)
        #self.tree_view.add_node(foo)
        #foo = CategoryLabel("SESSIONS", None, self.tree_view, self, self._populate_sessions)
        #self.tree_view.add_node(foo)
        self.queue.queue_view.adapter.bind(data = self._update_availability)
        self.adapter = self.master_list.adapter
        self.list_view = self.master_list.list_view
        


    """
    def focus(self):
        self.has_focus = True
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self, 'text')
        self._keyboard.bind(on_key_down = self._on_keyboard_down)
        if self._current_selection is not None:
            row = self._current_selection
            row = max(min(row, len(self.master_list.adapter.data) - 1), 0)
            try:
                v = self.master_list.adapter.get_view(row)
                if v is not None:
                    v._update_background()
                #self.master_list.adapter.get_view(row)._update_background()
                self._current_selection = row
            except IndexError:
                self._current_selection = None
                
    def unfocus(self):
        self.has_focus = False
        #self.search_filter.focus = False
        if self._keyboard is not None:
            self._keyboard.release()
        if self._current_selection is not None:
            #self.master_list.adapter.get_view(self._current_selection)._update_background()
            row = self._current_selection
            row = max(min(row, len(self.master_list.adapter.data) - 1), 0)
            try:
                v = self.master_list.adapter.get_view(row)
                if v is not None:
                    v._update_background()
                self._current_selection = row
            except IndexError:
                self._current_selection = None

                
    def _keyboard_closed(self):
        #print('My keyboard have been closed!')
        self._keyboard.unbind(on_key_down = self._on_keyboard_down)
        self._keyboard = None


    @property
    def current_selection(self):
        if self._current_selection is not None:
            try:
                return self.master_list.adapter[self._current_selection]
            except:
                return None
        return None


    @property
    def current_selection_index(self):
        if self._current_selection is not None:
            try:
                return self.master_list.adapter[self._current_selection]
            except:
                return None
        return None
            #self.main_player.add_unavailable(item['item'].track.location)
        
        
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        #print('The key', keycode, 'have been pressed')
        #print(' - text is %r' % text)
        #print(' - modifiers are %r' % modifiers)

        key_seq = "+".join(modifiers+[keycode[1]])

        
        if key_seq == 'down':
            if self._current_selection is not None:
                self.select(self._current_selection + 1)
            else:
                self.select(0)
        elif key_seq == 'shift+down':
            if self._current_selection is not None:
                self.select(self._current_selection + 20)
            else:
                self.select(0)
        elif key_seq == 'up':
            if self._current_selection is not None:
                self.select(self._current_selection - 1)
            else:
                self.select(0)

        elif key_seq == 'shift+u':
            #self.main_player.add_unavailable()
            #if self._current_selection is not None:
            item = self.current_selection #master_list.adapter[self._current_selection]
            if item is not None:
                self.main_player.add_unavailable(item['item'].track.location)

        elif key_seq == 'shift+a':
            #self.main_player.add_unavailable()
            #if self._current_selection is not None:
            item = self.current_selection #master_list.adapter[self._current_selection]
            if item is not None:
                self.main_player.remove_unavailable(item['item'].track.location)


                
        elif key_seq == 'shift+up':
            if self._current_selection is not None:
                self.select(self._current_selection - 20)
            else:
                self.select(0)

        
        elif key_seq == 'ctrl+f':
            self.search_filter.focus = True

        elif key_seq == 'shift+s':
            #if self._current_selection is not None:
            item = self.current_selection
            if item is not None:
                self.short_list.add_shortlist_track(item['item'].track)
            #else:
            #    self.select(0)
            
        elif key_seq == 'shift+q':
            #if self._current_selection is not None:
            item = self.current_selection
            if item is not None:
                self.queue.add_track(item['item'].track)
            #else:
            #    self.select(0)


        elif key_seq == 'enter':
            #if self._current_selection is not None:
            item = self.current_selection #master_list.adapter[self._current_selection]
            if item is not None:
                self.preview_player.play(item['item'].track)
        else:
            pydjay.core_logic.keyboard.key_map.key_pressed(keycode, modifiers)

        # Keycode is composed of an integer + a string
        # If we hit escape, release the keyboard
        #if keycode[1] == 'escape':
        #    keyboard.release()

        # Return True to accept the key. Otherwise, it will be used by
        # the system.
        return True

    """
    def _focus_filter(self):
        self.search_filter.focus = True

    def _add_selection_to_short_list(self):
        item = self.current_selection
        if item is not None:
            self.short_list.add_shortlist_track(item['item'].track)

    def _add_selection_to_queue(self):
        item = self.current_selection
        if item is not None:
            self.queue.add_track(item['item'].track)

    
        
    def _toggle_keyboard_shortcuts(self, *a):
        #print self.search_filter.focus
        if not self.search_filter.focus:
            self.window.request_focus(self)
            #if self.has_focus:
            #    self.focus()
            #pydjay.core.keyboard.enable_keyboard_shortcuts()
        else:
            self.window.suspend_focus()
            pass
            #pydjay.core.keyboard.disable_keyboard_shortcuts()

    def _update_availability(self, *args):
        self.master_list.update_availability(self._track_is_available)


    def show_preview_player(self, track, pos, size):
        #self.short_list.preview_track(track)
        
        #self.preview_player.set_track(track)
        self.preview_player.play(track)
        #self.window.show_preview_player(track, pos, size)

    #def _populate_filters(self):
    #    bar = get_filters()
    #    playlists = []
    #    for pl in sorted(bar.keys()):
    #        playlists.append(PlaylistItem(pl, bar[pl], self.side_view, self))
    #    return playlists

    #def _populate_sessions(self):
    ##    sessions = []
    #    for name, path in get_sessions():
    #        sessions.append(SessionItem(name, path, self.side_view, self))
    #    return sessions

    #def _populate_playlists(self):
    #    sessions = []
    #    for name, path in get_playlists():
    #        sessions.append(SessionItem(name, path, self.side_view, self))
    #    return sessions

    def set_playlist_title(self, tit):
        self.playlist_title = tit
    
    def _start_drag(self, coords, item):
        self.window.start_drag(coords, item.track)

    def do_filter(self, window, text):
        self.master_list.do_filter(text) #self._unfiltered_list


    #def _track_is_available(self, track):
    #    is_available = True
    #    if self.queue is not None:
    #        is_available = is_available and not self.queue.contains(track.location)
    #    if self.main_player is not None:
    #        is_available = is_available and (not self.main_player.has_played(track.location) and \
    #                                         (not ((self.main_player.track is not None) and \
    #                                               (self.main_player.track.track.location == track.location))))
    #    return is_available


    #def show_side_view(self):
    #    if self.side_view.state == 'open':
    #        self.side_view.anim_to_state('closed')
    #    else:
    #        self.side_view.anim_to_state('open')
            
    #def add_shortlist_track(self, track, index = None):
    #    self.short_list.add_track(track)
    #    self.short_list.sort()#_adapter.data.sort()
            
    #def enqueue_track(self, track_data):
    #    self.queue.enqueue(track_data.track)
    #    self.shortlist_adapter.data.remove(track_data)

    #def _pre_queue_item(self, *args):
    #    print "foo", args



    def _convert(self, row, item):
        return {'row': row,
                'item': item,
                'view':self,
                'drag_context':self.drag_context,
                'is_selected': False}

    #def clear_view(self):
    #    foo = []
    #    for node in self.tree_view.iterate_all_nodes(self.tree_view.root):
    #        foo.append(node)
#
#        for x in foo:
#            self.tree_view.remove_node(x)

    def _update_track_count(self, *args):
        num = len(self.master_list.adapter.data)
        time = 0

        track_count_text = self.title
        if num > 0 and track_count_text != "":
            track_count_text += " - " 
        #else:
        for t in self.master_list.adapter.data:
            try:
                time += t['item'].track.info.length
            except:
                pass
        track_count_text += "[color=#ffffff]" + str(num) + " tracks " + "[/color]" + \
                            "[color=#444444] | [/color]"+ \
                            "[color=#888888]" + seconds_to_human_readable(time / 1000000000) + "[/color]"
        self.track_count.text = track_count_text
        return True
        
    def _on_list_touch_down(self, window, event):
        if self.master_list.collide_point(*event.pos):
            if not event.is_mouse_scrolling:
                for data in self.master_list.adapter.data:
                    data['is_selected'] = False

    #def select(self, row):
    #    #print self._current_selection
    #    if len(self.master_list.adapter.data) == 0:
    #        self._current_selection = None
    #        return ##
#
#        row = max(min(row, len(self.master_list.adapter.data) - 1), 0)
#        if self._current_selection is not None:
#            try:
#                item = self.master_list.adapter[self._current_selection]
#                item['item'].is_selected = False
#                self.master_list.adapter.get_view(self._current_selection)._update_background()
#            except IndexError:
#                pass
#        try:
#            item = self.master_list.adapter[row]
#            self.master_list.list_view.layout_manager.show_index_view(row)
#            item['item'].is_selected = True
#            self.master_list.adapter.get_view(row)._update_background()
#            self._current_selection = row
#            self.window.request_focus(self)
#        except IndexError:
#            self._current_selection = None
#            pass
#

#    def set_file_list(self, list):
#        ll = []
#        for xx in list:
#            zz = load_file(xx)
#            if zz is not None:
#                ll.append(zz)
#        foo = [TrackData(x) for x in sorted(ll)]
#        for x in foo:
#            if self.queue.contains(x.track.location) or self.main_player.has_played(x.track.location):
#                x.is_available = False
#        self._unfiltered_list = foo
#        
#        if self.search_filter.text == "":        
#           self.master_list.adapter.data = foo #[TrackData(x) for x in sorted(ll)]
#        else:
#            self.search_filter.text = ""

    def set_track_list(self, list, sort = True):
        self.master_list.set_track_list(list, sort, self._track_is_available)
        self._update_track_count()
        num = len(self.master_list.adapter.data)
        time = 0
        if num == 0:
            self.total_track_count = ""
        else:
            for t in self.master_list.adapter.data:
                try:
                    time += t['item'].track.info.length
                except:
                    pass
                #[color=#<color>][/color]
            self.total_track_count = "[color=#ffffff]" + str(num) + " tracks " + "[/color]" + \
                                     "[color=#444444] | [/color]"+ \
                                     "[color=#888888]" + seconds_to_human_readable(time / 1000000000) + "[/color]"

        
    #def set_shortlist_tracks(self, list, sort = True):
    #    ll = []
    #    foo = sorted(list) if sort else list
    #    self.short_list.set_track_list(list, sort)
        
Builder.load_string(kv_string)
Factory.register('MainTrackList', MainTrackList)





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
    
    foo = MainTrackList()
    bar = MainWindow()#Builder.load_string(kv_string)#FilesScreen(size_hint = (1,1))#size = (450,550))
    #print "FOO", bar.adapter
    bar.add_widget(foo)
    foo.window = bar

    #foo.master_list. = bar.list.adapter
    foo.master_list.window = bar

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
