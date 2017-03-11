from kivy.clock import mainthread, Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.factory import Factory


#from pydjay.gui.utils import seconds_to_human_readable
from elements.clickable_area import ImageButton
from behaviors.long_press_button import LongPressButtonBehaviour

from elements import widgets

from elements.simple_detailed_list_item import SimpleDetailedListItem
from elements.utils import seconds_to_human_readable


from elements import large_track_list
from behaviors.track_list_behaviour import TrackListBehaviour
from pydjay.bootstrap import play_queue, session_manager, playback_manager


kv_string = """
#:import label kivy.uix.label
#:import sla kivy.adapters.simplelistadapter
#:import SimpleDetailedListItem pydjay.ui.elements.simple_detailed_list_item.SimpleDetailedListItem
#:import SimpleTrackCardItem pydjay.ui.elements.simple_track_card_item.SimpleTrackCardItem
<MainTrackList>:
    orientation: 'horizontal'
    size_hint: 1,1
    master_list: master_list
    #tree_view:tree_view
    #short_list: short_list
    search_filter:search_filter
    track_count:track_count
    button_size: 45
    #side_view: side_view

    StencilView:
        size_hint: 1,1
        RelativeLayout:
            size: self.parent.size
            pos: self.parent.pos
            BoxLayout:
                orientation: 'vertical'
                size_hint: 1,1
                RelativeLayout:
                    size_hint: 1, None
                    height: 55

                    BoxLayout:
                        orientation: 'horizontal'
                        size_hint: 1, 1
                        padding:[10,0,10,0]
                        spacing: 10
                        canvas.before:
                            Color: 
                                rgba: (.3,.3,.3,1) if root.has_focus else (0.1,0.1,0.1,1)
                            Rectangle:
                                pos: self.pos
                                size: self.size

                        #ImageButton:
                        #    size_hint: None, None
                        #    size: root.button_size,root.button_size
                        #    pos_hint: {'center_y':.5}
                        #    #on_press: root.show_side_view()
                        #    image: 'atlas://pydjay/gui/images/resources/show-list'
                        BoxLayout:
                            orientation: 'vertical'
                            size_hint: .75, 1
                            #height: 
                            Label:
                                size_hint: 1,1
                                text: root.playlist_title  #"PLAYLIST TITLE"
                                bold: True
                                halign: 'left'
                                valign: "bottom"
                                text_size: self.size
                                font_size: 18
                                #size_hint: None, None
                                #size: self.texture_size
                                height:45#
                            Label:
                                size_hint: 1,1
                                text: root.total_track_count
                                markup: True
                                halign: 'left'
                                valign: "top"
                                text_size: self.size
                                font_size: 15
                                #size_hint: None, None
                                #size: self.texture_size
                                height:45#

                        BoxLayout:
                            orientation: 'horizontal'
                            size_hint: 1, None
                            pos_hint: {'center_y': .5}
                            height: 30
                            spacing: 0
                            canvas.before:
                                Color:
                                    rgba: .2,.2,.2,1
                                Rectangle:
                                    pos:self.pos
                                    size: self.size

                            TextInput:
                                id:search_filter
                                size_hint: 1,1
                                multiline: False
                                text_size: self.width - 30, self.height
                                hint_text: "Filter list..."
                                foreground_color: 1,1,1,.8
                                background_color: 0,0,0,0
                                on_text: root.do_filter(*args)

                            ImageButton:
                                size_hint: None, None 
                                #pos_hint: {'center_y': .5}
                                size: 30,30
                                image:'atlas://pydjay/gui/images/resources/clear-filter'
                                on_press: search_filter.text = ''
                                #text:'Clear'

                HDivider:

                LargeTrackList:
                    id: master_list
                    size_hint: 1,1
                    #player: root.main_player
                    item_class: SimpleDetailedListItem
                    item_convert: root._convert
                HDivider:
                Label:
                    id: track_count
                    size_hint: 1, None
                    markup:True
                    height: 25
                    text: ""
                    bold: True
                    halign: 'center'
                    valign: "middle"
                    text_size: self.size
                    font_size: 15
                    #size_hint: None, None
                    #size: self.texture_size
                    #height:45#
                    on_touch_down: root._on_list_touch_down(*args)

"""

