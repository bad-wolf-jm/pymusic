from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.factory import Factory
from pydjay.ui.elements.drag_item import DragItem


#from kivy.graphics import *

win_str = """
<MainWindow>
    on_touch_move: self._on_touch_move(*args)
    on_touch_up: self._on_touch_up(*args)
    on_touch_down: self._on_touch_down(*args)
"""

Builder.load_string(win_str)


class MainWindow(FloatLayout):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self._is_dragging = False
        self._drag_item = None
        self._drag_payload = None

    def _on_touch_move(self, window, event):
        if self._is_dragging and self._drag_item is not None:
            self._drag_item.center_x = event.pos[0]
            self._drag_item.center_y = event.pos[1]
            return True


    def _delete_all_drag_items(self):
        foo = []
        for x in self.children:
            if isinstance(x, DragItem):
                foo.append(x)
        for y in foo:
            self.remove_widget(y)        

    def drop(self):
        self._drag_item = None
        self._drag_payload = None
        
    def _on_touch_up(self, window, event):
        self._is_dragging = False
        self._delete_all_drag_items()
        
    def _on_touch_down(self, window, event):
        self._drag_payload = None
        self._delete_all_drag_items()
    
    def start_drag(self, pos, track):
        if not self._is_dragging:
            foo = DragItem(track)
            self._drag_payload = track
            self._drag_item = foo
            self.add_widget(foo)
            self._drag_item.center_x = pos[0]
            self._drag_item.center_y = pos[1]
            self._is_dragging = True
