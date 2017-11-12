from math import cos, acos, pi
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.image import Image

from kivy.properties import ObjectProperty, NumericProperty, AliasProperty
from kivy.factory import Factory
from kivy.graphics import Mesh, Color, Rectangle, Line, RoundedRectangle, Ellipse
from kivy.clock import mainthread, Clock


class VolumeSlider(Widget):

    value = NumericProperty(0)
    step = NumericProperty(0.01)
    min_value = NumericProperty(-1, allownone=True)
    max_value = NumericProperty(1, allownone=True)

    def __init__(self, *args, **kwargs):
        super(VolumeSlider, self).__init__(*args, **kwargs)
        self._redraw = Clock.create_trigger(self.draw_window)
        self.bind(max_value=self._redraw,
                  min_value=self._redraw,
                  value=self._redraw,
                  size=self._redraw,
                  pos=self._redraw)

    def draw_window(self, *args):
        self.canvas.clear()

        with self.canvas:
            Color(0, 0, 0, 1)
            Rectangle(size=self.size,
                      pos=self.pos)

            Color(1, 1, 1, 1)
            Line(points=[self.pos[0], self.pos[1], self.width + self.pos[0], self.pos[1]],
                 width=2)
            Line(points=[self.pos[0], self.pos[1] + self.height, self.width + self.pos[0], self.pos[1] + self.height],
                 width=2)
            Color(.7, .7, .7, 1)
            for i in range(1, 10):
                Line(points=[self.pos[0], self.pos[1] + i * self.height / 10,
                             self.width / 3 + self.pos[0], self.pos[1] + i * self.height / 10],
                     width=1)
                Line(points=[self.pos[0] + 2 * self.width / 3, self.pos[1] + i * self.height / 10,
                             self.width + self.pos[0], self.pos[1] + i * self.height / 10],
                     width=1)
            Color(1, 1, 1, 1)
            Line(points=[self.pos[0], self.pos[1] + 5 * self.height / 10,
                         self.width / 3 + self.pos[0], self.pos[1] + 5 * self.height / 10],
                 width=2)
            Line(points=[self.pos[0] + 2 * self.width / 3, self.pos[1] + 5 * self.height / 10,
                         self.width + self.pos[0], self.pos[1] + 5 * self.height / 10],
                 width=2)

            Color(.5, .5, .5, 1)
            Line(points=[self.pos[0] + self.width / 2, self.pos[1],
                         self.width / 2 + self.pos[0], self.pos[1] + self.height],
                 width=3)

            Color(1, 1, 1, 1)
            Rectangle(source='atlas://pydjay/gui/images/resources/volume-slider-knob',
                      pos=(self.pos[0] + self.width / 2 -
                           (self.width - 5) / 2, self.value_pos[1] - 10),
                      size=(self.width - 5, 20))

    def get_vol_value(self):
        d = -0.5 * (cos(pi * self.value_normalized) - 1.0)
        if d == 0:
            return 0
        if d <= 0.5:
            return 2 * d
        else:
            return 14 * (d - 0.5) + 1

    def set_vol_value(self, value):

        if value <= 1:
            x = value / 2
        else:
            x = (value - 1) / 14.0 + 0.5

        v_n = acos(1 - 2 * (x)) / pi
        self.value_normalized = v_n
    volume = AliasProperty(get_vol_value, set_vol_value,
                           bind=('value', 'min_value', 'max_value', 'step'))

    def get_norm_value(self):
        vmin = self.min_value
        d = self.max_value - vmin
        if d == 0:
            return 0
        return (self.value - vmin) / float(d)

    def set_norm_value(self, value):
        vmin = self.min_value
        vmax = self.max_value
        step = self.step
        val = min(value * (vmax - vmin) + vmin, vmax)
        if step == 0:
            self.value = val
        else:
            self.value = min(round((val - vmin) / step) * step + vmin,
                             vmax)
    value_normalized = AliasProperty(get_norm_value, set_norm_value,
                                     bind=('value', 'min_value', 'max_value', 'step'))

    def get_value_pos(self):
        padding = 0
        x = self.x
        y = self.y
        nval = self.value_normalized
        return (x, y + padding + nval * (self.height - 2 * padding))

    def set_value_pos(self, pos):
        padding = 0
        x = min(self.right - padding, max(pos[0], self.x + padding))
        y = min(self.top - padding, max(pos[1], self.y + padding))
        if self.height == 0:
            self.value_normalized = 0
        else:
            self.value_normalized = (y - self.y - padding) / float(self.height - 2 * padding)
    value_pos = AliasProperty(get_value_pos, set_value_pos,
                              bind=('x', 'y', 'width', 'height', 'min_value',
                                    'max_value', 'value_normalized'))

    def on_touch_down(self, touch):
        if self.disabled or not self.collide_point(*touch.pos):
            return
        if touch.is_mouse_scrolling:
            if 'down' in touch.button or 'left' in touch.button:
                if self.step:
                    self.value = min(self.max_value, self.value + self.step)
                else:
                    self.value = min(
                        self.max,
                        self.value + (self.max_value - self.min_value) / 20)
            if 'up' in touch.button or 'right' in touch.button:
                if self.step:
                    self.value = max(self.min_value, self.value - self.step)
                else:
                    self.value = max(
                        self.min_value,
                        self.value - (self.max_value - self.min_value) / 20)
        else:
            touch.grab(self)
            self.value_pos = touch.pos
        return True

    def on_touch_move(self, touch):
        if touch.grab_current == self:
            self.value_pos = touch.pos
            return True

    def on_touch_up(self, touch):
        if touch.grab_current == self:
            self.value_pos = touch.pos
            return True


Factory.register('VolumeSlider', VolumeSlider)


class VolumeLevel(Label):

    value = NumericProperty(0)
    step = NumericProperty(0.01)
    min_value = NumericProperty(-1, allownone=True)
    max_value = NumericProperty(1, allownone=True)

    def __init__(self, *args, **kwargs):
        super(VolumeLevel, self).__init__(*args, **kwargs)
        self._redraw = Clock.create_trigger(self.draw_window)
        self.bind(max_value=self._redraw,
                  min_value=self._redraw,
                  value=self._redraw,
                  size=self._redraw,
                  pos=self._redraw)

    def draw_window(self, *a):
        self.text = "%s%%" % (self.value_normalized * (self.max_value - self.min_value) * 100,)

    def get_vol_value(self):
        d = -0.5 * (cos(pi * self.value_normalized) - 1.0)
        if d == 0:
            return 0

        if d <= 0.5:
            return 2 * d
        else:
            return 14 * (d - 0.5) + 1

    def set_vol_value(self, value):
        if value <= 1:
            x = value / 2
        else:
            x = (value - 1) / 14.0 + 0.5
        v_n = acos(1 - 2 * (x)) / pi
        self.value_normalized = v_n
    volume = AliasProperty(get_vol_value, set_vol_value,
                           bind=('value', 'min_value', 'max_value', 'step'))

    def get_norm_value(self):
        vmin = self.min_value
        d = self.max_value - vmin
        if d == 0:
            return 0
        return (self.value - vmin) / float(d)

    def set_norm_value(self, value):
        vmin = self.min_value
        vmax = self.max_value
        step = self.step
        val = min(value * (vmax - vmin) + vmin, vmax)
        if step == 0:
            self.value = val
        else:
            self.value = min(round((val - vmin) / step) * step + vmin,
                             vmax)
    value_normalized = AliasProperty(get_norm_value, set_norm_value,
                                     bind=('value', 'min_value', 'max_value', 'step'))


Factory.register('VolumeLevel', VolumeLevel)