class DragContext:
    def __init__(self, drag, drop):
        self.drag = drag
        self.drop = drop

class MainTrackList(BoxLayout, TrackListBehaviour):
    master_list       = ObjectProperty(None)
    short_list        = ObjectProperty(None)
    #main_player       = ObjectProperty(None)
    preview_player    = ObjectProperty(None)
    search_filter     = ObjectProperty(None)
    total_track_count = StringProperty("")
    playlist_title    = StringProperty("")
    title             = StringProperty("")
    
    def __init__(self, *args, **kwargs):
        super(MainTrackList, self).__init__(*args, **kwargs)
        self._focus = False
        self._keyboard = None
        Clock.schedule_once(self._post_init,-1)
        self.drag_context = DragContext(self._start_drag, None)
        self._current_selection = None
        self.set_keyboard_handlers({'ctrl+f':  self._focus_filter,
                                    'shift+q': self._add_selection_to_queue,
                                    'shift+s': self._add_selection_to_short_list})
        
    def _post_init(self, *args):
        self.search_filter.bind(focus = self._toggle_keyboard_shortcuts)
        self.master_list.adapter.bind(data = self._update_track_count)
        self.master_list.bind(adapter = self._update_track_count)
        playback_manager.bind(track                = self._update_availability)
        play_queue.bind(on_queue_content_change = self._update_availability)
        session_manager.bind(on_current_session_changed = self._update_availability)
        self.adapter = self.master_list.adapter
        self.list_view = self.master_list.list_view
        
    def _focus_filter(self):
        self.search_filter.focus = True

    def _add_selection_to_short_list(self):
        item = self.current_selection
        if item is not None:
            self.short_list.add_shortlist_track(item['item'].track)

    def _add_selection_to_queue(self):
        item = self.current_selection
        if item is not None:
            play_queue.add_track(item['item'].track)

    
        
    def _toggle_keyboard_shortcuts(self, *a):
        if not self.search_filter.focus:
            self.window.request_focus(self)
        else:
            self.window.suspend_focus()
            pass

    def _update_availability(self, *args):
        self.master_list.update_availability(self._track_is_available)

    def show_preview_player(self, track, pos, size):
        self.preview_player.play(track)

    def set_playlist_title(self, tit):
        self.playlist_title = tit
    
    def _start_drag(self, coords, item):
        self.window.start_drag(coords, item.track)

    def do_filter(self, window, text):
        self.master_list.do_filter(text)

    def _convert(self, row, item):
        return {'row': row,
                'item': item,
                'view':self,
                'drag_context':self.drag_context,
                'is_selected': False}

    def _update_track_count(self, *args):
        num = len(self.master_list.adapter.data)
        time = 0

        track_count_text = self.title
        if num > 0 and track_count_text != "":
            track_count_text += " - " 
        for t in self.master_list.adapter.data:
            try:
                time += t['item'].track.info.length
            except:
                pass
        track_count_text += "[color=#ffffff]" + str(num) + " tracks " + "[/color]" + \
                            "[color=#444444] | [/color]"+ \
                            "[color=#888888]" + seconds_to_human_readable(time / 1000000000) + "[/color]"
        self.track_count.text = track_count_text
        return True
        
    def _on_list_touch_down(self, window, event):
        if self.master_list.collide_point(*event.pos):
            if not event.is_mouse_scrolling:
                for data in self.master_list.adapter.data:
                    data['is_selected'] = False

    def set_track_list(self, list, sort = True):
        self.master_list.set_track_list(list, sort, self._track_is_available)
        self._update_track_count()
        num = len(self.master_list.adapter.data)
        time = 0
        if num == 0:
            self.total_track_count = ""
        else:
            for t in self.master_list.adapter.data:
                try:
                    time += t['item'].track.info.length
                except:
                    pass
            self.total_track_count = "[color=#ffffff]" + str(num) + " tracks " + "[/color]" + \
                                     "[color=#444444] | [/color]"+ \
                                     "[color=#888888]" + seconds_to_human_readable(time / 1000000000) + "[/color]"

        
Builder.load_string(kv_string)
Factory.register('MainTrackList', MainTrackList)
