"""Module doc."""
# import os
# import re
# import mimetypes
# import array
# from functools import partial
# from threading import Thread
# from os.path import getsize
# from datetime import datetime
# from kivy.core.window import Window
# from kivy.graphics import Mesh, Color, Rectangle, Line, RoundedRectangle, Ellipse, Triangle
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty
# from kivy.uix.boxlayout import BoxLayout
# from kivy.uix.relativelayout import RelativeLayout
# from kivy.uix.widget import Widget
from kivy.uix.label import Label
# from kivy.properties import ObjectProperty, NumericProperty
from kivy.factory import Factory
# from kivy.uix.popup import Popup
from kivy.uix.modalview import ModalView
# from pydjay.ui.elements import waveform_seekbar#screen, paged_grid, paged_display
from pydjay.ui.elements.utils import seconds_to_human_readable
# from kivy.animation import Animation
import pydjay.bootstrap
import pydjay.ui.dialogs.track_list

from kivy.uix.treeview import TreeViewLabel
# from pydjay.ui.elements import SimpleTrackCardItemModal
import playlist_edit_list


kv_string = """
<PlaylistView>:
    size_hint: .7,.95
    short_list: short_list
    #side_view: side_view
    #sl_track_count:sl_track_count

    canvas:
        Color:
            rgba: 0.7,0.7,0.7,.98
        Rectangle:
            size: self.size
            pos: self.pos

    BoxLayout:
        orientation: 'vertical'

        BoxLayout:
            orientation: 'horizontal'
            size_hint: 1, None
            height: 65
            padding: [10,0,10,0]
            canvas.before:
                Color:
                    rgba: 0.3,0.3,0.3,.98
                Rectangle:
                    size: self.size
                    pos: self.pos

            BoxLayout:
                orientation: 'vertical'
                spacing:2
                Label:
                    size_hint: 1,1
                    #height: 25
                    font_size: 25
                    markup: True
                    halign: 'center'
                    valign: 'middle'
                    text_size: self.size
                    text: "EDIT PLAYLIST"
        ModalHDivider:
        BoxLayout:
            orientation: 'horizontal'
#            ScrollView:
#                size_hint: .3,1
#                do_scroll:True
#                canvas.before:
#                    Color:
#                        rgba: 0.65,0.65,0.65,1
#                    Rectangle:
#                        size: self.size
#                        pos: self.pos
#
#                TreeView:
#                    id: side_view
#                    size_hint_y: None
#                    hide_root: True
#                    #root_options: {'text': 'PLAYLISTS', 'font_size': 15, 'color': [.1,.1,.1,1]}
#                    load_func: root._load_tree_node
#                    minimum_height: self.height
#                    #text: 'PLAYLISTS'
#                    #color: .1,.1,.1,1


            ModalVDivider:
            BoxLayout:
                orientation: 'vertical'
                size_hint: 1,1


                BoxLayout:
                    orientation: 'horizontal'
                    size_hint: 1, None
                    height: 75
                    padding: [10,0,10,0]
                    canvas.before:
                        Color:
                            rgba: 0.65,0.65,0.65,.98
                        Rectangle:
                            size: self.size
                            pos: self.pos

                    BoxLayout:
                        orientation: 'vertical'
                        spacing:2
                        Label:
                            size_hint: 1,None
                            height: 25
                            font_size: 25
                            color: .1,.1,.1,1
                            markup: True
                            halign: 'left'
                            valign: 'middle'
                            text_size: self.size
                            text: "PLAYLIST TITLE"

                        Label:
                            id: sl_track_count
                            size_hint: 1, None
                            height: 20
                            markup:True
                            color: .3,.3,.3,1
                            text: "30 tracks | 2:35"
                            #bold: True
                            halign: 'left'
                            valign: "top"
                            text_size: self.size
                            font_size: 17
                            #size_hint: None, None
                            #size: self.texture_size
                            height:30#

                    BoxLayout:
                        orientation: 'horizontal'
                        size_hint: 1, None
                        pos_hint: {'center_y': .5}
                        height: 30
                        spacing: 0
                        canvas.before:
                            Color:
                                rgba: .6,.6,.6,1
                            Rectangle:
                                pos:self.pos
                                size: self.size

                        TextInput:
                            id:search_filter
                            size_hint: 1,1
                            multiline: False
                            text_size: self.width - 30, self.height
                            hint_text: "Filter list..."
                            foreground_color: .1,.1,.1,1
                            background_color: 0.6,0.6,0.6,1
                            on_text: root.do_filter(*args)

                        ImageButton:
                            size_hint: None, None
                            #pos_hint: {'center_y': .5}
                            size: 30,30
                            image:'atlas://pydjay/gui/images/resources/clear-filter'
                            on_press: search_filter.text = ''

                ModalHDivider:
                PreviewPlayer:
                    id: preview_player
                    size_hint: 1, None
                    height: 85
                    title_color: .1,.1,.1,1
                    artist_color: .3,.3,.3,1
                    time_color: .2,.2,.2,1

                ModalHDivider:
                TrackShortListModal:
                    #orientation: 'vertical'
                    size_hint: 1, 1
                    id: short_list
                    window:root
                    #queue: master_queue
                    preview_player: preview_player
                    #main_player: deck

            ModalVDivider:
            BoxLayout:
                orientation: 'vertical'
                size_hint: .5,1


                BoxLayout:
                    orientation: 'horizontal'
                    size_hint: 1, None
                    height: 75
                    padding: [10,0,10,0]
                    canvas.before:
                        Color:
                            rgba: 0.65,0.65,0.65,.98
                        Rectangle:
                            size: self.size
                            pos: self.pos

                    BoxLayout:
                        orientation: 'vertical'
                        spacing:2
                        Label:
                            size_hint: 1,None
                            height: 25
                            font_size: 25
                            color: .1,.1,.1,1
                            markup: True
                            halign: 'left'
                            valign: 'middle'
                            text_size: self.size
                            text: "PLAYLIST TITLE"

                        Label:
                            id: sl_track_count
                            size_hint: 1, None
                            height: 20
                            markup:True
                            color: .3,.3,.3,1
                            text: "30 tracks | 2:35"
                            #bold: True
                            halign: 'left'
                            valign: "top"
                            text_size: self.size
                            font_size: 17
                            #size_hint: None, None
                            #size: self.texture_size
                            height:30#

                BoxLayout:
                    orientation: 'horizontal'
                    size_hint: 1, None
                    pos_hint: {'center_y': .5}
                    height: 50
                    spacing: 0
                    padding: [10,10,10,10]
                    canvas.before:
                        Color:
                            rgba: .6,.6,.6,1
                        Rectangle:
                            pos:self.pos
                            size: self.size

                    TextInput:
                        id:search_filter
                        size_hint: 1,1
                        multiline: False
                        text_size: self.width - 30, self.height
                        hint_text: "Filter list..."
                        foreground_color: .1,.1,.1,1
                        background_color: 0.6,0.6,0.6,1
                        on_text: root.do_filter(*args)

                    ImageButton:
                        size_hint: None, None
                        #pos_hint: {'center_y': .5}
                        size: 30,30
                        image:'atlas://pydjay/gui/images/resources/clear-filter'
                        on_press: search_filter.text = ''

                ModalHDivider:
                PlaylistEditModal:
                    #orientation: 'vertical'
                    size_hint: 1, 1
                    id: short_list
                    window:root
                    #queue: master_queue
                    preview_player: preview_player
                BoxLayout:
                    orientation: 'horizontal'
                    size_hint: 1, None
                    height: 50
                    padding:[10,5,10,5]
                    spacing: 20
                    Button:
                        text: 'Save'
                    Button:
                        text: 'Dismiss'


"""


