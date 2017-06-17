import os
from os.path import getsize
from datetime import datetime

from kivy.event import EventDispatcher
from kivy.clock import mainthread, Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.factory import Factory
#from pydjay.gui.utils import seconds_to_human_readable

from pydjay.ui.elements.utils import seconds_to_human_readable


from kivy.core.window import Window
from pydjay.ui.elements import large_track_list
from pydjay.ui.behaviors.track_list_behaviour import TrackListBehaviour
from pydjay.bootstrap import play_queue, session_manager
import pydjay.bootstrap

kv_string = """
#:import PlaylistItem pydjay.ui.dialogs.playlist_list_item.PlaylistItem
<PlaylistList>:
    orientation: 'horizontal'
    size_hint: 1,1
    #master_list: master_list
    #preview_player: preview_player
    short_list: short_list
    #sl_track_count:sl_track_count
    button_size: 45

    LargeTrackList:
        id: short_list
        size_hint: 1,1
        item_class: PlaylistItem
        item_convert: root._convert_sl
        on_touch_up: root._on_touch_up(*args)
        on_touch_down: root._on_list_touch_down(*args)
"""


class DragContext:
    def __init__(self, drag, drop):
        self.drag = drag
        self.drop = drop


class PlaylistList(BoxLayout, TrackListBehaviour):
    master_list = ObjectProperty(None)
    dim_unavailable_tracks = ObjectProperty(None)
    short_list = ObjectProperty(None)
    preview_player = ObjectProperty(None)
    search_filter = ObjectProperty(None)
    total_track_count = StringProperty("")
    title = StringProperty("")

    def __init__(self, *args, **kwargs):
        super(PlaylistList, self).__init__(*args, **kwargs)
        Clock.schedule_once(self._post_init, -1)
        self.drag_context_sl = DragContext(self._start_drag_sl, self._drop_sl)
        self.has_focus = False
        self._current_selection = None
        self.mobile_selection = True

    def _post_init(self, *args):
        play_queue.bind(on_queue_content_change=self._update_availability)
        session_manager.bind(on_current_session_changed=self._update_availability)
        self.adapter = self.short_list.adapter
        self.list_view = self.short_list.list_view
        self.list_view.layout_manager.default_size = 60

    def _update_availability(self, *args):
        self.short_list.update_availability(self._track_is_available)

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
        self.master_list.do_filter(text)

    def _on_touch_up(self, window, event):
        if self.short_list.list_view.collide_point(*event.pos):
            if len(self.short_list.adapter.data) == 0 or \
               (event.pos[1] < self.short_list.list_view.height - self.short_list.list_view.container.height + self.short_list.list_view.pos[1]):
                if self.window is not None and self.window._drag_payload is not None:
                    self.add_shortlist_track(self.window._drag_payload)
                    self.window.drop()

    def add_shortlist_track(self, track, index=None):
        self.short_list.add_track(track, index, self._track_is_available)

    def _convert_sl(self, row, item):
        return {'row': row,
                'item': item,
                'view': self,
                'drag_context': self.drag_context_sl,
                'is_selected': False}

    def _on_list_touch_down(self, window, event):
        pass

    def set_track_list(self, list, sort=True):
        self.short_list.set_track_list(list, sort, self._track_is_available)


Builder.load_string(kv_string)
Factory.register('PlaylistList', PlaylistList)
