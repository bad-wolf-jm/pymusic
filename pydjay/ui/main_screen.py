import os
import re
import time
import mimetypes

from functools import partial
from threading import Thread
from os.path import getsize
from datetime import datetime

from kivy.clock import mainthread, Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout

from kivy.properties import ObjectProperty
from kivy.factory import Factory

from kivy.uix.popup import Popup

import main_queue
import player_display
import player_deck
#import .clickable_area


from kivy.animation import Animation

from elements.main_window import MainWindow
from track_editor import TrackEditor
#from playlist_editor import PlaylistEditor
#from shortlist_view import ShortListView
from dialogs.playlist_view import PlaylistView


from dialogs.playlist_selector import PlaylistSelector

#from dialogs.playlist_chooser import PlaylistChooser
#from dialogs.session_chooser import SessionChooser
#from dialogs.genre_chooser import GenreChooser
#from dialogs.style_chooser import StyleChooser

#from current_session_view import CurrentSessionView
from preview_player import PreviewPlayer
from mixer import Mixer

from main_track_list import MainTrackList
from track_short_list import TrackShortList
from kivy.uix.treeview import TreeViewLabel

import pydjay.bootstrap

kv_string = """
<MainScreen>:
    master_queue: master_queue
    master_list: master_list
    #side_view: side_view
    #short_list: short_list
    precue_player: preview_player
    #main_player: main_player
    size_hint: 1,1
    current_date:""
    current_time:""

    Widget:
        canvas:
            Color:
                rgba: 0.03,0.03,0.03,1
            Rectangle:
                size:self.size
                pos:self.pos
        size_hint: 1,1
        pos_hint: {'x': 0, 'y': 0}
        #keep_ratio: False

    BoxLayout:
        orientation: 'vertical'

        #BoxLayout:
        #    orientation: 'vertical'
        #    size_hint: .25,1

        BoxLayout:
            orientation: 'horizontal'
            size_hint: 1, None
            height: 30 #time_label.height+date_label.height
            padding: [10,0,10,0]
            Label:
                id: time_label
                text: root.current_date #"Monday, November 23"
                halign: 'left'
                valign:"middle"
                font_size: 15
                size_hint: 1, 1
                width: self.texture_size[0]
                #size: self.texture_size
                text_size: self.size
            Label:
                id:date_label
                color: .6,.6,.6,1
                text: root.current_time
                halign: 'right'
                valign: "middle"
                font_size: 15
                size_hint: 1, 1
                #width:200
                size: self.texture_size
                text_size: self.size
                #height:15#

        HDivider:

        BoxLayout:
            orientation: 'horizontal'
            size_hint: 1,1

            #ScrollView:
            #    size_hint: .3,1
            #    do_scroll:True
            #    canvas.before:
            #        Color:
            #            rgba: 0.1,0.1,0.1,1
            #        Rectangle:
            #            size: self.size
            #            pos: self.pos
#
#                TreeView:
#                    id: side_view
#                    size_hint_y: None
#                    hide_root: True
#                    item_height: 25
#                    load_func: root._load_tree_node
#                    odd_color: .1,.1,.1,1
#                    minimum_height: self.height
#            VDivider:
            MainTrackList:
                id: master_list
                window: root
                queue: master_queue
                #short_list: short_list
                #main_player: deck
                preview_player: preview_player
                size_hint: (1.0, 1.0)
                #text: "Browser goes here"
            VDivider:
            BoxLayout:
                orientation: 'vertical'
                size_hint: .6, 1
                #height: 125 #time_label.height+date_label.height

                BoxLayout:
                    orientation: 'horizontal'
                    size_hint: 1, None
                    height: 125 #time_label.height+date_label.height
                    padding: [0,0,0,0]
                    MainPlayerDisplay:
                        id: display
                        size_hint: 1, 1
                        height: 150
                        queue: master_queue

                HDivider:

                BoxLayout:
                    orientation: 'horizontal'
                    size_hint: 1,1
                    #VDivider:
                    BoxLayout:
                        orientation: 'vertical'
                        size_hint: 1,1
                        BoxLayout:
                            orientation: 'horizontal'
                            size_hint: 1,1
                            VDivider:
                            MasterQueue:
                                window:root
                                preview_player: master_list.short_list.preview_player
                                id: master_queue
                                #short_list: short_list
                                preview_player: preview_player
                                #deck: deck
                                size_hint: (.65, 1.0)
                                #text: "Queue goes here"
                        HDivider:
                        BoxLayout
                            orientation: 'vertical'
                            size_hint: 1, None
                            height: 125

                            PreviewPlayer:
                                id: preview_player
                                size_hint: 1, 1

                                #height: 225
                            HDivider:
                            Mixer:
                                id: mixer
                                size_hint: 1, None
                                #width: 220
                                height: 40


"""