class PlaylistView(ModalView):
    short_list = ObjectProperty(None)
    sl_track_count = ObjectProperty(None)

    def __init__(self, *args, **kw):
        super(PlaylistView, self).__init__(*args, **kw)
        self.bind(on_dismiss=lambda *a: pydjay.bootstrap.preview_player.stop())
        self._drag_payload = None

        # self._current_session_item = TreeViewLabel(text='Current Session', color = [.1,.1,.1,1], is_open=True)
        # self._shortlist_item       = TreeViewLabel(text='Short list', color = [.1,.1,.1,1], is_open=True)
        # self._sessions_item        = TreeViewLabel(text='Sessions', color = [.1,.1,.1,1], is_open=False, is_leaf = False)
        # self._genres_item          = TreeViewLabel(text='Genres', color = [.1,.1,.1,1], is_open=False, is_leaf = False)
        # self._styles_item          = TreeViewLabel(text='Styles', color = [.1,.1,.1,1],  is_open=False, is_leaf = False)
        # self._playlists_item       = TreeViewLabel(text='Playlists', color = [.1,.1,.1,1],  is_open=False, is_leaf = False)

        Clock.schedule_once(self._post_init, -1)

    def _post_init(self, *a):
        self.short_list.short_list.adapter.bind(data=self._update_sl_track_count)
        # tree_view.add_node(TreeViewLabel(text=node['node_id'], is_open=True))

        # for x in [#self._current_session_item, # = TreeViewLabel(text='Current Session', is_open=True)
        #    #self._shortlist_item, # = TreeViewLabel(text='Short list', is_open=True)
        #    self._sessions_item,
        #    self._genres_item, # = TreeViewLabel(text='Genres', is_open=True)
        #    self._styles_item, # = TreeViewLabel(text='Styles', is_open=True)
        #    self._playlists_item]:
        #    self.side_view.add_node(x)
        # self._session_item = None]
        #self._session_item = None
        #self._session_item = None
        #self._session_item = None
        # pass

    def open(self):
        super(PlaylistView, self).open()
        self.short_list.set_track_list(pydjay.bootstrap.get_short_list(), sort=False)
        self._update_sl_track_count()
        self.short_list.focus()

    def dismiss(self):
        pydjay.bootstrap.set_short_list(self.short_list.short_list.get_full_track_list())
        super(PlaylistView, self).dismiss()

    def do_filter(self, window, text):
        self.short_list.short_list.do_filter(text)

    # def _load_tree_node(self, tv, node):
