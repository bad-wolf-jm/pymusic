import os
from kivy.lang import Builder#from kivy.lang import Builder
from kivy.uix.anchorlayout import AnchorLayout
from kivy.factory import Factory
from kivy.properties import ObjectProperty

class AlignedLabel(AnchorLayout):#CompositeListItem):
    _label = ObjectProperty(None)
    def __init__(self, **args):
        super(AlignedLabel, self).__init__(**args)
 

kv_string = """
<AlignedLabel@AnchorLayout>:
    id: _layout
    anchor_x: 'left'
    anchor_y: 'center'
    size_hint: (1, 1)
    height: _label.height
    #padding: 10,10
    font_size: 12
    text: ""
    color: 1,1,1,1
    label_width: _label.width
    Label:
    #    canvas:
    #        Color:
    #            rgba: 0,1,1,.6
    #        Rectangle:
    ##            pos:self.pos
    #            size: self.size

        id: _label
        font_size: _layout.font_size
        color: root.color
        markup:True
        shorten: True
        text: root.text
        size_hint: (None, None)
        text_size: self.parent.width, None#root.font_size
        size: self.texture_size
"""

Builder.load_string(kv_string)
Factory.register('AlignedLabel', AlignedLabel)