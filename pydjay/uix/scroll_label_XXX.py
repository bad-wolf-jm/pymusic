import os
import os.path

from kivy.lang import Builder#from kivy.lang import Builder
from kivy.factory import Factory

DETAILS = """
#:import get_path mediacentre.skins.default.theme.get_path
<ScrollLabel@ScrollView>:
    text: ""
    font_size: 12
    halign: 'justify'
    Label:  
        id: overview
        markup: True
        font_size: root.font_size
        halign:root.halign
        valign:"top"
        size_hint:(None, None)
        text: root.text
        text_size: (root.width - 20, None)
        size: self.texture_size[0], self.texture_size[1]#(20,0)
"""

class ScrollLabel(ScrollView):
    def __init__(self, **kw):
        super(ScrollLabel, self).__init__(**kw)

Builder.load_string(DETAILS)
Factory.register("ScrollLabel", ScrollLabel)
