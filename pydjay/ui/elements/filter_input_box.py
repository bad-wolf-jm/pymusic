from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.properties import ObjectProperty, NumericProperty
from kivy.factory import Factory

kv_string = """
<FilterInputBox>:
    orientation: 'horizontal'
    size_hint: 1, None
    pos_hint: {'center_y': .5}
    height: 30
    spacing: 0
    background_color: [.1,.1,.1,1]
    foreground_color: [.9,.9,.9,1]
    hint_text: 'Filter list...'
    canvas.before:
        Color:
            rgba: root.background_color
        Rectangle:
            pos:self.pos
            size: self.size

    TextInput:
        id:search_filter
        size_hint: 1,1
        multiline: False
        text_size: self.width - 30, self.height
        hint_text: root.filter_text
        foreground_color: root.foreground_color
        background_color: root.background_color
        on_text: root.do_filter(*args)
        on_text_validate: root.do_filter(*args)

    ImageButton:
        size_hint: None, None
        #pos_hint: {'center_y': .5}
        size: 30,30
        image:'atlas://pydjay/gui/images/resources/clear-filter'
        on_press: search_filter.text = ''
"""


class FilterInputBox(BoxLayout):
    short_list = ObjectProperty(None)
    sl_track_count = ObjectProperty(None)

    def __init__(self, *args, **kw):
        super(FilterInputBox, self).__init__(*args, **kw)

    def do_filter(self, window, text):
        self.short_list.short_list.do_filter(text)


Builder.load_string(kv_string)
Factory.register('FilterInputBox', FilterInputBox)
