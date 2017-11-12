

import os
import re
import mimetypes

from functools import partial
from threading import Thread
from os.path import getsize
from datetime import datetime

from kivy.properties import NumericProperty, BooleanProperty,\
    BoundedNumericProperty, StringProperty, ListProperty, ObjectProperty,\
    DictProperty, AliasProperty

from kivy.clock import Clock

from kivy.graphics import Mesh, Color, Rectangle, Line

from kivy.clock import mainthread
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.stencilview import StencilView
from kivy.properties import ObjectProperty
from kivy.factory import Factory

from kivy.graphics import Line, RenderContext

from kivy.uix.relativelayout import RelativeLayout


electric_blue = [44.0 / 255, 117.0 / 255, 255.0 / 255, .7]
purple = [137.0 / 255, 59.0 / 255, 255 / 255, .7]
purple_2 = [127.0 / 255, 56.0 / 255, 236.0 / 255, 1]
purple_3 = [176.0 / 255, 65.0 / 255, 255.0 / 255, .7]
green_1 = [84.0 / 255, 185.0 / 255, 213.0 / 255, .7]
gray_1 = [.7, .7, .7, .7]
gray_2 = [.5, .5, .5, .5]


class WaveformVisualize(StencilView):
    color = ListProperty(purple_2)
    points = ListProperty([])
    x_min = ObjectProperty(None)
    x_max = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        super(WaveformVisualize, self).__init__(*args, **kwargs)
        self.ask_redraw = Clock.create_trigger(self.draw_waveform)
        self.bind(width=self.ask_redraw,
                  size=self.ask_redraw,
                  x_max=self.ask_redraw,
                  x_min=self.ask_redraw,
                  points=self.ask_redraw,
                  height=self.ask_redraw)

    def draw_waveform(self, *args):
        points = []
        self.canvas.clear()
        with self.canvas:
            Color(*self.color)
            for x, y in self.iterate_points():
                Line(points=[x, y[0], x, y[1]], width=1, joints='round')

    def iterate_points(self):
        '''Iterate on all the points adjusted to the graph settings
        '''

        if len(self.points) > 0:
            if self.x_min is not None:
                sample_min_x = self.x_min
            else:
                sample_min_x = self.points[0][0]

            if self.x_max is not None:
                sample_max_x = self.x_max
            else:
                sample_max_x = self.points[-1][0]

            sample_min_y = self.points[0][1]
            sample_max_y = self.points[0][1]

            for x, y in self.points:
                if y > sample_max_y:
                    sample_max_y = y
                if y < sample_min_y:
                    sample_min_y = y

            zero_y = self.height / 2 + self.y
            y_amplitude = sample_max_y - sample_min_y
            y_factor = float(self.height) / y_amplitude

            zero_x = self.x  # self.height / 2
            x_amplitude = sample_max_x - sample_min_x
            x_factor = float(self.width) / x_amplitude

            scaled = {}
            c_p = 0
            for x, y in self.points:
                v_x = int(x * x_factor + zero_x)
                v_y = y * y_factor + zero_y
                if v_x not in scaled:
                    scaled[v_x] = [v_y, v_y]
                else:
                    ll = scaled[v_x]
                    if v_y < ll[0]:
                        ll[0] = v_y
                    if v_y > ll[1]:
                        ll[1] = v_y

            return [(p, scaled[p]) for p in sorted(scaled.keys())]
        else:
            return []



# Builder.load_string(kv_string)
Factory.register('WaveformVisualize', WaveformVisualize)

kv_string = """
<WaveformSeekbar>
    waveform: visualizer
    size_hint: 1,1
    BoxLayout:
        orientation: 'vertical'
        size_hint: 1,1
        Widget:
            size_hint: 1, None
            height: 5
        #StencilView:
        #    size_hint: 1,1

        WaveformVisualize:
            id: visualizer
            size_hint: 1,1

        Widget:
            size_hint: 1, None
            height: 5

    Widget:
        size_hint: None, 1
        width: 1
        pos: float(root.value - root.min_value) / (root.max_value - root.min_value)*root.width ,0
        canvas:
            Color:
                rgba: .7,.7,.7, 1 
            Rectangle:
                pos: self.pos
                size: 2, self.height
                #points: [self.pos[0], self.pos[1], self.pos[0], self.pos[1]+self.height]

"""

#84, 197, 113
#176, 65, 255


class WaveformSeekbar(RelativeLayout):
    waveform = ObjectProperty(None)
    min_value = NumericProperty(0)
    max_value = NumericProperty(100)
    value = NumericProperty(0)

    def __init__(self, *args, **kwargs):
        super(WaveformSeekbar, self).__init__(*args, **kwargs)


Builder.load_string(kv_string)
Factory.register('WaveformSeekbar', WaveformSeekbar)