#        foo = {self._genres_item: self._load_genres,
#               self._styles_item: self._load_styles,
#               self._playlists_item: self._load_playlists}
#        try:
#            return foo[node]()
#        except Exception, details:
#            print details
#            pass
        # if node == self._genres_item:
        #    return self._get_genres()

    def _load_genres(self):
        for g in pydjay.bootstrap.get_all_genres():
            yield TreeViewLabel(text=g if g is not None else "", color=[.25, .25, .25, 1], is_open=True)

    def _load_styles(self):
        for g in pydjay.bootstrap.get_all_styles():
            yield TreeViewLabel(text=g if g is not None else "", color=[.25, .25, .25, 1], is_open=True)

    def _load_playlists(self):
        for g in pydjay.bootstrap.get_all_playlists():
            yield TreeViewLabel(text=g if g is not None else "", color=[.25, .25, .25, 1], is_open=True)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _update_sl_track_count(self, *args):
        num = len(self.short_list.short_list.adapter.data)
        time = 0

        for t in self.short_list.short_list.adapter.data:
            try:
                time += t['item'].track.info.length
            except:
                pass
        track_count_text = "[color=#ffffff]" + str(num) + " tracks " + "[/color]" + \
            "[color=#999999] | [/color]" + \
            "[color=#cccccc]" + \
            seconds_to_human_readable(time / 1000000000) + "[/color]"
        #self.sl_track_count.text = track_count_text

    def request_focus(self, *a):
        pass

    def remove_unavailable_tracks(self, *a):
        foo = RemoveUnavailableDialog(self)
        foo.open()

    def do_remove_unavailable_tracks(self):
        tracks = [x for x in pydjay.bootstrap.get_short_list() if pydjay.bootstrap.track_is_available(x)]
        pydjay.bootstrap.set_short_list(tracks)
        self.short_list.set_track_list(pydjay.bootstrap.get_short_list(), sort=False)
        self._update_sl_track_count()
        self.short_list.focus()


Builder.load_string(kv_string)
Factory.register('PlaylistView', PlaylistView)
