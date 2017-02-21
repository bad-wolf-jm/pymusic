import os
import time

from kivy.clock import mainthread, Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty, ListProperty, BooleanProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget
from kivy.uix.selectableview import SelectableView
from kivy.adapters.listadapter import ListAdapter


from kivy.properties import ObjectProperty
from kivy.factory import Factory

from kivy.graphics import *

from pydjay.gui.utils import seconds_to_human_readable
from pydjay.uix.long_press_button import LongPressButtonBehaviour


from kivy.logger import Logger
import player_deck
import player_display
from current_session_list import CurrentSessionList
from pydjay.gui.list_items.main_queue_track_card import MasterQueueTrackCard
from pydjay.gui.track_data import TrackData


#import pydjay.core_logic.keyboard
from kivy.core.window import Window

from pydjay.gui import large_track_list
from track_list_behaviour import TrackListBehaviour


kv_string = """
#:import MasterQueueTrackCard pydjay.gui.list_items.main_queue_track_card.MasterQueueTrackCard
<MasterQueue>:
    queue_view: list_view
    orientation: 'vertical'
    size_hint: 1,1
    #deck: deck
    #display: display
    current_session: current_session
    on_touch_up: self._on_touch_up(*args)
    BoxLayout:
        orientation: 'vertical'
        padding: [7,7,7,7]
        size_hint: 1, None
        height: 55
        spacing: 4

        canvas.before:
            Color:
                rgba: (.3, .3, .3, 1) if root.has_focus else (0.1, 0.1, 0.1, 1)
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            size_hint: 1,1
            text: "QUEUE"
            halign: 'center'
            valign: 'middle'
            font_size: 18
            #size_hint: None, None
            #size: self.texture_size
            text_size: self.size

        BoxLayout:
            orientation: 'horizontal'
            size_hint: 1, 1
            #height: 20
            spacing: 10
            Label:
                text: root.queue_time #"Total time:"
                #color: .6,.6,.6,1
                #halign: 'right'
                font_size: 15
                valign: 'middle'
                markup: True
                size_hint: 1, 1
                #size: self.texture_size
                text_size: self.size
                valign: 'bottom'
                halign: 'left'

            Label:
                text: root.queue_end_time #"Queue ends at:"
                #color: .6,.6,.6,1
                #halign: 'right'
                font_size: 15
                valign: 'middle'
                markup: True
                size_hint: 1, 1
                #size: self.texture_size
                text_size: self.size
                valign: 'bottom'
                halign: 'right'
                #height:20#

    HDivider:
    LargeTrackList:
        id: list_view
        orientation: 'vertical'
        size_hint: 1,1
        padding:5
        spacing:5
        item_class: MasterQueueTrackCard
        item_convert: root._convert

        on_touch_down: root._on_touch_down(*args)
        #height:self.minimum_height
    HDivider:
    CurrentSessionList:
        id: current_session
        #item_class: DefaultTrackItemView
        size_hint: 1, .75
"""

class DragContext:
    def __init__(self, drag, drop):
        self.drag = drag
        self.drop = drop

        
class MasterQueue(BoxLayout, TrackListBehaviour):
    #has_focus         =  BooleanProperty(False)
    ###is_connected_to   = StringProperty("")
    #connected_ip      = StringProperty("")
    #connected_host    = StringProperty("")
    #connected_port    = NumericProperty(0) 
    queue_view         = ObjectProperty(None)
    #window            = ObjectProperty(None)
    track_list        = ListProperty()
    card_list         = ListProperty()
    queue_time        = StringProperty()
    play_time         = StringProperty()
    queue_end_time    = StringProperty()
    queue_changed     = BooleanProperty(False)
    uploading_track   = ObjectProperty(None)
    short_list        = ObjectProperty(None)
    player            = ObjectProperty(None)
    deck              = ObjectProperty(None)
    preview_player    = ObjectProperty(None)
    

    def __init__(self, *args, **kwargs):
        super(MasterQueue, self).__init__(*args, **kwargs)
        self._queued_tracks = set([])
        #self.adapter = ListAdapter(
        #    cls = MasterQueueTrackCard,
        #    data = [],
        #    selection_mode = 'none',
        #    allow_empty_selection = False,
        #    args_converter = self._convert
        #)
        #self._control_client   = None
        #self._files_port       = None
        #self._uploading_track  = None
        #self._uploading_thread = None
        #self._uploading        = False
        #self._is_connected     = False
        
        self.drag_context = DragContext(self._start_drag, self._drop)
        self._play_time        = 0
        self._total_queue_time = 0
        self.has_focus         = False
        self._current_selection = None
        self.set_keyboard_handlers({'shift+up': self._move_selection_up,
                                    'shift+down': self._move_selection_down,
                                    'shift+t': self._move_selection_to_top,
                                    'shift+backspace': self._delete_selection})
        Clock.schedule_once(self._post_init,0)

    def show_preview_player(self, track, pos, size):
        #self.preview_player.set_track(track)
        self.preview_player.play(track)

