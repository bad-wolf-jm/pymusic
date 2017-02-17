from math import cos, acos, pi
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget
from kivy.uix.image import Image

from kivy.properties import ObjectProperty, NumericProperty, AliasProperty
from kivy.factory import Factory
from kivy.graphics import Mesh, Color, Rectangle, Line, RoundedRectangle, Ellipse
from kivy.clock import mainthread, Clock


class VolumeSlider(Widget):
    
    value     = NumericProperty(0)
    step      = NumericProperty(0.01)
    min_value = NumericProperty(-1, allownone = True)
    max_value = NumericProperty(1, allownone = True)

    def __init__(self, *args, **kwargs):
        super(VolumeSlider, self).__init__(*args, **kwargs)
        self._redraw = Clock.create_trigger(self.draw_window)
        #self._cursor = Image(source = 'atlas://pydjay/gui/images/resources/volume-slider-knob')
        #self._cursor.size_hint = (1, 1)
        #self.add_widget(self._cursor)
        self.bind(max_value  = self._redraw,
                  min_value  = self._redraw,
                  value      = self._redraw,
                  size       = self._redraw,
                  pos        = self._redraw)



    """
    def draw_window_2(self, *args):
        self.canvas.clear()
        #self._cursor.width = self.width - 10
        #self._cursor.height = 15
        #self._cursor.center_x = self.width /2
        #self._cursor.center_y = 25 
        #zero_x      = self.x 
        #x_factor    = float(self.width) / self.track_length if self.track_length is not 0 else 1
        #track_start = self.track_start if self.track_start is not None else 0
        #track_end   = self.track_end if self.track_end is not None else self.track_length
        
        with self.canvas:
            Color(0,0,0,1)
            Rectangle(size = self.size,#(track_start * x_factor,
                             # self.height),
                      pos = self.pos)

            Color(1,1,1,1)
            Line(points = [0,0,self.width+0, 0],
                 width = 2)
            Line(points = [0,0+self.height,self.width+0, 0+self.height],
                 width = 2)
            Color(.7, .7, .7, 1)
            for i in range(1, 10):
                Line(points = [0, 0 + i * self.height / 10 ,
                               self.width / 3 + 0, 0 + i * self.height / 10],
                     width = 1)
                Line(points = [0 + 2*self.width / 3, 0+ i * self.height / 10 ,
                               self.width + 0, 0 + i * self.height / 10 ],
                     width = 1)
            Color(1, 1, 1, 1)
            Line(points = [0, 0 + 5 * self.height / 10 ,
                           self.width / 3 + 0, 0 + 5 * self.height / 10],
                 width = 2)
            Line(points = [0 + 2*self.width / 3, 0+ 5 * self.height / 10 ,
                           self.width + 0, 0 + 5 * self.height / 10 ],
                 width = 2)
                


            #window_end = (self.track_length - track_end) * x_factor
            #Rectangle(size = (window_end, self.height),
            #          pos = [0 + self.width - window_end, 0])
            Color(.5, .5, .5, 1)
            Line(points = [0 + self.width / 2, 0 + 10 ,
                           self.width / 2 + 0, 0 + self.height - 10],
                 width = 3)
            Color(1,1,1, 1)
            Rectangle(source = 'atlas://pydjay/gui/images/resources/volume-slider-knob',
                      pos    = (self.width / 2 - (self.width - 5) / 2, 0),
                      size   = (self.width - 5, 20))
            #Line(rounded_rectangle = [track_start * x_factor, self.y,
            #                          (track_end - track_start) * x_factor, self.height, 10],
            #     width = 1)

            #Ellipse(size = [16,16],
            #        pos = [track_start * x_factor + self.x - 8, self.y+self.height / 2 - 8])
            #Ellipse(size = [16,16],
            #        pos = [track_end * x_factor + self.x - 8, self.y+self.height / 2 - 8])
    """

    def draw_window(self, *args):
        self.canvas.clear()
        #self._cursor.width = self.width - 10
        #self._cursor.height = 15
        #self._cursor.center_x = self.width /2
        #self._cursor.center_y = 25 
        #zero_x      = self.x 
        #x_factor    = float(self.width) / self.track_length if self.track_length is not 0 else 1
        #track_start = self.track_start if self.track_start is not None else 0
        #track_end   = self.track_end if self.track_end is not None else self.track_length
        
        with self.canvas:
            Color(0,0,0,1)
            Rectangle(size = self.size,#(track_start * x_factor,
                             # self.height),
                      pos = self.pos)

            Color(1,1,1,1)
            Line(points = [self.pos[0],self.pos[1],self.width+self.pos[0], self.pos[1]],
                 width = 2)
            Line(points = [self.pos[0],self.pos[1]+self.height,self.width+self.pos[0], self.pos[1]+self.height],
                 width = 2)
            Color(.7, .7, .7, 1)
            for i in range(1, 10):
                Line(points = [self.pos[0], self.pos[1] + i * self.height / 10 ,
                               self.width / 3 + self.pos[0], self.pos[1] + i * self.height / 10],
                     width = 1)
                Line(points = [self.pos[0] + 2*self.width / 3, self.pos[1]+ i * self.height / 10 ,
                               self.width + self.pos[0], self.pos[1] + i * self.height / 10 ],
                     width = 1)
            Color(1, 1, 1, 1)
            Line(points = [self.pos[0], self.pos[1] + 5 * self.height / 10 ,
                           self.width / 3 + self.pos[0], self.pos[1] + 5 * self.height / 10],
                 width = 2)
            Line(points = [self.pos[0] + 2*self.width / 3, self.pos[1]+ 5 * self.height / 10 ,
                           self.width + self.pos[0], self.pos[1] + 5 * self.height / 10 ],
                 width = 2)
                


            #window_end = (self.track_length - track_end) * x_factor
            #Rectangle(size = (window_end, self.height),
            #          pos = [self.pos[0] + self.width - window_end, self.pos[1]])
            Color(.5, .5, .5, 1)
            Line(points = [self.pos[0] + self.width / 2, self.pos[1] ,
                           self.width / 2 + self.pos[0], self.pos[1] + self.height],
                 width = 3)

            #Color(.5, .5, .5, 1)
            #Line(points = [0 + self.width / 2, 0 + 10 ,
            #               self.width / 2 + 0, 0 + self.height - 10],
            #     width = 3)
            Color(1,1,1, 1)
            Rectangle(source = 'atlas://pydjay/gui/images/resources/volume-slider-knob',
                      pos    = (self.pos[0] + self.width / 2 - (self.width - 5) / 2, self.value_pos[1] - 10),
                      size   = (self.width - 5, 20))


    #@staticmethod
    #def in_out_sine(progress):
    #    '''.. image:: images/anim_in_out_sine.png
    #    '''
    #    
    #    return -0.5 * (cos(pi * progress) - 1.0)


            
    def get_vol_value(self):
        d = -0.5 * (cos(pi * self.value_normalized) - 1.0)
        
        #vmin = self.min_value
        #d = self.max_value - vmin
        if d == 0:
            return 0


        if d <= 0.5:
            return 2 * d
        else:
            return 14 * (d-0.5) + 1
        
        #return d #(self.value - vmin) / float(d)

    def set_vol_value(self, value):

        if value <= 1:
            x = value / 2
        else:
            x = (value - 1) / 14.0 + 0.5
        
        #print x
        v_n = acos(1-2*(x)) / pi
        self.value_normalized = v_n
        #print self.value
        
        #vmin = self.min_value
        #vmax = self.max_value
        #step = self.step
        #val = min(value * (vmax - vmin) + vmin, vmax)
        #if step == 0:
        #    self.value = val
        #else:
        #    self.value = min(round((val - vmin) / step) * step + vmin,
        #                     vmax)
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
        padding = 0 #self.padding
        x = self.x
        y = self.y
        nval = self.value_normalized
        #if self.orientation == 'horizontal':
         #   return (x + padding + nval * (self.width - 2 * padding), y)
        #else:
        return (x, y + padding + nval * (self.height - 2 * padding))

    def set_value_pos(self, pos):
        padding = 0 #self.padding
        x = min(self.right - padding, max(pos[0], self.x + padding))
        y = min(self.top - padding, max(pos[1], self.y + padding))
        #if self.orientation == 'horizontal':
        #    if self.width == 0:
        #        self.value_normalized = 0
        #    else:
        #        self.value_normalized = (x - self.x - padding
        #                                 ) / float(self.width - 2 * padding)
        #else:
        if self.height == 0:
            self.value_normalized = 0
        else:
            self.value_normalized = (y - self.y - padding) / float(self.height - 2 * padding)
    value_pos = AliasProperty(get_value_pos, set_value_pos,
                              bind=('x', 'y', 'width', 'height', 'min_value',
                                    'max_value', 'value_normalized'))
    

    def on_touch_down(self, touch):
        #print self.disabled, touch.pos, self.to_window(*touch.pos), self.collide_point(*self.to_window(*touch.pos))
        #print self.pos, self.size
        if self.disabled or not self.collide_point(*touch.pos):
            #print "cannot change"
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
            #print 'grabbing'
            touch.grab(self)
            self.value_pos = touch.pos
            #print self.value_pos
        print self.volume
        return True

    def on_touch_move(self, touch):
        if touch.grab_current == self:
            self.value_pos = touch.pos
            #print self.volume
            return True

    def on_touch_up(self, touch):
        if touch.grab_current == self:
            self.value_pos = touch.pos
            #print self.volume
            return True



            #Line(rounded_rectangle = [track_start * x_factor, self.y,
            #                          (track_end - track_start) * x_factor, self.height, 10],
            #     width = 1)

            #Ellipse(size = [16,16],
            #        pos = [track_start * x_factor + self.x - 8, self.y+self.height / 2 - 8])
            #Ellipse(size = [16,16],
            #        pos = [track_end * x_factor + self.x - 8, self.y+self.height / 2 - 8])