from pydjay.core.keyboard import key_map

#even_color = [.1,.1,.1,1], odd_color = [.1,.1,.1,1]

class MainScreen(MainWindow):
    def __init__(self, main_player, preview_player, volume_control, *args, **kwargs):
        super(MainScreen, self).__init__(*args, **kwargs)
        self.m_p = main_player
        Clock.schedule_once(self._post_init, -1)
        Clock.schedule_interval(self._update_time, 1)
        self._preview_player_visible = False
        self._anim = None
        self._volume_control = volume_control
        self._preview_player = preview_player

        key_map.bind(on_edit_track = self._show_track_editor)
        key_map.bind(on_edit_playlist = self._show_playlist_editor)
        key_map.bind(on_display_sessions = self._show_session_chooser)
        key_map.bind(on_display_playlists = self._show_playlist_chooser)
        key_map.bind(on_display_genres = self._show_genre_chooser)
        key_map.bind(on_display_styles = self._show_style_chooser)
        key_map.bind(on_reset_playlist = self._reset_playlist)
        self._focusable_elements = []
        self._no_cycle = False

    def _post_init(self, *args):
        popup = TrackEditor(self._preview_player, self._volume_control, self)
        popup.bind(on_dismiss = self.restore_focus)
        popup.queue = self.master_queue
        popup.window = self
        self.preview_popup = popup
        self._focus = 0
        self._focusable_elements = [self.master_list, self.master_queue]
        self.master_list.focus()

    def request_focus(self, w):
        try:
            i = self._focusable_elements.index(w)
        except ValueError:
            i = None
        if i is not None:
            self._focusable_elements[self._focus].unfocus()
            self._focus = i
            self._focusable_elements[self._focus].focus()

    def cycle_focus(self, _, i):
        if not self._no_cycle:
            self._focusable_elements[self._focus].unfocus()
            self._focus = (self._focus + i) % len(self._focusable_elements)
            self._focusable_elements[self._focus].focus()

    def restore_focus(self, *a):
        self._no_cycle = False
        self._focusable_elements[self._focus].focus()

    def suspend_focus(self):
        self._focusable_elements[self._focus].unfocus()

    def _update_time(self, *args):
        #t = time.localtime()
        self.current_date = time.strftime('%a, %b %d %Y')
        self.current_time = time.strftime('%H:%M:%S')

    def _show_track_editor(self, *a):
        t = self._preview_player._track
        if t is not None:
            self.show_preview_player(t, 0,0)

    def _show_playlist_editor(self, *a):
        self._no_cycle = True
        foo = PlaylistView()
        foo.bind(on_dismiss = self.restore_focus)
        foo.open()

    def _show_session_chooser(self, *a):
        self._no_cycle = True
        foo = PlaylistSelector()
        foo.bind(on_dismiss = self.restore_focus,
                 on_playlist_selected = self.__select_playlist)

        sessions = [#{'list': pydjay.bootstrap.get_current_session(),
                     {'list': pydjay.bootstrap.get_current_session(),
                      'dim_unavailable_tracks':     False,
                      'fixed_item_positions':       True,
                      'can_delete_items':           False,
                      'auto_save':                  False,
                      'sort':                       False,
                      'can_add_selection_to_queue': True}
                    ]

        sessions.extend([{'list':x,
                          'dim_unavailable_tracks':True,
                          'fixed_item_positions':True,
                          'can_delete_items':False,
                          'auto_save': False,
                          'sort': False,
                          'can_add_selection_to_queue':True} for x in pydjay.bootstrap.get_all_sessions()])
        #print sessions
        foo.open(title = 'SESSIONS', pl_list = sessions)

    def __select_playlist(self, w, g):
        params = dict(list_                      = g['list'],
                      dim_unavailable_tracks     = g['dim_unavailable_tracks'],
                      fixed_item_positions       = g['fixed_item_positions'],
                      can_delete_items           = g['can_delete_items'],
                      can_add_selection_to_queue = g['can_add_selection_to_queue'],
                      auto_save                  = g['auto_save'],
                      sort                       = g['sort'],
                      context_menu               = None,
                      editable                   = False)
        self.master_list.display_list(**params)

    def _show_playlist_chooser(self, *a):
        self._no_cycle = True
        foo = PlaylistSelector()

        playlists = [{'list':pydjay.bootstrap.get_all_tracks(),
                      'dim_unavailable_tracks':     True,
                      'fixed_item_positions':       True,
                      'can_delete_items':           False,
                      'auto_save':                  False,
                      'sort':                       False,
                      'can_add_selection_to_queue': True},

                     {'list':pydjay.bootstrap.get_short_list_playlist(),
                      'dim_unavailable_tracks':     True,
                      'fixed_item_positions':       False,
                      'can_delete_items':           True,
                      'auto_save':                  True,
                      'sort':                       False,
                      'can_add_selection_to_queue': True}]


        playlists.extend([{'list':x,
                          'dim_unavailable_tracks':     True,
                          'fixed_item_positions':       False,
                          'can_delete_items':           False,
                          'auto_save':                  True,
                          'sort':                       False,
                          'can_add_selection_to_queue': True} for x in pydjay.bootstrap.get_all_playlists()])
                         #pydjay.bootstrap.get_all_playlists())
        foo.bind(on_dismiss = self.restore_focus,
                 on_playlist_selected = self.__select_playlist)
        foo.open(title = 'PLAYLISTS', pl_list = playlists)

    def _show_genre_chooser(self, *a):
        self._no_cycle = True
        foo = PlaylistSelector()
        foo.bind(on_dismiss = self.restore_focus,
                 on_playlist_selected = self.__select_playlist)
        foo.open(title = 'GENRES', pl_list = [{'list':x,
                          'dim_unavailable_tracks':     True,
                          'fixed_item_positions':       True,
                          'can_delete_items':           False,
                          'auto_save':                  False,
                          'sort':                       True,
                          'can_add_selection_to_queue': True} for x in pydjay.bootstrap.get_all_genres()])

    def _show_style_chooser(self, *a):
        self._no_cycle = True
        foo = PlaylistSelector()
        foo.bind(on_dismiss = self.restore_focus,
                 on_playlist_selected = self.__select_playlist)
        foo.open(title = 'STYLES', pl_list = [{'list':x,
                          'dim_unavailable_tracks':     True,
                          'fixed_item_positions':       True,
                          'can_delete_items':           False,
                          'auto_save':                  False,
                          'sort':                       True,
                          'can_add_selection_to_queue': True} for x in pydjay.bootstrap.get_all_styles()])

    def _reset_playlist(self, *a):
        self.master_list.display_list(#title = g.name if g is not None else "Unknown playlist",
                          list_ = pydjay.bootstrap.get_all_tracks(),
                          dim_unavailable_tracks     = True,
                          fixed_item_positions       = True,
                          can_delete_items           = False,
                          can_add_selection_to_queue = True,
                          context_menu               = None,
                          editable                   = False)

    def show_preview_player(self, track, pos, size, rel = 'right'):
        def _foo(*a):
            self.preview_popup.set_track(track)
            self.preview_popup.open()
        Clock.schedule_once(_foo, 0)

    def _completed_animation(self, *args):
        self._anim = None

    def shutdown(self):
        #self.main_player.shutdown()
        self.master_queue.shutdown()

Builder.load_string(kv_string)
