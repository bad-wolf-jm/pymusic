#import os

from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.factory import Factory

#from jmc.uix import screen, paged_grid, paged_display
#from jmc.uix import clickable_area
from jmc.uix import  throbber
from kivy.uix.boxlayout import BoxLayout

#from kivy.clock import mainthread

#from mediacentre.skins.default.theme import get_path

from functools import partial
#from threading import Thread

#from os.path import getsize
#from datetime import datetime
#import re
#import mimetypes

kv_string = """
#:import get_path mediacentre.skins.default.theme.get_path
<BusyLabel@BoxLayout>:
    text: ""
    text_label: text_label
    font_size: 12
    Label:
        id: text_label
        shorten: True
        #pos: self.parent.pos
        shorten_from: 'center'
        text_size: self.width, None
        text: root.text 
        font_size: root.font_size
"""

class BusyLabel(BoxLayout):
    text_label = ObjectProperty(None)
    def __init__(self, **args):
        super(BusyLabel, self).__init__(**args)
        self.busy_throbber = None


    def get_busy_state(self):
        return not (self.busy_throbber is None)

    def set_busy_state(self, value):
        if value:
            self.start_busy_state()
        else:
            self.stop_busy_state()

    busy = property(get_busy_state, set_busy_state)

    def start_busy_state(self):
        if self.busy_throbber is None:
            self.busy_throbber           = throbber.Throbber()
            self.busy_throbber.size_hint = (None, None)
            throbber_size = self.height - self.padding[1] - self.padding[3]
            self.busy_throbber.size      = (throbber_size, throbber_size)
            self.add_widget(self.busy_throbber)
            self.busy_throbber.start()

    def stop_busy_state(self):
        if self.busy_throbber is not None:
            self.busy_throbber.stop()
            self.remove_widget(self.busy_throbber)
            self.busy_throbber = None

Builder.load_string(kv_string)
Factory.register('BusyLabel', BusyLabel)


if __name__ == '__main__':
    from kivy.base import runTouchApp
    from mediacentre.database.TVShows import database_pickle
    from kivy.core.window import Window
    from kivy.clock import Clock
    from kivy.uix.button import Button
    Window.clearcolor = (0.4,0.4,0.4, 1)
    #Window.width = 350
    #Window.height = 475
    #index = 0
    #def add_item(*a):
    #    global index
    #    index += 1
    #    #print index
    #    item = Button(text= '%s'%index)
    #    bar.add_page(item)
        
    #def _foo(*a):
    #    Clock.schedule_interval(add_item, 1)
    #db = database_pickle.Database('/Users/jihemme/mediaserver_data')
    #from kivy.clock import Clock
    #foo = AnchorLayout(size_hint = (1,1), anchor_x = 'center', anchor_y = 'center')
    #init_gui()
    foo = BoxLayout(orientation = 'vertical')
    bar = BusyLabel(size_hint = (1,None), height = 30, padding = [5,5])#size = (450,550))
    egg = Button(on_press = lambda *a: bar.set_busy_state(not bar.busy))
    bar.text = "SOME TEXT"
    #bar.start_busy_state()
    foo.add_widget(bar)
    foo.add_widget(egg)
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
    runTouchApp(foo)#size=(400,200)))#, size_hint = (None, None)))
    #bar.unload()