Factory.register('VolumeSlider', VolumeSlider)

            
"""
class TrackCutWindow(Widget):
    track_length = NumericProperty(0)
    track_start  = NumericProperty(0, allownone = True)
    track_end    = NumericProperty(0, allownone = True)

    def __init__(self, *args, **kwargs):
        super(TrackCutWindow, self).__init__(*args, **kwargs)
        self._redraw = Clock.create_trigger(self.draw_window)
        self.bind(track_length = self._redraw,
                  track_start  = self._redraw,
                  track_end    = self._redraw,
                  size         = self._redraw,
                  pos          = self._redraw)

        self.bind(on_touch_down = self._on_touch_down,
                  on_touch_up   = self._on_touch_up,
                  on_touch_move = self._on_touch_move)
        self._move_func = None

    def _move_start_time(self, x, y):
        x_factor = float(self.width) / self.track_length if self.track_length is not 0 else 1
        if x < 10:
            x = 0
        foo =   int(x / x_factor)
        #print x, foo
        if foo + 7000000000 <= self.track_end:
            self.track_start = foo if foo > 0 else 0
        
            
        #if self.track_end < self.track_start:
        #    self.track_end = self.track_start + 7000000000
        pass
    
    def _move_end_time(self, x, y):
        x_factor = float(self.width) / self.track_length if self.track_length is not 0 else 1
        #self.track_end =  int(x / x_factor)
        if x > self.width - 10:
            x = self.width
        foo =   int(x / x_factor)
        if foo - 7000000000 >= self.track_start:
            self.track_end = foo if foo < self.track_length else self.track_length

        ##if self.track_end < self.track_start:
        #    self.track_start = self.track_end - 7000000000
        #pass

    def _on_touch_down(self, window, event):
        x_factor    = float(self.width) / self.track_length if self.track_length is not 0 else 1
        track_start = self.track_start if self.track_start is not None else 0
        track_end   = self.track_end if self.track_end is not None else self.track_length
        
        if self.collide_point(*event.pos):
            x, y = event.pos
            if x < track_start * x_factor + 10 and x > track_start * x_factor - 10:
                if y < self.height / 2 + 10 and y > self.height / 2 - 10:
                    #if self._move_func is not None:
                    self._move_func = self._move_start_time #print "MOVE START"
            if x < track_end * x_factor + 10 and x > track_end * x_factor - 10:
                if y < self.height / 2 + 10 and y > self.height / 2 - 10:
                    self._move_func = self._move_end_time #print "MOVE END"
            
        
        pass

    def _on_touch_up(self, window, event):
        self._move_func = None
        pass

    def _on_touch_move(self, window, event):
        if self.collide_point(*event.pos):
            if self._move_func is not None:
                self._move_func(*event.pos)
    
        
    def draw_window(self, *args):
        self.canvas.clear()
        zero_x      = self.x 
        x_factor    = float(self.width) / self.track_length if self.track_length is not 0 else 1
        track_start = self.track_start if self.track_start is not None else 0
        track_end   = self.track_end if self.track_end is not None else self.track_length
        
        with self.canvas:
            Color(.2,.2,.2,.8)
            Rectangle(size = (track_start * x_factor,
                              self.height),
                      pos = self.pos)
            window_end = (self.track_length - track_end) * x_factor
            Rectangle(size = (window_end, self.height),
                      pos = [self.pos[0] + self.width - window_end, self.pos[1]])
            Color(.7, .7, .7, 1)
            Line(rounded_rectangle = [track_start * x_factor, self.y,
                                      (track_end - track_start) * x_factor, self.height, 10],
                 width = 2)

            Ellipse(size = [16,16],
                    pos = [track_start * x_factor + self.x - 8, self.y+self.height / 2 - 8])
            Ellipse(size = [16,16],
                    pos = [track_end * x_factor + self.x - 8, self.y+self.height / 2 - 8])
"""
