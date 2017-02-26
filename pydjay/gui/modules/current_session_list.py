from kivy.clock import mainthread, Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.factory import Factory
from pydjay.gui.utils import seconds_to_human_readable
from pydjay.gui.track_list import TrackList

kv_string = """
#:import label kivy.uix.label
#:import sla kivy.adapters.simplelistadapter
#:import DefaultTrackItemView pydjay.gui.list_items.default_track_list_item.DefaultTrackItemView
<CurrentSessionList>:
    orientation: 'horizontal'
    size_hint: 1,1
    #master_list: master_list
    short_list: short_list
    sl_track_count:sl_track_count
    button_size: 45
    BoxLayout:
        orientation: 'vertical'
        size_hint: 1, 1
        BoxLayout:
            orientation: 'horizontal'
            size_hint: 1, None
            height:25
            padding: [10,0,10,0]
            Label:
                text: "CURRENT SESSION"
                halign: 'left'
                valign: 'middle'
                font_size: 15
                bold: True
                size_hint: 1, 1
                text_size: self.size
                height:30#

            Label:
                id: sl_track_count
                size_hint: 1, 1
                markup:True
                text: ""
                bold: True
                halign: 'right'
                valign: "middle"
                text_size: self.size
                font_size: 15
                #size_hint: None, None
                #size: self.texture_size
                height:30#


        HDivider:
       
        TrackList: #ScrollView:
            id: short_list
            size_hint: 1,1
            item_class: DefaultTrackItemView
            item_convert: root._convert_sl
            #on_touch_up: root._on_touch_up(*args)
            #on_touch_down: root._on_list_touch_down(*args)
"""


class CurrentSessionList(BoxLayout):
    master_list = ObjectProperty(None)
    tree_view   = ObjectProperty(None)
    short_list  = ObjectProperty(None)
    queue       = ObjectProperty(None)
    window      = ObjectProperty(None)
    main_player = ObjectProperty(None)
    search_filter = ObjectProperty(None)
    total_track_count = StringProperty("")
    title = StringProperty("")
    
    def __init__(self, *args, **kwargs):
        super(CurrentSessionList, self).__init__(*args, **kwargs)
        Clock.schedule_once(self._post_init,-1)

    def _post_init(self, *args):
        self.short_list.adapter.bind(data = self._update_sl_track_count)
        self.short_list.bind(adapter = self._update_sl_track_count)


    def add_track(self, track, index = None):
        self.short_list.add_track(track, index)

    def _convert_sl(self, row, item):
        return {'row': row, 'item': item, 'view':self, 'drag_context': None}

    def _update_sl_track_count(self, *args):
        num = len(self.short_list.adapter.data)
        time = 0

        track_count_text = self.title
        if num > 0 and track_count_text != "":
            track_count_text += " - " 
        #else:
        for t in self.short_list.adapter.data:
            try:
                time += t.track.info.length
            except:
                pass
        track_count_text += "[color=#ffffff]" + str(num) + " tracks " + "[/color]" + \
                            "[color=#444444] | [/color]"+ \
                            "[color=#888888]" + seconds_to_human_readable(time / 1000000000) + "[/color]"
        self.sl_track_count.text = track_count_text
        return True

    def set_track_list(self, list, sort = True):
        self.short_list.set_track_list(list, False)
        self._update_sl_track_count()
        num = len(self.short_list.adapter.data)
        time = 0
        if num == 0:
            self.total_track_count = ""
        else:
            for t in self.short_list.adapter.data:
                try:
                    time += t.track.info.length
                except:
                    pass
            self.total_track_count = "[color=#ffffff]" + str(num) + " tracks " + "[/color]" + \
                                     "[color=#444444] | [/color]"+ \
                                     "[color=#888888]" + seconds_to_human_readable(time / 1000) + "[/color]"

        
Builder.load_string(kv_string)
Factory.register('CurrentSessionList', CurrentSessionList)




