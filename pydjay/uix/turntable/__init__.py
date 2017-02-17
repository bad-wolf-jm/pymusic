import os
from kivy.lang import Builder#from kivy.lang import Builder
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.properties import ObjectProperty

#class AlignedLabel(AnchorLayout):#CompositeListItem):
#    def __init__(self, **args):
#        super(AlignedLabel, self).__init__(**args)
def get_throbber_file():
    return os.path.join(os.path.dirname(__file__), 'throbber.png')

#kv_string = """
##:import join os.path.join
##:import dirname os.path.dirname
#<Throbber@Image>:
#    #source: join(dirname(__file__), 'throbber.gif')
#    #anim_delay: 0.2
#    allow_stretch: True
#    rot_angle: 0
#    keep_ratio: True
#    
#    canvas.before:
#        Color:
#            rgb: (0, 0, 1)
#        PushMatrix
#        Rotate:
#            axis: 0,0,1
#            angle: self.rot_angle
#            origin: self.center
#    #source: "images/butterflybluex.gif"
#    canvas.after:
#        PopMatrix
#"""

#class Throbber(Image):
#    def __init__(self, **kw):
#        super(Throbber, self).__init__(**kw)
#        self.source = get_throbber_file()
#        self.start()
#        
#    def start(self):
#        Clock.schedule_interval(self._do_rotate, 0.1)
#        
#    def stop(self):
#        Clock.unschedule(self._do_rotate)
    
#    def _do_rotate(self, *a):
#        ang = (self.rot_angle - 30)% 360
#        self.rot_angle = ang
#        self.canvas.ask_update()
        
    

#Builder.load_string(kv_string)
#Factory.register('Throbber', Throbber)