#    def focus(self):
#        self.has_focus = True
#        self._keyboard = Window.request_keyboard(self._keyboard_closed, self, 'text')
#        self._keyboard.bind(on_key_down = self._on_keyboard_down)
#        if self._current_selection is not None:
#            row = self._current_selection
#            row = max(min(row, len(self.adapter.data) - 1), 0)
#            try:
#                v = self.adapter.get_view(self._current_selection)
#                if v is not None:
#                    v._update_background()
#                #self.adapter.get_view(self._current_selection)._update_background()
#                self._current_selection = row
#            except IndexError:
#                self._current_selection = None
 #           
 #   def unfocus(self):
 #       self.has_focus = False
 #       if self._keyboard is not None:
 #           self._keyboard.release()
 #       if self._current_selection is not None:
 #           row = self._current_selection
 #           row = max(min(row, len(self.adapter.data) - 1), 0)
 #           try:
 #               v = self.adapter.get_view(self._current_selection)
 #               if v is not None:
 #                   v._update_background()
 #               self._current_selection = row
 #           except IndexError:
 #               self._current_selection = None
                
 #   def _keyboard_closed(self):
 #       #print('My keyboard have been closed!')
 #       self._keyboard.unbind(on_key_down = self._on_keyboard_down)
 #       self._keyboard = None

 #   @property
 #   def current_selection(self):
 #       if self._current_selection is not None:
 #           try:
 #               return self.adapter.data[self._current_selection]
 #           except:
 #               return None
 #       return None


    def _move_selection_up(self):
        #print self._current_selection
        #if self._current_selection is not None:
        item = self.current_selection #short_list.adapter.data[self._current_selection]
        if item is not None:
            self.queue_view.remove_track(item['item'])
            self.add_track(item['item'].track, self._current_selection - 1)
            self.select(self._current_selection - 1)

    def _move_selection_down(self):
        #print self._current_selection
        #if self._current_selection is not None:
        item = self.current_selection #short_list.adapter.data[self._current_selection]
        if item is not None:
            self.queue_view.remove_track(item['item'])
            self.add_track(item['item'].track, self._current_selection + 1)
            self.select(self._current_selection + 1)

            #        elif key_seq == 'shift+t':
    def _move_selection_to_top(self):
        #print self._current_selection
        #if self._current_selection is not None:
        item = self.current_selection #short_list.adapter.data[self._current_selection]
        if item is not None:
            self.queue_view.remove_track(item['item'])
            self.add_track(item['item'].track, 0)
            self.select(self._current_selection)

            #        elif key_seq == 'shift+backspace':
    def _delete_selection(self):
        #if self._current_selection is not None:
        item = self.current_selection #short_list.adapter.data[self._current_selection]
        if item is not None:
            self.queue_view.remove_track(item['item'])
            self.short_list.add_shortlist_track(item['item'].track, 0)
            #self.add_shortlist_track(item.track, 0)
            self.select(self._current_selection)

            #        elif key_seq == 'shift+q':
    #def _add_selection_to_queue(self):
    #    #if self._current_selection is not None:
    #    item = self.current_selection #short_list.adapter.data[self._current_selection]
    #    if item is not None:
    #        self.short_list.remove_track(item['item'])
    #        self.queue.add_track(item['item'].track)

    #def _start_drag(self, coords, item):
    #    self.window.start_drag(coords, item.trac


    def _start_drag(self, coords, item):
        if self.window is not None:
            try:
                self.window.start_drag(coords, item.track)
                self.queue_view.remove_track(item)
            except Exception, details:
                print details

    def _drop(self, row):
        if self.window is not None and self.window._drag_payload is not None:
            self.add_track(self.window._drag_payload, row)
            self.window.drop()

