import os
import time

from kivy.clock import mainthread, Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty, ListProperty, BooleanProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.factory import Factory
from elements.utils import seconds_to_human_readable
from kivy.logger import Logger
#from current_session_list import CurrentSessionList
from elements import large_track_list
from behaviors.track_list_behaviour import TrackListBehaviour
from pydjay.bootstrap import play_queue, playback_manager, session_manager, add_shortlist_track

kv_string = """
#:import MasterQueueTrackCard pydjay.ui.elements.main_queue_track_card.MasterQueueTrackCard
<MasterQueue>:
    queue_view: list_view
    orientation: 'vertical'
    size_hint: 1,1
    #current_session: current_session
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
                text_size: self.size
                valign: 'bottom'
                halign: 'left'

            Label:
                text: root.queue_end_time #"Queue ends at:"
                font_size: 15
                valign: 'middle'
                markup: True
                size_hint: 1, 1
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
    #HDivider:
    #CurrentSessionList:
    #    id: current_session
    #    size_hint: 1, .75
"""


class DragContext:
    def __init__(self, drag, drop):
        self.drag = drag
        self.drop = drop


class MasterQueue(BoxLayout, TrackListBehaviour):
    queue_view = ObjectProperty(None)
    track_list = ListProperty()
    card_list = ListProperty()
    queue_time = StringProperty()
    play_time = StringProperty()
    queue_end_time = StringProperty()
    queue_changed = BooleanProperty(False)
    uploading_track = ObjectProperty(None)
    short_list = ObjectProperty(None)
    player = ObjectProperty(None)
    deck = ObjectProperty(None)
    preview_player = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        super(MasterQueue, self).__init__(*args, **kwargs)
        self._queued_tracks = set([])
        self.drag_context = DragContext(self._start_drag, self._drop)
        self._play_time = 0
        self._total_queue_time = 0
        self.has_focus = False
        self._current_selection = None
        self.can_delete_items = True
        self.fixed_item_positions = False
        self.set_keyboard_handlers({'shift+up':        self._move_selection_up,
                                    'shift+down':      self._move_selection_down,
                                    'shift+t':         self._move_selection_to_top})
        #'shift+backspace': self._delete_selection})
        play_queue.bind(on_queue_content_change=self._update_queue_contents)
        playback_manager.bind(wait_time=self._update_queue_labels,
                              queue_length=self._update_queue_length,
                              queue_end_time=self._update_queue_end_time)

        Clock.schedule_once(self._post_init, 0)

    def _update_queue_contents(self, i, queue):
        self.set_track_list(queue)
        item = self.current_selection
        if item is not None:
            self.select(self._current_selection + 1)

    def show_preview_player(self, track, pos, size):
        self.preview_player.play(track)

    def _start_drag(self, coords, item):
        if self.window is not None:
            try:
                self.window.start_drag(coords, item.track)
                play_queue.remove_track(item.track)
            except Exception, details:
                print details

    def _drop(self, row):
        if self.window is not None and self.window._drag_payload is not None:
            play_queue.add_track(self.window._drag_payload, row)
            self.window.drop()

    def _delete_selection(self):
        item = self.current_selection
        if item is not None and self.can_delete_items:
            self.remove_track(item['item'])
            self.select(self._current_selection - 1)

    def contains(self, location):
        return location in self._queued_tracks

    def _post_init(self, *args):
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
        self._update_queue_contents(None, play_queue.track_list)
        self._update_queue_labels()
        self._update_queue_length()

    def set_player(self, p):
        self.player = p

    def _convert(self, row, item):
        return {'row': row, 'item': item, 'view': self, 'drag_context': self.drag_context, 'is_selected': False}

    def add_track(self, track, index=None, track_is_available=True):
        play_queue.add_track(track, index)
    enqueue = add_track

    def remove_track(self, track):
        play_queue.remove_track(track.track)

    def set_track_list(self, list):
        self.queue_view.set_track_list(list, False)
        self._queued_tracks = set([track.location for track in list])
        self._update_queue_labels()

    def _update_queue_end_time(self, *a):
        current_time = playback_manager.queue_end_time
        self.queue_end_time = "[color=#bbbbbb]Queue ends at:[/color] " + \
                              "[color=#ffffff]" + \
                              time.strftime("%H:%M", time.localtime(current_time)) + \
                              "[/color]"

    def _update_queue_length(self, *a):
        total_length = playback_manager.queue_length
        self.queue_time = "[color=#bbbbbb]Total time:[/color] " + \
                          "[color=#ffffff]" + \
                          seconds_to_human_readable(total_length / 1000000000) + \
                          "[/color]"

    def _update_queue_labels(self, *a):
        current_time = time.time()
        for card in self.queue_view.adapter.data:
            play_time = time.strftime("%H:%M", time.localtime(current_time))
            card['item'].play_time = play_time
            current_time += card['item'].track.info.length / 1000000000 + playback_manager.wait_time

    def _on_touch_up(self, window, event):
        if self.queue_view.collide_point(*event.pos):
            if play_queue.is_empty or (event.pos[1] < self.queue_view.height - self.queue_view.list_view.container.height + self.queue_view.list_view.pos[1]):
                if self.window is not None and self.window._drag_payload is not None:
                    play_queue.add_track(self.window._drag_payload)
                    self.window.drop()

    def _on_touch_down(self, window, event):
        pass

    def shutdown(self):
        pass
        # self.deck.shutdown()


Builder.load_string(kv_string)
Factory.register('MasterQueue', MasterQueue)
