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
    HDivider:
    CurrentSessionList:
        id: current_session
        size_hint: 1, .75
"""

class DragContext:
    def __init__(self, drag, drop):
        self.drag = drag
        self.drop = drop

        
class MasterQueue(BoxLayout, TrackListBehaviour):
    queue_view         = ObjectProperty(None)
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
        self.drag_context = DragContext(self._start_drag, self._drop)
        self._play_time        = 0
        self._total_queue_time = 0
        self.has_focus         = False
        self._current_selection = None
        self.set_keyboard_handlers({'shift+up':        self._move_selection_up,
                                    'shift+down':      self._move_selection_down,
                                    'shift+t':         self._move_selection_to_top,
                                    'shift+backspace': self._delete_selection})
        self.register_event_type('on_queue_changed')
        self.register_event_type('on_current_session_changed')

        Clock.schedule_once(self._post_init,0)


    def on_queue_changed(self, *a):
        pass

    def on_current_session_changed(self, *a):
        pass

    
    def show_preview_player(self, track, pos, size):
        self.preview_player.play(track)

    def _move_selection_up(self):
        item = self.current_selection 
        if item is not None:
            self.queue_view.remove_track(item['item'])
            self.add_track(item['item'].track, self._current_selection - 1)
            self.select(self._current_selection - 1)

    def _move_selection_down(self):
        item = self.current_selection
        if item is not None:
            self.queue_view.remove_track(item['item'])
            self.add_track(item['item'].track, self._current_selection + 1)
            self.select(self._current_selection + 1)

    def _move_selection_to_top(self):
        item = self.current_selection
        if item is not None:
            self.queue_view.remove_track(item['item'])
            self.add_track(item['item'].track, 0)
            self.select(self._current_selection)

    def _delete_selection(self):
        item = self.current_selection
        if item is not None:
            self.remove_track(item['item'])
            self.short_list.add_shortlist_track(item['item'].track, 0)
            self.select(self._current_selection)

    def _start_drag(self, coords, item):
        if self.window is not None:
            try:
                self.window.start_drag(coords, item.track)
                self.remove_track(item)
            except Exception, details:
                print details

    def _drop(self, row):
        if self.window is not None and self.window._drag_payload is not None:
            self.add_track(self.window._drag_payload, row)
            self.window.drop()

        
    def contains(self, location):
        return location in self._queued_tracks
        
    def _post_init(self, *args):
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
        self.dispatch('on_queue_changed')
        return t_track['item']

    def remove_track(self, track):
        self._queued_tracks.discard(track.track.location)
        self.queue_view.remove_track(track)
        self.dispatch('on_queue_changed')
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
        self._queued_tracks.add(track.location)
        self.update_labels()
        self.dispatch('on_queue_changed')

    enqueue = add_track

    def set_track_list(self, list):
        self.queue_view.set_track_list(list, False)
        self._queued_tracks = set([track.location for track in list])
        self.update_labels()
        self.dispatch('on_queue_changed')


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

    def shutdown(self):
        self.deck.shutdown()

Builder.load_string(kv_string)
Factory.register('MasterQueue', MasterQueue)