#    def _on_keyboard_down_FOO(self, keyboard, keycode, text, modifiers):
#        #print('The key', keycode, 'have been pressed')
#        #print(' - text is %r' % text)
#        #print(' - modifiers are %r' % modifiers)
#        key_seq = "+".join(modifiers+[keycode[1]])
#        if key_seq == 'down':
#            if self._current_selection is not None:
#                #if self._current_selection < len(self.adapter.data) - 1:
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
#
#
#        elif key_seq == 'shift+up':
#            #print self._current_selection
#            #if self._current_selection is not None:
#            item = self.current_selection #adapter.data[self._current_selection]
#            if item is not None:
#                self.remove_track(item)
#                self.add_track(item.track, self._current_selection - 1)
#                self.select(self._current_selection - 1)
#
#        elif key_seq == 'shift+down':
 #           #print self._current_selection
##            if self._current_selection is not None:
##                item = self.adapter.data[self._current_selection]
#            item = self.current_selection #adapter.data[self._current_selection]
#            if item is not None:
#
#                self.remove_track(item)
#                self.add_track(item.track, self._current_selection + 1)
#                self.select(self._current_selection + 1)#
#
#
 #       elif key_seq == 'shift+t':
 #           #print self._current_selection
 #           item = self.current_selection #adapter.data[self._current_selection]
 #           if item is not None:
##            if self._current_selection is not None:
#                #item = self.adapter.data[self._current_selection]
#                self.remove_track(item)
#                self.add_track(item.track, 0)
#                self.select(self._current_selection)
#
#        elif key_seq == 'shift+backspace':
#            item = self.current_selection #adapter.data[self._current_selection]
#            if item is not None:
##            if self._current_selection is not None:
#                #item = self.adapter.data[self._current_selection]
#                self.remove_track(item)
#                self.short_list.add_shortlist_track(item.track, 0)
#                self.select(self._current_selection)
#
#        #elif key_seq == 'shift+q':
#        #    if self._current_selection is not None:
#        #        self.queue.add_track(self.short_list.adapter.data[self._current_selection].track)##
##
#
#        elif key_seq == 'enter':
#            item = self.current_selection #adapter.data[self._current_selection]
#            if item is not None:
##            if self._current_selection is not None:
##                item = self.adapter.data[self._current_selection]
#                self.preview_player.play(item.track)
#        else:
#            pydjay.core_logic.keyboard.key_map.key_pressed(keycode, modifiers)
#        pass
#
#        # Keycode is composed of an integer + a string
#        # If we hit escape, release the keyboard
#        #if keycode[1] == 'escape':
#        #    keyboard.release()#
#
#        # Return True to accept the key. Otherwise, it will be used by
#        # the system.
#        return True


        
  #  def _toggle_keyboard_shortcuts(self, *a):
  #      #print self.search_filter.focus
  #      if not self.search_filter.focus:
  #          if self.has_focus:
  #              self.focus()
  #          #pydjay.core.keyboard.enable_keyboard_shortcuts()
  #      else:
  #          pass
            #pydjay.core.keyboard.disable_keyboard_shortcuts()



    #def select(self, row):
    ##    #print self._current_selection#
