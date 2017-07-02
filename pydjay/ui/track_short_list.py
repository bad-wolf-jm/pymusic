from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.factory import Factory
from elements.utils import seconds_to_human_readable
from behaviors.track_list_behaviour import TrackListBehaviour
from pydjay.bootstrap import play_queue, session_manager

kv_string = """
#:import label kivy.uix.label
#:import sla kivy.adapters.simplelistadapter
#:import SimpleDetailedListItem pydjay.ui.elements.simple_detailed_list_item.SimpleDetailedListItem
#:import SimpleTrackCardItem pydjay.ui.elements.simple_track_card_item.SimpleTrackCardItem
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

        HDivider:
        LargeTrackList:
            id: short_list
            size_hint: 1,1
            item_class: SimpleTrackCardItem
            item_convert: root._convert_sl
            on_touch_up: root._on_touch_up(*args)
            on_touch_down: root._on_list_touch_down(*args)
"""


class DragContext:
    def __init__(self, drag, drop):
        self.drag = drag
        self.drop = drop


class TrackShortList(BoxLayout, TrackListBehaviour):
    master_list = ObjectProperty(None)
    short_list = ObjectProperty(None)
    preview_player = ObjectProperty(None)
    search_filter = ObjectProperty(None)
    total_track_count = StringProperty("")
    title = StringProperty("")

    def __init__(self, *args, **kwargs):
        super(TrackShortList, self).__init__(*args, **kwargs)
        Clock.schedule_once(self._post_init, -1)
        self.drag_context_sl = DragContext(self._start_drag_sl, self._drop_sl)
        self.has_focus = False
        self._current_selection = None
        self.set_keyboard_handlers({'shift+up':        self._move_selection_up,
                                    'shift+down':      self._move_selection_down,
                                    'shift+t':         self._move_selection_to_top,
                                    'shift+backspace': self._delete_selection,
                                    'shift+q':         self._add_selection_to_queue})

    def _post_init(self, *args):
        self.short_list.adapter.bind(data=self._update_sl_track_count)
        self.short_list.bind(adapter=self._update_sl_track_count)
        play_queue.bind(on_queue_content_change=self._update_availability)
        session_manager.bind(on_current_session_changed=self._update_availability)
        self.preview_player.window = self.window
        self.preview_player.player = self.window._preview_player
        self.preview_player.volume_controls = self.window._volume_control
        self.adapter = self.short_list.adapter
        self.list_view = self.short_list.list_view
        self.list_view.layout_manager.default_size = 60

    def _update_availability(self, *args):
        self.short_list.update_availability(self._track_is_available)

    def show_preview_player(self, track, pos, size):
        self.window.show_preview_player(track, pos, size, 'left')

    def preview_track(self, track):
        self.preview_player.play(track)

    def _move_selection_up(self):
        item = self.current_selection
        if item is not None:
            index = max(min(self._current_selection - 1, len(self.adapter.data)), 0)
            self.short_list.remove_track(item['item'])
            self.add_shortlist_track(item['item'].track, index)
            self.select(index)

    def _move_selection_down(self):
        item = self.current_selection
        if item is not None:
            index = max(min(self._current_selection + 1, len(self.adapter.data)), 0)
            self.short_list.remove_track(item['item'])
            self.add_shortlist_track(item['item'].track, index)
            self.select(index)

    def _move_selection_to_top(self):
        item = self.current_selection
        if item is not None:
            self.short_list.remove_track(item['item'])
            self.add_shortlist_track(item['item'].track, 0)
            self.select(self._current_selection)

    def _delete_selection(self):
        item = self.current_selection
        if item is not None:
            self.short_list.remove_track(item['item'])
            self.select(self._current_selection)

    def _add_selection_to_queue(self):
        item = self.current_selection
        if item is not None:
            self.short_list.remove_track(item['item'])
            self.queue.add_track(item['item'].track)

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

    def _update_sl_track_count(self, *args):
        num = len(self.short_list.adapter.data)
        time = 0

        track_count_text = self.title
        if num > 0 and track_count_text != "":
            track_count_text += " - "
        # else:
        for t in self.short_list.adapter.data:
            try:
                time += t['item'].track.info.length
            except:
                pass
        track_count_text += "[color=#ffffff]" + str(num) + " tracks " + "[/color]" + \
                            "[color=#444444] | [/color]" + \
                            "[color=#888888]" + \
            seconds_to_human_readable(time / 1000000000) + "[/color]"
        self.sl_track_count.text = track_count_text
        return True

    def _on_list_touch_down(self, window, event):
        pass

    def set_track_list(self, list, sort=True):
        self.short_list.set_track_list(list, sort, self._track_is_available)
        self._update_sl_track_count()
        num = len(self.short_list.adapter.data)
        time = 0
        if num == 0:
            self.total_track_count = ""
        else:
            for t in self.short_list.adapter.data:
                try:
                    time += t['item'].track.info.length
                except:
                    pass
            self.total_track_count = "[color=#ffffff]" + str(num) + " tracks " + "[/color]" + \
                                     "[color=#444444] | [/color]" + \
                                     "[color=#888888]" + \
                seconds_to_human_readable(time / 1000) + "[/color]"


Builder.load_string(kv_string)
Factory.register('TrackShortList', TrackShortList)
