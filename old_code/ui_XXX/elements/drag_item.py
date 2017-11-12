import os

from kivy.clock import mainthread, Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.relativelayout import RelativeLayout

from kivy.properties import ObjectProperty
from kivy.factory import Factory
#from behaviors.long_press_button import LongPressButtonBehaviour


kv_drag_widget = """
<DragItem>:
    orientation: 'horizontal'
    size_hint: None, None
    size: 350,75
    title: ""
    artist: ""
    image: 'atlas://pydjay/gui/images/resources/default_album_cover'
    album_art:album_art

    on_pos:  root.update_bg()#self.pos, self.size)
    on_size: root.update_bg()#self.pos, self.size)
    #on_touch_down: self._on_touch_down(*args)

    canvas:
        Color:
            rgba:.5,.5,.5,1
        Rectangle:
            pos:  0,0
            size: self.size

    BoxLayout:
        orientation: 'horizontal'
        size_hint: 1, None
        size_hint: 1,1 
        pos_hint: {'x': 0, 'y': 0}
        padding:[5,5,5,7]
        spacing: 8
        Image:
            id: album_art
            size_hint: (None, 1)
            width: self.height
            keep_ratio: True
            allow_stretch: True
            source: root.image #'pydjay/gui/default_album_cover.png'

        BoxLayout:
            orientation: 'vertical'
            size_hint: 1,1
            #height: will_play.height
            padding:[5,5,5,5]
      
            Label:
                font_size: 15
                color: .1,.1,.1,1
                text: root.title #"Title"
                text_size: self.size
                halign: 'left'
                valign: 'middle'
                size_hint: 1, 1
                shorten: True
                ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}

                #height:will_play.height

            Label:
                text: root.artist  #"Artist"
                color: .3,.3,.3,1
                text_size: self.size
                halign: 'left'
                valigh: 'middle'
                font_size: 15
                size_hint: 1, 1
                shorten: True
                ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}
"""


class DragItem(RelativeLayout):
    album_art = ObjectProperty(None)
    album_art_file = ObjectProperty(None)
    title = StringProperty("")
    artist = StringProperty("")
    album = StringProperty("")
    bpm = StringProperty("")
    length = StringProperty("")
    bg = ObjectProperty(None)
    track = ObjectProperty(None)
    play_time = StringProperty("")

    def __init__(self, item=None, *args, **kwargs):
        super(DragItem, self).__init__(*args, **kwargs)
        self._album_art = None
        self._item = item
        self.track = item
        if item is not None:
            self.title = unicode(item.metadata.title)
            self.artist = unicode(item.metadata.artist)
            self.album = unicode(item.metadata.album)
            self.bpm = str(item.metadata.bpm)

            if item.metadata.album_cover is not None:
                try:
                    self.album_art.source = item.metadata.album_cover['small']
                except:
                    self.album_art.source = 'atlas://pydjay/gui/images/resources/default_album_cover'
            else:
                self.album_art.source = 'atlas://pydjay/gui/images/resources/default_album_cover'
        else:
            self.title = ""
            self.artist = ""
            self.album = ""
            self.bpm = ""
            self.length = ""

    def update_bg(self, *args):
        pass

    def update_album_art(self, w, h):
        if self._album_art is not None:
            self.album_art.texture = self._album_art.texture


Builder.load_string(kv_drag_widget)
