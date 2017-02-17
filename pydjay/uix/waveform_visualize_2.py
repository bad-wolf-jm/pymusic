


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
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.factory import Factory

from kivy.graphics import Line, RenderContext


electric_blue = [44.0/255, 117.0/255, 255.0/255, .7]
purple = [137.0/255, 59.0/255, 255/255, .7]
purple_2 = [127.0/255, 56.0/255, 236.0/255, .5]
purple_3 = [176.0/255, 65.0/255, 255.0/255, .7]
green_1 = [84.0/255, 185.0/255, 213.0/255, .7]


#84, 197, 113
#176, 65, 255
class WaveformVisualize(Widget):
    color  = ListProperty(purple_2)
    points = ListProperty([])
    x_min = ObjectProperty(None)
    x_max = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        super(WaveformVisualize, self).__init__(*args, **kwargs)
        self.ask_redraw = Clock.create_trigger(self.draw_waveform)
        self.bind(width  = self.ask_redraw,
                  size   = self.ask_redraw,
                  x_max  = self.ask_redraw,
                  x_min  = self.ask_redraw,
                  points = self.ask_redraw,
                  height = self.ask_redraw)

        with self.canvas:
            self._gcolor = Color(*self.color)
            self._gline = Line(points=[], cap='none', width=1, joint='round')


    def draw_waveform(self, *args):
        #super(LinePlot, self).draw(*args)
        # flatten the list
        points = []
        
        for x, y in self.iterate_points():
            #print 'POINT', x, y
            points += [x, y]
        self._gline.points = points       


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

            for x,y in self.points:
                if y > sample_max_y:
                    sample_max_y = y
                if y < sample_min_y:
                    sample_min_y = y


            #print sample_min_x, sample_min_y, sample_max_x, sample_max_y 

            zero_y = self.height / 2 + self.y
            y_amplitude = sample_max_y - sample_min_y
            y_factor = float(self.height) / y_amplitude

            zero_x      = self.x#self.height / 2 
            x_amplitude = sample_max_x - sample_min_x
            x_factor    = float(self.width) / x_amplitude

            #print 'X DATA', zero_x, x_amplitude, x_factor, sample_max_x, sample_min_x, x, x * x_factor + zero_x

            for x, y in self.points:
                yield (x * x_factor + zero_x, y * y_factor + zero_y)#+self.height / 2)


            
#Builder.load_string(kv_string)
#Factory.register('WaveformVisualize', WaveformVisualize)
buffer = []

if __name__ == '__main__':

    from random import randint, random
    ## red background color
    #from jmc.gui import config

    import gi
    import pprint
    import sys
    import urllib
    gi.require_version("Gst", "1.0")
    #gi.require_version('Gtk', '3.0')
    from gi.repository import Gst, GObject as gobject, GLib
    
    from struct import unpack_from

    
    Gst.init(None)     
    gobject.threads_init()

    from kivy.base import runTouchApp
    #from mediacentre.database.TVShows import database_pickle
    from kivy.core.window import Window
    from kivy.clock import Clock
    from kivy.uix.button import Button


    from pydjay.audio.wavegen import WaveformGenerator


    #print "HERE"
    Window.clearcolor = (0,0,0, 1)
    #Window.width = 350
    #Window.height = 475
    Window.size = (700, 150)
    #index = 0
    #def add_item(*a):
    #    global index
    #    index += 1
    #    #print index
    #    item = Button(text= '%s'%index)
    #    bar.add_page(item)
    from math import*
    Fs=8000
    f=50
    sample=30000
    a=[0]*sample
    for n in range(sample):
        a[n]=(n, random() * sin(2*pi*randint(1, 1000)*n/Fs))
    #def _foo(*a):
    #    Clock.schedule_interval(add_item, 1)
    #db = database_pickle.Database('/Users/jihemme/mediaserver_data')
    #from kivy.clock import Clock
    #foo = AnchorLayout(size_hint = (1,1), anchor_x = 'center', anchor_y = 'center')
    #init_gui()
    foo = WaveformGenerator("/Users/jihemme/Python/DJ/pydjay/audio/test.mp3", 45000)


   

    
    def add_point(total_time, timestamp, value):
        global buffer
        bar.x_max = total_time
        buffer.append((timestamp, value))
        if len(buffer) == 150:
            bar.points.extend(buffer)
            buffer = []

            
    def done_points(points):
        bar.points = points
        #x = open('ttt.txt','w')
        #x.write(str(points))
        #x.close()
    foo.set_data_point_callback(add_point)
    foo.set_process_done_callback(done_points)
    
    bar = WaveformVisualize()#Builder.load_string(kv_string)#FilesScreen(size_hint = (1,1))#size = (450,550))
    #print a
    bar.points = foo.get_data_points()
    #bar.location_browser.set_default_locations()
    #bar.set_list(locations)
    #add_item()
    #add_item()
    
    #add_item()
    
    #add_item()
    
    #add_item()
    #Clock.schedule_once(add_item, 5)
    #button = Button(test="FOO",size_hint = (1,1))
    #bar.set_seasons(12)
    #bar.set_episodes(123, 45)
    #foo.add_widget(bar)
    #foo.add_widget(button)
    #button.bind(on_press = lambda *x: 
    #bar.set_show(db.get_tv_show('stargate-sg-1'))#db.get_tv_shows())
    runTouchApp(bar)#size=(400,200)))#, size_hint = (None, None)))
    bar.unload()
