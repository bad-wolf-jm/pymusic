import os
import sys
import traceback
from kivy.event import EventDispatcher
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivy.core.window import Window
import pydjay.core.keyboard
from pydjay.bootstrap import play_queue, session_manager, playback_manager


class TrackListBehaviour(EventDispatcher):
    has_focus = BooleanProperty(False)
    dim_unavailable_tracks = BooleanProperty(True)
    fixed_item_positions = BooleanProperty(True)
    can_delete_items = BooleanProperty(False)
    can_add_selection_to_queue = BooleanProperty(True)
    adapter = ObjectProperty(None)
    queue = ObjectProperty(None)
    window = ObjectProperty(None)
    list_view = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        super(TrackListBehaviour, self).__init__(*args, **kwargs)
        self._focus = False
        self._keyboard = None
        self._keyboard_handlers = {'up':              self._on_up_arrow,
                                   'down':            self._on_down_arrow,
                                   'shift+up':       self._on_shift_up_arrow,
                                   'shift+down':     self._on_shift_down_arrow,
                                   'shift+u':        self._make_selection_unavailable,
                                   'shift+a':        self._make_selection_available,
                                   'enter':           self._preview_current_selection,
                                   'u':               self._move_selection_up,
                                   'd':               self._move_selection_down,
                                   't':               self._move_selection_to_top,
                                   'shift+backspace': self._delete_selection}
        self._current_selection = None

    def focus(self):
        self.has_focus = True
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self, 'text')
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        if self._current_selection is not None:
            row = self._current_selection
            row = max(min(row, len(self.adapter.data) - 1), 0)
            try:
                v = self.adapter.get_view(row)
                if v is not None:
                    v._update_background()
                self._current_selection = row
            except IndexError:
                self._current_selection = None

    def unfocus(self):
        self.has_focus = False
        if self._keyboard is not None:
            self._keyboard.release()
        if self._current_selection is not None:
            row = self._current_selection
            row = max(min(row, len(self.adapter.data) - 1), 0)
            try:
                v = self.adapter.get_view(row)
                if v is not None:
                    v._update_background()
                self._current_selection = row
            except IndexError:
                self._current_selection = None

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def set_keyboard_handlers(self, d):
        self._keyboard_handlers.update(d)

    @property
    def current_selection(self):
        if self._current_selection is not None:
            try:
                return self.adapter[self._current_selection]
            except:
                return None
        return None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        key_seq = "+".join(modifiers + [keycode[1]])
        if key_seq in self._keyboard_handlers:
            try:
                self._keyboard_handlers[key_seq]()
            except Exception, details:
                print "ERROR HANDLING KEY SEQUENCE", details
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print '-' * 60
                traceback.print_exc(file=sys.stdout)
                print '-' * 60
                print details
        else:
            pydjay.core.keyboard.key_map.key_pressed(keycode, modifiers)

    def select(self, row):
        if len(self.adapter.data) == 0:
            self._current_selection = None
            return

        row = max(min(row, len(self.adapter.data) - 1), 0)
        if self._current_selection is not None:
            try:
                item = self.adapter[self._current_selection]
                item['item'].is_selected = False
                self.adapter.get_view(self._current_selection)._update_background()
            except IndexError:
                pass
        try:
            item = self.adapter[row]
            self.list_view.layout_manager.show_index_view(row)
            item['item'].is_selected = True
            self.adapter.get_view(row)._update_background()
            self._current_selection = row
            self.window.request_focus(self)
        except IndexError:
            self._current_selection = None
            pass

    def _track_is_available(self, track):
        if self.dim_unavailable_tracks:
            is_available = True
            is_available = is_available and not play_queue.contains(track.location)
            is_available = is_available and session_manager.is_available(track)
            if playback_manager.track is not None:
                return is_available and playback_manager.track.location != track.location
            return is_available
        return True

    def _move_selection(self, amount):
        if self._current_selection is not None:
            self.select(self._current_selection + amount)
        else:
            self.select(0)

    def _on_down_arrow(self):
        self._move_selection(1)

    def _on_shift_down_arrow(self):
        self._move_selection(20)

    def _on_up_arrow(self):
        self._move_selection(-1)

    def _on_shift_up_arrow(self):
        self._move_selection(-20)

    def _make_selection_unavailable(self):
        item = self.current_selection
        if item is not None:
            session_manager.add(item['item'].track, False)

    def _make_selection_available(self):
        item = self.current_selection
        if item is not None:
            session_manager.remove(item['item'].track)

    def _preview_current_selection(self):
        item = self.current_selection
        if item is not None:
            self.preview_player.play(item['item'].track)

    def _move_selection_up(self):
        item = self.current_selection
        if item is not None and not self.fixed_item_positions:
            index = max(min(self._current_selection - 1, len(self.adapter.data)), 0)
            self.remove_track(item['item'])
            self.add_track(item['item'].track, index, self._track_is_available)
            self.select(index)

    def _move_selection_down(self):
        item = self.current_selection
        if item is not None and not self.fixed_item_positions:
            index = max(min(self._current_selection + 1, len(self.adapter.data)), 0)
            self.remove_track(item['item'])
            self.add_track(item['item'].track, index, self._track_is_available)
            self.select(index)

    def _move_selection_to_top(self):
        item = self.current_selection
        if item is not None and not self.fixed_item_positions:
            self.remove_track(item['item'])
            self.add_track(item['item'].track, 0, self._track_is_available)
            self.select(self._current_selection)

    def _delete_selection(self):
        item = self.current_selection
        if item is not None and self.can_delete_items:
            self.remove_track(item['item'])
            self.select(self._current_selection)

    def _add_selection_to_queue(self):
        item = self.current_selection
        if item is not None and self.can_add_selection_to_queue:
            self.queue.add_track(item['item'].track)
