import os

from kivy.uix.button import Button
from kivy.properties import ObjectProperty, StringProperty
from pydjay.uix import aligned_label


#def get_path(path):
#    return os.path.join(os.path.dirname(__file__), path + '.png')

kv_string = """
#:import get_path pydjay.uix.get_path.get_path
<ClickableArea@Button>:
    #content: content_area
    background_normal: get_path('transparent_image')
    #on_press: self._do_press
    #AnchorLayout:
    #    id: content_area
    #    pos: self.parent.pos
    #    size: self.parent.size
        
<ImageButton@ClickableArea>:
    id: _b
    image: get_path("transparent_image")
    image_width: 32#self.width - 5
    image_height: 32#self.height - 5
    background_normal: get_path("transparent_image")
    
    Image:
        size: self.parent.image_width, self.parent.image_height
        pos:self.parent.x + self.parent.width/2 - self.parent.image_width / 2, self.parent.y + self.parent.height/2 - self.parent.image_height / 2
        size_hint: (None, None)
        keep_ratio: True
        allow_stretch: True
        source: self.parent.image
        
        
<TextButton@Button>:
    text: ""
    #text_size: 100
    #button:button
    font_size:20
    #width: image_button.width + button.width
    
    #ImageButton:
    #    id: image_button
    #    image: get_path('right-arrow')
    #    size_hint:(None, 1)
    #    width: self.height
    #Button:
    #id:button
    #text: root.text
    font_size: 20
    max_lines: 1
    #shorten: True
    size_hint: (None,1)
    #shorten_from: 'right'
    split_str:""
    background_normal: ""#get_path('transparent_image')
    #text_size: min(size_label.texture_size[0], 300), None
    size: self.texture_size
    
#        canvas:
#            Color:
#                rgba: 0,0,1,.6
#            Rectangle:
#                pos:self.pos
#                size: self.size

    Label:
        id: size_label
        opacity: 0
        text: root.text 
        font_size: root.font_size


        
#<TextButton@ClickableArea>:
#    id: _b
#    image: get_path("transparent_image")
#    background_normal: ""#get_path("transparent_image")
#    label_text: ""
#    font_size: 12
#    anchor_y: 'center'
#    label: label#_width: self.label._label.width
#    canvas:
#        Color:
#            rgba: 1,0,1,.6
#        Rectangle:
#            pos:self.pos
#            size: self.size
#
#    AlignedLabel:
#        id: label
#        size_hint: (1, None)
#        height: self.parent.height  #image_width, self.parent.image_height
#        pos:self.parent.pos     # + self.parent.width/2 - self.parent.image_width / 2, self.parent.y + self.parent.height/2 - self.parent.image_height / 2
#        #size_hint: (None, None)
#        anchor_y: root.anchor_y
#        text: self.parent.label_text           #keep_ratio: True
#        font_size: self.parent.font_size #allow_stretch: True
#        #source: self.parent.image
        
        
<TagButton@ClickableArea>:
    id: _b
    image: ""#get_path("transparent_image")
    background_normal: ""#get_path("transparent_image")
    label_text: ""
    font_size: 12
    anchor_y: 'center'
    tag_area: tag_area
    label: label#_width: self.label._label.width
    Image:
        size: self.parent.image_width, self.parent.image_height
        pos:self.parent.x + self.parent.width/2 - self.parent.image_width / 2, self.parent.y + self.parent.height/2 - self.parent.image_height / 2
        size_hint: (None, None)
        keep_ratio: True
        allow_stretch: True
        source: self.parent.image
        
    BoxLayout:
        id: tag_area
        orientation: 'vertical'
    #AlignedLabel:
    #    id: label
    #    size: self.parent.size  #image_width, self.parent.image_height
    #    pos:self.parent.pos     # + self.parent.width/2 - self.parent.image_width / 2, self.parent.y + self.parent.height/2 - self.parent.image_height / 2
    #    size_hint: (None, None)
    #    anchor_y: root.anchor_y
    #    text: self.parent.label_text           #keep_ratio: True
    ##    font_size: self.parent.font_size #allow_stretch: True
    #    #source: self.parent.image

"""

class ClickableArea(Button):
    def __init__(self, **args):
        super(ClickableArea, self).__init__(**args)
 
class ImageButton(ClickableArea):
    def __init__(self, **args):
        super(ImageButton, self).__init__(**args)
        #print "OMAGE BUTTON CREATED", self

class TextButton(Button):
    label = ObjectProperty(None)
    label_text = StringProperty(None)
    def __init__(self, **args):
        super(TextButton, self).__init__(**args)
        
class TagButton(ClickableArea):
    tag_area = ObjectProperty(None)
    def __init__(self, **args):
        super(TagButton, self).__init__(**args)
        
from kivy.lang import Builder
from kivy.factory import Factory

Builder.load_string(kv_string)
Factory.register('ClickableArea', ClickableArea)
Factory.register('ImageButton', ImageButton)
Factory.register('TextButton', TextButton)
Factory.register('TagButton', TextButton)