#
#        if len(self.adapter.data) == 0:
#            self._current_selection = None
#            return 
 #       
 #       row = max(min(row, len(self.adapter.data) - 1), 0)
 #       if self._current_selection is not None:
 #           try:
 #               item = self.adapter.data[self._current_selection]
 #               item.is_selected = False
 #           except IndexError:
 #               pass
 #           #self.master_list.adapter.get_view(self._current_selection)._update_background()
 #       try:
 #           item = self.adapter.data[row]
 #           #self.short_list.list_view.layout_manager.show_index_view(row)
 #           item.is_selected = True
 #           #self.master_list.adapter.get_view(row)._update_background()
 #           self._current_selection = row
 #           self.window.request_focus(self)
 #       except IndexError:
 #           self._current_selection = None

        
    def contains(self, location):
        return location in self._queued_tracks
        
    def _post_init(self, *args):
        #self.list_view.adapter = self.adapter
        self.play_time = "[color=#bbbbbb]Play time:[/color] " + \
                         "[color=#ffffff]" + \
                         seconds_to_human_readable(self._play_time) + \
                         "[/color]"


        self.queue_time = "[color=#bbbbbb]Total time:[/color] " + \
                          "[color=#ffffff]" + \
                          seconds_to_human_readable(0) + \
                          "[/color]"
        current_time = time.time()
        self.queue_end_time = "[color=#bbbbbb]Queue ends at:[/color] " + \
                              "[color=#ffffff]" + \
                              time.strftime("%H:%M", time.localtime(current_time)) + \
                              "[/color]"
        self.adapter = self.queue_view.adapter
        self.list_view = self.queue_view.list_view
        self.list_view.layout_manager.default_size = 70
        
        Clock.schedule_interval(self._update_queue_times, 1)
        self.update_labels()
        
    def set_player(self, p):
        self.player = p


    def dequeue(self, incomplete = None):
        self.update_labels()
        self._queued_tracks.discard(self.adapter.data[0]['item'].track.location)
        t_track = self.adapter.data.pop(0)
        return t_track['item']

    def remove_track(self, track):
        self._queued_tracks.discard(track.track.location)
        self.queue_view.remove_track(track)
        #idx = self.adapter.data.index(track)
        #self.adapter.data.remove(track)
        self.update_labels()
    
    def top(self):
        t_track = self.adapter.data[0]
        return t_track

    @property
    def is_empty(self):
        return len(self.adapter.data) == 0

    def _convert(self, row, item):
        return {'row': row, 'item': item, 'view':self, 'drag_context':self.drag_context, 'is_selected': False}

    
    def add_track(self, track, index = None):
        self.queue_view.add_track(track, index)
        #new_track = TrackData(track)
        #self._queued_tracks.add(track.location)
        #if index is None:
        #    self.adapter.data.append(new_track)
        #else:
        #    self.adapter.data.insert(index, new_track)
        self.update_labels()

    enqueue = add_track

    def set_track_list(self, list):
        self.queue_view.set_track_list(list, False)
        #ll = [TrackData(track) for track in list]
        #for t in ll:
        #    self.list_view.adapter.data.append(t)
        self._queued_tracks = set([track.location for track in list])
        self.update_labels()


    def _update_queue_times(self, *a):
        pl_remaining_time = self.deck._player.remaining_time if self.deck._player is not None else 0
        total_length = 0
        for track in self.queue_view.adapter.data:#track_list:
            total_length += track['item'].track.info.length + 5000000000
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
        for track in self.queue_view.adapter.data:#track_list:
            total_length += track['item'].track.info.length + 5000000000
        total_length = max(total_length - 5000000000, 0)
        self._total_queue_time = total_length
        self._update_queue_times()
        current_time = time.time()
        for card in self.queue_view.adapter.data:
            play_time = time.strftime("%H:%M", time.localtime(current_time))
            card['item'].play_time = play_time
            current_time += card['item'].track.info.length / 1000000000 + 5

    def _on_touch_up(self, window, event):
        if self.queue_view.collide_point(*event.pos):
            if self.is_empty or (event.pos[1] < self.queue_view.height - self.queue_view.list_view.container.height + self.queue_view.list_view.pos[1]):
                if self.window is not None and self.window._drag_payload is not None:
                    self.add_track(self.window._drag_payload)
                    self.window.drop()

    def _on_touch_down(self, window, event):
        pass
        #if self.list_view.collide_point(*event.pos):
        #    if not event.is_mouse_scrolling:
        #        for data in self.adapter.data:
        #            data.is_selected = False

    def shutdown(self):
        self.deck.shutdown()

Builder.load_string(kv_string)
Factory.register('MasterQueue', MasterQueue)




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
