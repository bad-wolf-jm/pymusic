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
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.selectableview import SelectableView
from kivy.uix.treeview import TreeViewNode
from kivy.uix.label import Label
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

#from pydjay.uix.side_panel import NavigationDrawer

from pydjay.gui.utils import seconds_to_human_readable

#from pydjay.uix.recycleView import RecycleView






#kv_string = """
##:import label kivy.uix.label
##:import sla kivy.adapters.simplelistadapter
#<TrackList>:
#    orientation: 'horizontal'
#    size_hint: 1,1
#    list_view: list
#    list_header: header
#    BoxLayout:
#        orientation: 'vertical'
#        RelativeLayout:
#            id: header
#            size_hint: 1, None
#            height: 35
#        HDivider:###

#        ListView:
#            id: list
#            size_hint: 1,1
#            #on_touch_down: root._on_list_touch_down(*args)
#"""
"""
class TrackData(EventDispatcher):
    is_available = BooleanProperty(True)
    is_selected  = BooleanProperty(False)
    track        = ObjectProperty(None)
    def __init__(self, track):
        super(TrackData, self).__init__()
        self.track = track


    def __lt__(self, other):
        #print 'cmp'
        if other is None:
            return False
        return self.track < other.track

    def __le__(self, other):
        #print 'cmpe'
        if other is None:
            return False
        return self.track <= other.track

    def __gt__(self, other):
        #print 'cmp'
        if other is None:
            return True
        return self.track > other.track

    def __ge__(self, other):
        #pint 'cmpe'
        if other is None:
            return True
        return self.track >= other.track

    def __eq__(self, other):
        #print 'cmpe'
        if other is None:
            return False
        return self.track == other.track
"""

kv_string_item = """
<DefaultTrackItemView>:
    #album_art: album_art
    #album_art_file:'atlas://pydjay/gui/images/resources/transparent_image'
    bg: bg
    size_hint: 1, None
    height:35
    bold: False
    color: 1,1,1,1

    on_touch_down: self._on_touch_down(*args)

    #on_pos:  self.update_bg()
    #on_size: self.update_bg()

    Widget:
        id: bg
        size_hint: 1,1
        on_pos:  root._update_background()
        on_size: root._update_background()#self.pos, self.size)

    BoxLayout:
        orientation: 'horizontal'
        size_hint: 1, None
        #size_hint: 1,1 
        padding:[10,1,10,1]
        spacing: 10
        height:35
        Label:
            id: index
            bold: root.bold
            color: root.color
            font_size:15
            text: root.idx
            text_size: self.size
            halign: 'left'
            valign: 'middle'
            size_hint: None, 1
            width: 30
            shorten: True
            ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}
            #opacity: 0.2 if root.dimmed else 1

        Label:
            id: title
            bold: root.bold
            color: root.color
            font_size:15
            text: root.tr_title
            text_size: self.size
            halign: 'left'
            valign: 'middle'
            size_hint: 1, 1
            shorten: True
            ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}
            #opacity: 0.2 if root.dimmed else 1
        Label:
            id: length
            bold: root.bold
            color: root.color
            font_size:15
            text: root.length
            text_size: self.size
            halign: 'right'
            valign: 'middle'
            size_hint: None, 1
            width: 75
            shorten: True
            ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}
            #opacity: 0.2 if root.dimmed else 1
"""

class DefaultTrackItemView(LongPressButtonBehaviour, RelativeLayout):
    #row            = StringProperty("")
    idx            = StringProperty("")
    album_art_file = ObjectProperty(None)
    favorite       = BooleanProperty(False)
    has_waveform   = BooleanProperty(False)
    tr_title          = StringProperty("")
    artist         = StringProperty("")
    album          = StringProperty("")
    bpm            = StringProperty("")
    length         = StringProperty("")
    bg             = ObjectProperty(None)
    dimmed         = BooleanProperty(True)

    def __init__(self, row = None, item = None, view = None, window = None, *args, **kwargs):
        super(DefaultTrackItemView, self).__init__(*args, **kwargs)
        #self.album_art = 'pydjay/gui/default_album_cover.png'
        self.row = row
        self._album_art = None
        self._item_data = item
        self._view = view
        self._item = self._item_data.track if self._item_data is not None else None
        self._window = window
        self._long_press_threshold = .25
        self.bind(on_long_press = self._start_dragging)

        

        
        if self._item_data is not None:
            self._update_background()#None, self._item_data.is_selected)
            self._update_availability()#None, self._item_data.is_available)
            self._item_data.bind(is_selected  = self._update_background,
                                 is_available = self._update_background)
            
        if self._item is not None:
            #print self.row
            self.idx    = str(self.row + 1)+'.'
            self.tr_title  = "%s - %s"%(unicode(self._item.metadata.title), unicode(self._item.metadata.artist))
            #self.artist = unicode(self._item.metadata.artist)
            #self.album  = unicode(self._item.metadata.album)
            #self.bpm    = str(self._item.metadata.bpm) if self._item.metadata.bpm is not None else ""
            self.length = seconds_to_human_readable(int(self._item.info.length /1000000000))
            #self.has_waveform =  self._item.metadata.waveform is not None
