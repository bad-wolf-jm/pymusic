import os
from mediacentre.skins.default.theme import get_path
from kivy.graphics import Rectangle, Color, Ellipse, Callback
from kivy.properties import ObjectProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.lang import Builder#from kivy.lang import Builder
from kivy.factory import Factory

from jmc.uix import page_indicator
import math

DETAILS = """
#:import get_path mediacentre.skins.default.theme.get_path

<PagedDisplay@BoxLayout>:
    carousel: carousel
    page_indicator: page_indicator
    orientation: 'vertical'
    #rows: 4
    #cols: 3
    #item_width: None
    #item_height: None
    loop: True
    Carousel:
        id: carousel
        loop: root.loop
        #direction: 'left'
        size_hint: (1,1)
        #canvas:
        #    Color:
        #        rgba: 0,0,1,.6
        #    Rectangle:
        #        pos:self.pos
        #        size: self.size
                
    BoxLayout:
        id: _layout
        orientation: "horizontal"
        size_hint: (1,None)
        height:30
        #pos_hint: {'x':0, 'y':0.0}
        padding: 10,10
        canvas:
            Color:
                rgba: 0,0,0,.6
            Rectangle:
                pos:self.pos
                size: self.size
        #ImageButton:
        #    height: _layout.height - 20
        #    width: _layout.height - 20
        #    font_size: 14
        #    image: get_path("left-arrow")
        #    on_press: root.carousel.load_previous()
        Widget:
            size_hint:(1,1)
        PageIndicator:
            id: page_indicator
            #font_size: 15
            #text: "Page n of m"
        Widget:
            size_hint:(1,1)

        #ImageButton:
        #    height: _layout.height - 20
        #    width: _layout.height - 20
        #    font_size: 14
        #    image: get_path("right-arrow")
        #    on_press: root.carousel.load_next()
"""

class PagedDisplay(BoxLayout):
    carousel = ObjectProperty(None)
    page_indicator = ObjectProperty(None)
    def __init__(self, **kw):
        super(PagedDisplay, self).__init__(**kw)
        self.bind(size = self._size_change)
        #self.carousel.bind(#size=self._size_change,
        #                   index = self._update_indicator,
        #                   slides = self._update_indicator_number)
        #self.page_indicator.bind(current_page = self._move_to_current_page)
        self._pages = None
        self._current_page = None
        self.bind(carousel = self.set_carousel,
                  page_indicator = self.set_page_indicator)
        
        
    def set_carousel(self, *foo):
        self.carousel.bind(#size=self._size_change,
                           index = self._update_indicator,
                           slides = self._update_indicator_number)
        
    def set_page_indicator(self, *foo):
        self.carousel.bind(index = self._move_to_current_page)
        self.page_indicator.bind(on_page_change = self._change_current_page)
        
    def _move_to_current_page(self, *a):
        #if math.isnan()
        self.page_indicator.current_page = self.carousel.index

    def _change_current_page(self, *a):
        #print self.page_indicator.current_page
        self.carousel.index = self.page_indicator.current_page


    def _size_change(self, *a):
        pass#print "DISPLAY SIZE CHANGE", a, self.size, self.carousel.size
        #for s in self.carousel.slides:
        #    #s.size = self.carousel.size
        #    print s, s.size, self.carousel.size
            
    def add_page(self, item):
        item.size_hint = (1,1)#None,None)
        #print 'PAGE_SIZE:', self.size, item.size
        self.carousel.add_widget(item)
        #print "FOO"
        #if len(self.carousel.slides) == 1:
        #    print 'FIRST PAGE'
        #    self.carousel.load_previous()#load_slide(item)
        #    print "Item Size", item.size
            #self.carousel.add_widget(Widget())
    
    def _update_indicator(self, *args):
        if self.carousel is not None:
            self.page_indicator.current_page = self.carousel.index
        #print "PAGE"#, self.carousel.index, self.carousel.current_slide.size, self.carousel.current_slide.pos, self.carousel.size
        
    def _update_indicator_number(self, *a):
        if self.carousel is not None:
            self.page_indicator.num_pages = len(self.carousel.slides)
        #print "PAGE in"#, self.carousel.index, self.carousel.current_slide.size, self.carousel.current_slide.pos, self.carousel.size



Builder.load_string(DETAILS)
Factory.register('PagedDisplay', PagedDisplay)


index  = 0
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
    def add_item(*a):
        global index
        index += 1
        #print index
        item = Button(text= '%s'%index)
        bar.add_page(item)
        
    def _foo(*a):
        Clock.schedule_interval(add_item, 1)
    #db = database_pickle.Database('/Users/jihemme/mediaserver_data')
    #from kivy.clock import Clock
    #foo = AnchorLayout(size_hint = (1,1), anchor_x = 'center', anchor_y = 'center')
    #init_gui()
    
    bar = PagedDisplay(size_hint = (1,1))#size = (450,550))
    add_item()
    add_item()
    
    add_item()
    
    add_item()
    
    add_item()
    #Clock.schedule_once(add_item, 5)
    #button = Button(test="FOO",size_hint = (1,1))
    #bar.set_seasons(12)
    #bar.set_episodes(123, 45)
    #foo.add_widget(bar)
    #foo.add_widget(button)
    #button.bind(on_press = lambda *x: 
    #bar.set_show(db.get_tv_show('stargate-sg-1'))#db.get_tv_shows())
    runTouchApp(bar)#size=(400,200)))#, size_hint = (None, None)))
