from kivy.clock import mainthread, Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.factory import Factory

from list_view import RecycleView, RecycleAdapter
from pydjay.ui.elements import list_view
from default_track_list_item import DefaultTrackItemView
from track_data import TrackData


kv_string = """
#:import label kivy.uix.label
#:import sla kivy.adapters.simplelistadapter
<LargeTrackList>:
    orientation: 'horizontal'
    size_hint: 1,1
    list_view: list

    RecycleView:
        id: list
        size_hint: 1,1
        #on_touch_down: root._on_list_touch_down(*args)
"""


class ListLayoutManager(list_view.LinearRecycleLayoutManager,
                        list_view.LayoutSelectionMixIn):
    def __init__(self, *args, **kwargs):
        super(ListLayoutManager, self).__init__(*args, **kwargs)
        self.key_selection = ''


class LargeTrackList(BoxLayout):
    list_view = ObjectProperty(None)
    window = ObjectProperty(None)
    adapter = ObjectProperty(None)
    item_class = ObjectProperty(None)
    item_convert = ObjectProperty(None)
    list_header = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        super(LargeTrackList, self).__init__(*args, **kwargs)

        self._unfiltered_list = []
        self._filter_text = ""
        self._filter_cache = {}
        self._current_selection = None
        self.adapter = RecycleAdapter(
            cls=DefaultTrackItemView,
            data=[],
            selection_mode='none',
            allow_empty_selection=True,
            args_converter=self._convert
        )

        Clock.schedule_once(self._post_init, 0)
        self.bind(item_class=self._update_adapter)
        self.bind(item_convert=self._update_adapter)

    def _post_init(self, *args):
        self.list_view.adapter = self.adapter
        self.list_view.layout_manager = ListLayoutManager()

    def _update_filter(self, *a):
        self.do_filter(self._filter_text)

    def do_filter(self, text):
        if text == "":
            self._filter_cache = {}
        self._filter_text = text

        if text in self._filter_cache:
            bar = self._filter_cache[text]
            _conv = self.item_convert if self.item_convert is not None else self._convert
            self.adapter.data = [_conv(i, x) for i, x in zip(range(len(bar)), bar)]
        else:
            self._filter_cache = {}
            foo = text.split(" ")
            bar = [x for x in self._unfiltered_list if x.track.matches(foo)]
            self._filter_cache[text] = bar
            _conv = self.item_convert if self.item_convert is not None else self._convert
            self.adapter.data = [_conv(i, x) for i, x in zip(range(len(bar)), bar)]

    def _convert(self, row, item):
        return {'row':          row,
                'item':         item,
                'view':         self,
                'drag_context': self.window,
                'is_selected':  False}

    def _update_adapter(self, window, value):
        data = self.adapter.data
        self.adapter = RecycleAdapter(
            viewclass=self.item_class,
            data=[],
            selection_mode='none',
            allow_empty_selection=False,
            args_converter=self.item_convert
        )
        self.adapter.data = data
        self.list_view.adapter = self.adapter

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
        _conv = self.item_convert if self.item_convert is not None else self._convert
        self.adapter.data = [_conv(i, x) for i, x in zip(range(len(bar)), bar)]

    def _update_selection(self, obj, value):
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
Factory.register('LargeTrackList', LargeTrackList)