##
#
 #           try:
 #               # JUST SO I DON'T FORGET
 #               self._item.bind(waveform = self._update_waveform_availability)
 #           except:
 #               pass

            
  #          if self._item.metadata.album_cover is not None:
  #              try:
  #                  self.album_art.source = self._item.metadata.album_cover['tiny']
  #              except:
  #                  self.album_art.source = 'atlas://pydjay/gui/images/resources/default_album_cover'
                #im_type = self._item.metadata.album_cover[0]
                #im_data = self._item.metadata.album_cover[1]
                #ext = {'image/jpeg': 'jpg','image/png': 'png'}.get(im_type, None)
                #if ext is not None:
                #    data = io.BytesIO(im_data)
                #    im   = CoreImage(data, ext = ext)
                #    self._album_art = im
   #         else:
   #             self.album_art.source = 'atlas://pydjay/gui/images/resources/default_album_cover'
        else:
            #self.album_art.source = 'pydjay/gui/transparent_image.png'
            self.title  = ""#unicode(item.metadata.title)
            self.artist = ""#unicode(item.metadata.artist)
            self.album  = ""#unicode(item.metadata.album)
            self.bpm    = ""#str(item.metadata.bpm)
            self.length = ""#seconds_to_human_readable(int(item.info.length /1000))
            #self.album_art.source = 'pydjay/gui/default_album_cover.png'


                #self.update_bg()

    def _update_availability(self, *args):#win, value):
        pass
    
    def _update_background(self, *value):
        #print "UPDATE BACKGROUND AVAILABILITY"
        value = self._item_data.is_selected if self._item_data is not None else False
        self.bold = value
        self.bg.canvas.clear()
        if value:
            with self.bg.canvas:
                Color(0,.3,.7,1)
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
        if self._window is not None:
            try:
                self._window.start_drag(self.to_window(x,y), self._item)
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
                self._item_data.is_selected = True
            except Exception, details:
                print details, self._item
                

Builder.load_string(kv_string_item)
Factory.register('DefaultTrackItemView', DefaultTrackItemView)



    

