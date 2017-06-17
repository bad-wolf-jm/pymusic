from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.factory import Factory

kv_string = """
<ListTitleHeader>:
    orientation: 'vertical'
    size_hint:   1, None
    spacing:     2
    title_font_size:     20
    subtitle_font_size:  18
    title_font_color:    [.9,.9,.9,1]
    subtitle_font_color: [.7,.7,.7,1]
    title_text:          ''
    subtitle_text:       ''
    halign:              'left'
    valign:              'middle'
    height:  50
    spacing: 5
    padding: [5,5,5,5]
    Label:
        size_hint: 1,None
        height: self.title_font_size
        font_size: root.title_font_size
        color: root.title_font_color
        markup: True
        halign: root.halign
        valign: root.valign
        text_size: self.size
        text: root.title_text

    Label:
        size_hint: 1, None
        height: root.subtitle_font_size
        color: root.subtitle_font_color
        text: root.subtitle_text
        halign: root.halign
        valign: root.valign
        text_size: self.size
        font_size: root.subtitle_font_size
        markup:True
"""


class ListTitleHeader(BoxLayout):
    def __init__(self, *args, **kw):
        super(ListTitleHeader, self).__init__(*args, **kw)


Builder.load_string(kv_string)
Factory.register('ListTitleHeader', ListTitleHeader)
