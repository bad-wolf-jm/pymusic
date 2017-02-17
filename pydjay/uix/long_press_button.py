import os
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.clock import Clock
#from jmc.uix import screen, paged_grid, paged_display
#from jmc.uix import clickable_area

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors.button import ButtonBehavior

#from mediacentre.skins.default.theme import get_path

from functools import partial

kv_string = """
#:import get_path mediacentre.skins.default.theme.get_path
<LongPressButton@ClickableArea>:
    image: get_path("transparent_image")
    background_normal: get_path("transparent_image")
    label_text: ""
    font_size: 12
    anchor_y: 'center'
    image_width: 64
    image_height: 64
    file_name: ""
    file_size: ""
"""
from time import time


class LongPressButtonBehaviour(object):
    def __init__(self, **args):
        super(LongPressButtonBehaviour, self).__init__(**args)
        #self.path = path
        #self._name = name
        #self.set_file(path)
        #self._cb = callback
        ##print callback, path, name
        #self._time_since_last_press = None
        self._click = False
        self._long_press_threshold = .75
        self._long_press_trigger = None
        self._last_press_event   = None
        self._last_release_event = None
        self.register_event_type('on_long_press')
        self.register_event_type('on_click')
        
        self.bind(on_touch_down  = self._do_press,
                  on_touch_up = self._do_release)
        
    def _long_press(self, x, y, *args):
        #print args
        self.dispatch('on_long_press', x, y)
        self._click = False
        #print "LONG PRESS"
        
    def _do_press(self, window, event):
        self._click = True
        if not self.collide_point(*event.pos):
            return False
        if event != self._last_press_event:
            self._long_press_trigger = partial(self._long_press, event.pos[0], event.pos[1])
            Clock.schedule_once(self._long_press_trigger, self._long_press_threshold)
            #print " HERE Button Pressed"
            self._last_press_event = event
        
    def _do_release(self, window, event):
        if not self.collide_point(*event.pos):
            return False

        if event != self._last_release_event:
            if self._long_press_trigger is not None:
                Clock.unschedule(self._long_press_trigger)
                self._long_press_trigger = None
            self._last_release_event = event
            if self._click:
                self.dispatch('on_click')
                self._clock = False
                #print "Button Released"
                

    def on_long_press(self, *a):
        pass
    
    def on_click(self, *a):
        pass

#Builder.load_string(kv_string)

if __name__ == '__main__':
    from kivy.base import runTouchApp
    from mediacentre.database.TVShows import database_pickle
    from kivy.core.window import Window
    from kivy.clock import Clock
    from kivy.uix.button import Button
## red background color
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
    
    bar = LongPressButton(size_hint = (1,1))#size = (450,550))
    #bar.set_path('/Users/jihemme/Downloads')
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
