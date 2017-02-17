import os
from mediacentre.skins.default.theme import get_path
from kivy.graphics import Rectangle, Color, Ellipse, Callback
from kivy.properties import ObjectProperty, NumericProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.lang import Builder#from kivy.lang import Builder
from kivy.factory import Factory
from kivy.uix.button import Button
from jmc.uix import paged_display

DETAILS = """
#:import get_path mediacentre.skins.default.theme.get_path


<GridPage@AnchorLayout>:
    rows: 4
    cols: 3
    size_hint:(1,1)
    anchor_x: 'center'
    anchor_y: 'center'
    layout: layout
#    canvas:
#        Color:
#            rgba: 1,0,0,.6
#        Rectangle:
#            pos:  self.pos
#            size: self.size
            
    #Button:
    #    size_hint: (1,1)
    #    text: "FOO"

    GridLayout:
        id: layout
        rows: root.rows
        cols: root.cols
        col_force_default: True
        row_force_default: True
        padding:0,0
        spacing: 10,10
        size_hint: (.85,.85)
        
"""

class GridPage(AnchorLayout):
    layout = ObjectProperty(None)
    
    def __init__(self, **kw):
        super(GridPage, self).__init__(**kw)
        self.rows = kw.get('rows', None)
        self.cols = kw.get('cols', None)
        #self.size_hint = (1,1)
        #self.layout.bind(size = self._ss)#, pos = self._ss)
        self.bind(size = self._ss)
        
    def _ss(self, *a):
        #print "FOO"
        full_layout_width = self.width * (self.layout.size_hint[0] or 0)
        
        full_layout_height = self.height * (self.layout.size_hint[1] or 0)
        #print full_layout_height - self.layout.spacing[0] * (self.rows - 1)
        
        self.layout.col_default_width = int((full_layout_width - self.layout.spacing[1] * (self.cols - 1)) / self.cols)
        self.layout.row_default_height  = int((full_layout_height - self.layout.spacing[0] * (self.rows - 1)) / self.rows)
        
        #print "Size of this page:", (full_layout_width, full_layout_height), self.layout.col_default_width, self.layout.row_default_height #self.size, self.pos, self.parent.size, self.parent.pos
    
    @property
    def page_size(self):
        return self.rows * self.cols
    
    @property
    def item_size(self):
        return (int((self.layout.width - self.layout.spacing[1] * (self.cols - 1)) / self.cols),
                int((self.layout.height - self.layout.spacing[0] * (self.rows - 1)) / self.rows))
    
    def add_item(self, item):
        item.size_hint = (None, None)
        #print self.item_size, self.size
        item.size = self.item_size
        self.layout.add_widget(item)
        #print self.parent.pos
        
    def __len__(self):
        return len(self.layout.children)


class PagedGrid(paged_display.PagedDisplay):
    #carousel = ObjectProperty(None)
    #page_label = ObjectProperty(None)
    rows = NumericProperty(4)
    cols = NumericProperty(3)
    #spacing = NumericProperty(10)
    def __init__(self, database = None, **kw):
        super(PagedGrid, self).__init__(**kw)
        #self.carousel.bind(index = self._update_label,
        #                   slides = self._update_label)
        self.rows = kw.get('rows', 1)
        self.cols = kw.get('cols', 1)
        
        self._list = []
        self._last_page = None#GridPage(rows = self.rows, cols = self.cols, size_hint = (1,1))
        self._pages = None#, [self._last_page]
        #self.add_page(self._last_page)
        #self.carousel.current_index = 0
        
    @property
    def page_size(self):
        return self.rows * self.cols
    
        
    #def add_item(self, item):
    #    self._list.append(item)
    #    if self._last_page is None:
    #        self._last_page = GridPage(rows = self.rows, cols = self.cols, size_hint = (1,1))
    #        self._pages = [self._last_page]
    #        self.add_page(self._last_page)
    #    #    self.add_page(Button(text = 'FOO'))
    #        self.carousel.index = 0
    #    elif len(self._last_page) == self.page_size:
    #        self._last_page = GridPage(rows = self.rows, cols = self.cols, size_hint = (1,1))
    #        self._pages.append(self._last_page)
    ##        self.add_page(self._last_page)
    #    #    self.add_page(Button(text = 'FOO'))
    #    self._last_page.add_item(item)
        
    #def unload(self):
    #    pass
    

    def set_list(self, ll):
        #print "SET LIST"
        page_size = self.page_size
        pages = []
        first_index = 0
        self._list = ll
        while first_index + page_size < len(ll):
            pages.append(ll[first_index: first_index + page_size])
            first_index += page_size
            
        if first_index < len(ll):
            pages.append(ll[first_index:])
        #print 'IN SET LIST'
        self.carousel.clear_widgets()
        for p in pages:
            #print "PAKING AGES"
            page = GridPage(rows = self.rows, cols = self.cols)
            #print "MAKING PAGES 2", self.rows, self.cols
            index = 0
            for element in p:
                #print "MAKING ELEMENT"
                page.layout.add_widget(element)
                index += 1
            self.add_page(page)
        self.carousel.index = 0
        #print "SET LIST DONE"




Builder.load_string(DETAILS)
Factory.register('PagedGrid', PagedGrid)

index = 0
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
    
    def add_item(*a):
        global index
        index += 1
        print index
        item = Button(text= '%s'%index)
        bar.add_item(item)
        
    def _foo(*a):
        Clock.schedule_interval(add_item, .5)
    #db = database_pickle.Database('/Users/jihemme/mediaserver_data')
    #from kivy.clock import Clock
    #foo = AnchorLayout(size_hint = (1,1), anchor_x = 'center', anchor_y = 'center')
    #init_gui()
    
    bar = PagedGrid(rows = 6, cols = 7, size_hint = (1,1))#size = (450,550))
    #add_item()
    ll = []
    for i in range(500):
        ll.append(Button(text = 'Item %s'%i))
    bar.set_list(ll)
    #Clock.schedule_once(_foo, 5)
    #button = Button(test="FOO",size_hint = (1,1))
    #bar.set_seasons(12)
    #bar.set_episodes(123, 45)
    #foo.add_widget(bar)
    #foo.add_widget(button)
    #button.bind(on_press = lambda *x: 
    #bar.set_show(db.get_tv_show('stargate-sg-1'))#db.get_tv_shows())
    runTouchApp(bar)#size=(400,200)))#, size_hint = (None, None)))
