import os
from kivy.lang import Builder#from kivy.lang import Builder
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.properties import ObjectProperty

from kivy.uix.relativelayout import RelativeLayout


#class AlignedLabel(AnchorLayout):#CompositeListItem):
#    def __init__(self, **args):
#        super(AlignedLabel, self).__init__(**args)
def get_throbber_file():
    return os.path.join(os.path.dirname(__file__), 'throbber.png')

kv_string = """
#:import join os.path.join
#:import dirname os.path.dirname
<Rotator>:
    #source: join(dirname(__file__), 'throbber.gif')
    #anim_delay: 0.2
    #allow_stretch: True
    rot_angle: 0
    rot_speed: 45 #rpm
    canvas.before:
        Color:
            rgb: (0, 0, 1)
        PushMatrix
        Rotate:
            axis: 0,0,1
            angle: self.rot_angle
            origin: self.center
    canvas.after:
        PopMatrix
"""

class Rotator(RelativeLayout):
    def __init__(self, **kw):
        super(Rotator, self).__init__(**kw)
        self.source = get_throbber_file()
        #self.start()
        
    def start(self):
        Clock.schedule_interval(self._do_rotate, 0.05)
        
    def stop(self):
        Clock.unschedule(self._do_rotate)

    def reset(self):
        self.rot_angle = 0
    
    def _do_rotate(self, *a):
        # fps = 1 / 0.05
        ang = (self.rot_angle - self.rot_speed * 6 * 0.05) % 360
        #print self.rot_speed * 60 
        self.rot_angle = ang
        self.canvas.ask_update()
        
    

Builder.load_string(kv_string)
Factory.register('Rotator', Rotator)


kv_string = """
Rotator:
    Image:
        size_hint: 1,None
 
        #pos_hint: {'x': None, 'y': None}
        height: self.parent.height + 8
        pos: 0, -4
        keep_ratio: True
        allow_stretch: True
        source: 'pydjay/uix/turntable/blank_disk.png'

"""


if __name__ == '__main__':
    from kivy.base import runTouchApp
    #from mediacentre.database.TVShows import database_pickle
    from kivy.core.window import Window
    from kivy.clock import Clock
    from kivy.uix.button import Button
    ## red background color
    #from jmc.gui import config
    #print(kivy.__version__)
    Window.clearcolor = (0.2,0.2,0.2, 1)
    Window.size = (250, 250)
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
    
    bar = Builder.load_string(kv_string)#FilesScreen(size_hint = (1,1))#size = (450,550))
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
