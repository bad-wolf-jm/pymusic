from kivy.event import EventDispatcher
from kivy.clock import mainthread, Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.adapters.simplelistadapter import SimpleListAdapter
from kivy.adapters.listadapter import ListAdapter
from kivy.factory import Factory
from kivy.graphics import *


from clickable_area import ImageButton
from drag_item import DragItem
from default_track_list_item import DefaultTrackItemView
from track_data import TrackData

kv_string = """
#:import label kivy.uix.label
#:import sla kivy.adapters.simplelistadapter
<TrackList>:
    orientation: 'horizontal'
    size_hint: 1,1
    list_view: list
    list_header: header
    BoxLayout:
        orientation: 'vertical'
        RelativeLayout:
            id: header
            size_hint: 1, None
            height: 35
        HDivider:

        ListView:
            id: list
            size_hint: 1,1
            #on_touch_down: root._on_list_touch_down(*args)
"""


class TrackList(BoxLayout):
    list_view = ObjectProperty(None)
    window = ObjectProperty(None)
    adapter = ObjectProperty(None)
    item_class = ObjectProperty(None)
    item_convert = ObjectProperty(None)
    list_header = ObjectProperty(None)
    player = ObjectProperty(None, allownone=True)

    def __init__(self, *args, **kwargs):
        super(TrackList, self).__init__(*args, **kwargs)

        self._unfiltered_list = []
        self._filter_text = ""
        self._filter_cache = {}
        self._current_selection = None

        self.adapter = ListAdapter(
            cls=DefaultTrackItemView,
            data=[],
            selection_mode='none',
            allow_empty_selection=True,
            args_converter=self._convert
        )

        Clock.schedule_once(self._post_init, 0)
        self.bind(item_class=self._update_adapter)
        self.bind(item_convert=self._update_adapter)
        self.bind(player=self._update_player)

    def _post_init(self, *args):
        self.list_view.adapter = self.adapter

    def _update_player(self, i, value):
        self.player.bind(track=self._update_filter)

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
        return {'row': row, 'item': item, 'view': self, 'window': self.window}

    def _update_adapter(self, window, value):
        data = self.adapter.data
        self.adapter = ListAdapter(
            cls=self.item_class if self.item_class is not None else DefaultTrackItemView,
            data=[],
            selection_mode='none',
            allow_empty_selection=False,
            args_converter=self.item_convert if self.item_convert is not None else self._convert
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

    def update_availability(self, available=None):
        for track in self._unfiltered_list:
            if available is not None:
                # print type(track)
                track.is_available = available(track.track)

    def _on_touch_up(self, window, event):
        if self.collide_point(*event.pos):
            if len(self.shortlist_adapter.data) == 0 or \
               (event.pos[1] < self.short_list.height - self.short_list.container.height + self.short_list.pos[1]):
                if self.window is not None and self.window._drag_payload is not None:
                    self.accept_drop_payload()

    def set_track_list(self, list, sort=True, available=None):
        ll = []
        foo = sorted(list) if sort else list
        bar = [TrackData(x) for x in foo]
        for x in bar:
            if available is not None:
                x.is_available = available(x.track)
            else:
                x.available = True
            x.bind(is_selected=self._update_selection)

        self._unfiltered_list = bar
        self.adapter.data = bar

    def _update_selection(self, obj, value):
        # print obj, value
        if value is False:
            if obj == self._current_selection:
                self._current_selection = None
        else:
            if self._current_selection != obj:
                self._current_selection = obj

    def get_full_track_list(self):
        return [x.track for x in self._unfiltered_list]

    def add_track(self, track, index=None, is_available=None):
        foo = TrackData(track)
        if is_available is not None:
            foo.is_available = is_available(track)
        if index is not None:
            self._unfiltered_list.insert(index, foo)
        else:
            self._unfiltered_list.append(foo)
        self.do_filter(self._filter_text)

    def remove_track(self, track_data):
        self._unfiltered_list.remove(track_data)
        self.do_filter(self._filter_text)

    def sort(self):
        self._unfiltered_list.sort()
        self.do_filter(self._filter_text)


Builder.load_string(kv_string)
Factory.register('TrackList', TrackList)
