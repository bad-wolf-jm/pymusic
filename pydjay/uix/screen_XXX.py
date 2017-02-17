import os

#from mediacentre.database.TVShows.utils import analyse_folder
#from mediacentre.skins.default.theme import get_path
#from mediacentre.skins.default.screen import Screen
#from mediacentre.skins.default import video_logos
#from kivy.uix.stencilview import StencilView
#rom kivy.uix.scrollview import ScrollView
#from kivy.uix.dropdown import DropDown
#from kivy.uix.togglebutton import ToggleButton
from kivy.uix.boxlayout import BoxLayout
from kivy.factory import Factory
#
#from kivy.uix.listview import ListItemButton, ListItemLabel, \
#        CompositeListItem, ListView, SelectableView

#from kivy.adapters.listadapter import ListAdapter

from kivy.graphics import Rectangle, Color, Ellipse, Callback

#from mediacentre.skins.default.tv_show_screen.episode_details import EpisodeDetails
from kivy.properties import ObjectProperty


#from mediacentre.skins.default.widgets import *
#from mediacentre.skins.default import filebrowser

#class Season(SelectableView, BoxLayout):

from jmc.uix import clickable_area, aligned_label, throbber, page_indicator


from kivy.lang import Builder#from kivy.lang import Builder
DETAILS = """
#:import get_path mediacentre.skins.default.theme.get_path

<MCScreen@BoxLayout>:
    #padding: 30
    #episode_details: episode_details
    #episode_list: ep_list
    #carousel: carousel
    #series_title: series_title
    #season_title: season_title
    #backdrop: backdrop
    #page_label: page_label
    title: ""
    subtitle: ""
    orientation: 'vertical'
    pos_hint: {'x':0, 'y':0}
    BoxLayout:
        orientation: "horizontal"
        size_hint: (1,None)
        height:70
        pos_hint: {'x':0, 'y':0.0}
        padding: 10,10
        spacing: 10
        TextButton:
            text: root.title
            font_size: 40
            anchor_y: 'bottom'
            size_hint: (None, 1)
            valign: 'bottom'
            on_press: root.dispatch("on_title_click")
            #width: self.label.label_width
        ImageButton:
            #label: 'Screen title'
            image: get_path('icon-chevron-right-white')
            font_size: 50
            size_hint: (None, None)
            width: 40
            height: 40
        TextButton:
            text: root.subtitle
            #anchor_y: 'bottom'
            color: .5,.5,.5,1
            font_size: 40
            size_hint: (None, 1)
            on_press: root.dispatch("on_subtitle_click")
        
        #BoxLayout:
        #    orientation: 'horizontal'
        #    size_hint: (None, 1)
        #    width: date_label.label_width+ time_label.label_width+30
        #    AlignedLabel:
        #        size_hint: (None, 1)
        #        id:date_label
        #        font_size: 25
        #        width: self.label_width
        #        anchor_x: 'right'
        #        anchor_y: 'bottom'
        #        text: "Mov. 26th, 2014"
        #    Image:
        #        source: get_path('separator_line_vertical')
        #        size_hint: (None, None)
        #        size: 20,40
        #        allow_stretch: True
        #        keep_ratio: False
        #    AlignedLabel:
        #        size_hint: (None, 1)
        #        id: time_label
        #        width: self.label_width
        #        font_size: 25
        #        color: .5,.5,.5,1
        #        anchor_x: 'right'
        #        anchor_y: 'bottom'
        #        text: "23:55"
    #Throbber:
    #    size_hint: (1,1)
    #PageIndicator:
    #    size_hint: (1, None)
    #    height: 40
    #    num_pages: 10
    #    current_page: 3

"""
#def init_gui():
#from kivy.uix.modalview import ModalView




class MCScreen(BoxLayout):
    #episode_details = ObjectProperty(None)
    #episode_list = ObjectProperty(None)
    #backdrop = ObjectProperty(None)
    #season_title = ObjectProperty(None)
    #carousel = ObjectProperty(None)
    #page_label = ObjectProperty(None)
    def __init__(self, database = None, **kw):
        #kw['orientation'] =  'vertical'
        BoxLayout.__init__(self, **kw)
        self.register_event_type('on_title_click')
        self.register_event_type('on_subtitle_click')
        
    def on_title_click(self, *a):
        pass
    
    def on_subtitle_click(self, *a):
        pass
    
        
        
Builder.load_string(DETAILS)
Factory.register('MCWindow', MCScreen)


if __name__ == '__main__':
    from kivy.base import runTouchApp
    from mediacentre.database.TVShows import database_pickle
    from kivy.core.window import Window

## red background color
    Window.clearcolor = (0,0,0, 1)
    #Window.width = 350
    #Window.height = 475
 
    db = database_pickle.Database('/Users/jihemme/mediaserver_data')
    #from kivy.clock import Clock
    #foo = AnchorLayout(size_hint = (1,1), anchor_x = 'center', anchor_y = 'center')
    #init_gui()
    bar = MCScreen()#size = (450,550))
    #button = Button(test="FOO",size_hint = (1,1))
    #bar.set_seasons(12)
    #bar.set_episodes(123, 45)
    #foo.add_widget(bar)
    #foo.add_widget(button)
    #button.bind(on_press = lambda *x: 
    #bar.set_show(db.get_tv_show('stargate-sg-1'))#db.get_tv_shows())
    runTouchApp(bar)#size=(400,200)))#, size_hint = (None, None)))