"""
class TrackList(BoxLayout):
    list_view    = ObjectProperty(None)
    window       = ObjectProperty(None)
    adapter      = ObjectProperty(None)
    item_class   = ObjectProperty(None)
    item_convert = ObjectProperty(None)
    list_header  = ObjectProperty(None)
    player       = ObjectProperty(None, allownone = True)
    
    def __init__(self, *args, **kwargs):
        super(TrackList, self).__init__(*args, **kwargs)

        self._unfiltered_list = []
        self._filter_text = ""
        self._filter_cache = {}
        self._current_selection = None
        #self._special_filters = {'~bpm': self._filter_like_bpm,
        #                         '<bpm': self._filter_smaller_bpm,
        #                         '>bpm': self._filter_bigger_bpm,
        #                         #'~genre': self._filter_like_genre,
        #                         #'~style': self._filter_like_style,
        #                         #'~length': self._filter_like_length,
        #                         #'<length': self._filter_smaller_length,
        #                         #'>length': self._filter_longer_length
        #}
        
        self.adapter = ListAdapter(
            cls = DefaultTrackItemView,
            data = [],
            selection_mode = 'none',
            allow_empty_selection = True,
            args_converter = self._convert
        )

        Clock.schedule_once(self._post_init,0)
        self.bind(item_class = self._update_adapter)
        self.bind(item_convert = self._update_adapter)
        self.bind(player = self._update_player)
        #self.adapter.bind(data = self._update_track_count)

    def _post_init(self, *args):
        self.list_view.adapter = self.adapter



    def _update_player(self, i, value):
        self.player.bind(track = self._update_filter)


    def _update_filter(self, *a):
        self.do_filter(self._filter_text)
        
        
    def do_filter(self, text):
        #self._filter_text = text
        if text == "":
            self._filter_cache = {}
        self._filter_text = text
            
        if text in self._filter_cache:
            self.adapter.data = self._filter_cache[text]
        else:
            self._filter_cache = {}
            foo = text.split(" ")
            bar = [x for x in self._unfiltered_list if x.track.matches(foo)]
            self._filter_cache[text] = bar
            self.adapter.data = bar
        
    def _convert(self, row, item):
        return {'row': row, 'item': item, 'view':self, 'window':self.window}


    def _update_adapter(self, window, value):
        data = self.adapter.data
        self.adapter = ListAdapter(
            cls = self.item_class if self.item_class is not None else DefaultTrackItemView,
            data = [],
            selection_mode = 'none',
            allow_empty_selection = False,
            args_converter = self.item_convert if self.item_convert is not None else self._convert
        )
        self.adapter.data = data
        self.list_view.adapter = self.adapter
        try:
            header = self.item_class.get_header()
        except:
            header = None
        if header is not None:
            self.list_header.add_widget(header)
            self.list_header.height = 35
        else:
            self.list_header.height = 0


    def update_availability(self, available = None):
        for track in self._unfiltered_list:
            if available is not None:
                #print type(track)
                track.is_available = available(track.track)
    
    #def _on_list_touch_down(self, window, event):
    #    #print "TOUCH DOWN"
    #    if self.collide_point(*event.pos):
    #        if not event.is_mouse_scrolling:
    #            for data in self.list_view.adapter.data:
    #                #print "FOOBAR"
    #                #data.is_selected = False
    #                pass
                    
    def _on_touch_up(self, window, event):
        if self.collide_point(*event.pos):
            if len(self.shortlist_adapter.data) == 0 or \
               (event.pos[1] < self.short_list.height - self.short_list.container.height + self.short_list.pos[1]):
                if self.window is not None and self.window._drag_payload is not None:
                    self.accept_drop_payload()
                    
    def set_track_list(self, list, sort = True, available = None):
        ll = []
        foo = sorted(list) if sort else list
        bar = [TrackData(x) for x in foo]
        for x in bar:
            if available is not None:
                x.is_available = available(x.track)
            else:
                x.available = True
            x.bind(is_selected = self._update_selection)
                
        self._unfiltered_list = bar
        self.adapter.data = bar

    def _update_selection(self, obj, value):
        print obj, value
        if value is False:
            if obj == self._current_selection:
                self._current_selection = None
        else:
            if self._current_selection != obj:
                self._current_selection = obj
                

    def get_full_track_list(self):
        return [x.track for x in self._unfiltered_list]
    
    def add_track(self, track, index = None, is_available = None):
        foo = TrackData(track)
        if is_available is not None:
            foo.is_available = is_available(track)
        if index is not None:
            self._unfiltered_list.insert(index, foo)
        else:
            self._unfiltered_list.append(foo)
        self.do_filter(self._filter_text)
        #
        #self.adapter.data.append()
    
    def remove_track(self, track_data):
        self._unfiltered_list.remove(track_data)
        self.do_filter(self._filter_text)

    def sort(self):
        self._unfiltered_list.sort()
        self.do_filter(self._filter_text)
        #self.adapter.data.sort()

Builder.load_string(kv_string)
Factory.register('TrackList', TrackList)

"""



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
    Window.size = 1000,1000
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
    
    bar = TrackList()#Builder.load_string(kv_string)#FilesScreen(size_hint = (1,1))#size = (450,550))
    bar.item_class = MasterListTrackItem
    #print "FOO", bar.adapter
    #bar.list.master_list.adapter = bar.list.adapter
    #bar.list.short_list.window = bar

    ll = []
    for xx in os.listdir('/Volumes/Media/Blues MP3'):
        yy = os.path.join('/Volumes/Media/Blues MP3', xx)
        zz = load_file(yy)
        if zz is not None:
            ll.append(zz)


    
    bar.set_track_list(ll)#range(15000)
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
    #bar.unload()
