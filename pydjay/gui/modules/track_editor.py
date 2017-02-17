import os
import re
import mimetypes
import array

from functools import partial
from threading import Thread
from os.path import getsize
from datetime import datetime

from kivy.core.window import Window
from kivy.graphics import Mesh, Color, Rectangle, Line, RoundedRectangle, Ellipse, Triangle
from kivy.clock import mainthread, Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label

from kivy.properties import ObjectProperty, NumericProperty
from kivy.factory import Factory

from kivy.uix.popup import Popup
from kivy.uix.modalview import ModalView

#from pydjay.audio.wavegen import WaveformGenerator
#from pydjay.audio.gst import AudioDecoder

#from pydjay.audio.player.player import AudioPlayer

from pydjay.uix import waveform_seekbar#screen, paged_grid, paged_display
#from pydjay.gui.turntable import turntable
from pydjay.gui.utils import seconds_to_human_readable
#from pydjay.uix import memory_image, clickable_area
from kivy.animation import Animation
#from pydjay.uix import long_press_button
#from pydjay.uix import screen

#from pydjay.gui.files_screen import file_browser, location_browser
#from mediacentre.skins.default.theme import get_path
import pydjay.bootstrap

#import pydjay.gui.tickline

#from pydjay.gui.tickline import Tick



kv_string = """
<PPVolumeKnob@BoxLayout>:
    orientation: 'vertical'
    max: 2.0
    knob: volume_slide
    text: ""
    channel: ""
    controller: None
    volume_controls: None
    size_hint: 1,1
    padding:[5,2,7,10]
    spacing: 10
    canvas:
        Color:
            rgba: 0.1,0.1,0.1,1
        Rectangle:
            size:self.size
            pos: self.pos

    Slider:
        orientation: 'vertical'
        id: volume_slide
        size_hint: 1,1
        min: 0
        max: root.max
        value: 1.0
        on_value: root.volume_controls.set_volume(root.channel, self.value) if root.volume_controls is not None else False
    Label:
        size_hint: 1, None
        height: 25
        text: "%s"%int(volume_slide.value * 100) + "%"
        font_size: 12
    Label:
        size_hint: 1, None
        height: 25
        text: root.text
        text_size: self.size
        font_size: 12
        halign: 'center'
        valign: 'middle'


#    #main_player_slider: main_player_slider
#    orientation: 'horizontal'
#    size_hint: 1,1
#    #title: "Volume setup:"
#    #auto_dismiss: True
#    #size_hint: None, None
#    #size: 700,500
#    canvas:
#        Color:
#            rgba: 0.1, 0.1, 0.1,1
#        Rectangle:
#            size:self.size
#            pos: self.pos#
#
#    BoxLayout:
<PPVolumeControls>:
    main_player_monitor_slider: monitor_slider
    preview_player_slider: preview_slider
    main_player_monitor_mute_slider:main_player_monitor_mute_slider

    orientation: 'horizontal'
    padding: [10,10,10,10]
    spacing: 20
    size_hint: 1,1

    #PPVolumeKnob:
    #    id: main_player_slider
    #    text: "Main player"
    #    max: 4.0
    #    channel: 'main_player'
    #    volume_controls: root.volume_controls

    PPVolumeKnob:
        id: monitor_slider
        text: "Monitor"
        max: 4.0
        channel: 'main_player_monitor'
        volume_controls: root.volume_controls
        size_hint: 1,1

    PPVolumeKnob:
        id: preview_slider
        text: "Preview player"
        max: 4.0
        channel: 'preview_player'
        volume_controls: root.volume_controls
        size_hint: 1,1

    PPVolumeKnob:
        id: main_player_monitor_mute_slider
        text: "Monitor mute"
        max: 0.5
        channel: 'main_player_monitor_mute'
        volume_controls: root.volume_controls
        size_hint: 1,1


"""



class PPVolumeControls(BoxLayout):
    player_choice   = ObjectProperty(None)
    volume_controls = ObjectProperty(None)
    def __init__(self, *args, **kwargs):#deck, volume_controls):
        super(PPVolumeControls, self).__init__(*args, **kwargs)
        #self.deck = deck
        #self.volume_controls = volume_controls
        Clock.schedule_once(self._post_init, -1)
        #self._broadcast = False
        #self._discovery_thread = None
        #self.bind(on_dismiss = self._stop_loop)
        #self.start_broadcast()


    def _post_init(self, *a):
        #self.main_player_slider.knob.value              = self.volume_controls.get_volume('main_player')
        self.preview_player_slider.knob.value           = self.volume_controls.get_volume('preview_player')
        self.main_player_monitor_slider.knob.value      = self.volume_controls.get_volume('main_player_monitor')
        self.main_player_monitor_mute_slider.knob.value = self.volume_controls.get_volume('main_player_monitor_mute')



        
    #def _do_broadcast_loop(self):
    #    #while True:
    #    Logger.info('remote: Waiting for remote player')
    #    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #create UDP socket
    #    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #    s.bind(('', 8989))
    #    s.settimeout(.1)
    #    self._broadcast = True
    #    addresses = {}
    #    while self._broadcast:
    #        try:
    #            data, addr = s.recvfrom(1024)#sendto(data, ('<broadcast>', 8989))
    #            if data.startswith(MAGIC):
    #                data = data[len(MAGIC):]
    #            if addr[0] not in addresses:
    #                Logger.info('remote: Found new remote player')
    #                self._add_choice(data, addr[0])
    #                addresses[addr[0]] = data
    #        except socket.timeout:
    #            pass
#
#        #print 'stopped'
        
#    @mainthread
#    def _add_choice(self, data, address):
#        but = Button(text = data)
#        but.bind(on_press = partial(self._connect, address, data))
#        self.player_choice.add_widget(but)


#    def _stop_loop(self, *args):
#        self._broadcast = False
        
        #def _stop(self, *args):
        #self.dismiss()


#    def _connect(self, address, name, *args):
#        self.deck._do_connect_remote(address, name)
#        self.dismiss()

                 
#    def start_broadcast(self):
#        self._discovery_thread = threading.Thread(target = self._do_broadcast_loop)
#        self._discovery_thread.start()





Builder.load_string(kv_string)
Factory.register('PPVolumeControls', PPVolumeControls)
#Factory.register('DisconnectFromRemote', DisconnectFromRemote)






kv_string = """
#<HDivider@Widget>
#    size_hint: 1, None
#    height: 1
#    canvas.after:
#        Color:
#            rgba: 1, 1, 1, .8
#        Line:
#            points: [self.pos[0],self.pos[1], self.pos[0] + self.width, self.pos[1]]
#
#<VDivider@Widget>
#    size_hint: None, 1
#    width: 1
#    canvas.after:
#        Color:
#            rgba: 1, 1, 1, .8
#        Line:
#            points: [self.pos[0], self.pos[1], self.pos[0], self.pos[1]+self.height]

<PlayPauseButton@ImageButton>:
    play: 'atlas://pydjay/gui/images/resources/play_2' #get_path('play')
    pause: 'atlas://pydjay/gui/images/resources/pause_2'#get_path('pause')
    media_state: "pause"
    image: self.play if self.media_state == 'pause' else self.pause

<TrackEditor>:
    #seekbar: seekbar
    waveform: waveform
    cut_window: cut_window
    #tick_line: tick_line
    cue_point_window: cue_point_window
    start_time_label: start_time_label
    end_time_label: end_time_label
    #turntable:turntable
    album_cover: album_art
    artist_label: artist_label
    title_label:  title_label
    album_label:  album_label
    #length_label:  length_label
    #position_label:  position_label
    title: "PREVIEW"
    #time_remaining_label: time_remaining
    #orientation: 'horizontal'
    #size_hint: 1, 1
    #height:75
    BoxLayout:
        orientation: 'vertical'

        padding: [15,0,15,7]
        #spacing: 10

        #canvas.before:
        #    Color:
        #        rgba: .6, .6, .6, 1
        #    Rectangle:
        #        pos:  self.pos
        #        size: self.size

        Label:
            size_hint: 1, None
            height: 80
            font_size: 30
            text: 'Track edit'
            text_size: self.size
            valign: 'middle'
            halign: 'center'

        HDivider:

        Widget:
            size_hint: None, None
            height: 20

        BoxLayout:
            orientation: 'horizontal'
            size_hint: 1, None
            height: 200
            spacing: 20
            RelativeLayout:
                size_hint: None, 1
                width: self.height

                Image:
                    id: album_art
                    size_hint: 1, 1
                    #width: self.height
                    source: 'atlas://pydjay/gui/images/resources/default_album_cover'
                    allow_stretch: True
                    keep_ratio: True
                #PlayPauseButton:
                #    size_hint: .5,.5
                #    pos_hint: {'center_x':.5, "center_y":.5}
                #    #media_state:root._player.is_playing
                #    #$width:    self.parent.width / 2
                #    #$height:   self.parent.height / 2
                #    #center_x: self.parent.center_x
                #    #center_y: self.parent.center_y
                #    on_press: root.play_pause()

            #BoxLayout:
            #    orientation: 'vertical'
            #    size_hint: 1,1
            BoxLayout:
                orientation: 'horizontal'
                size_hint: 1,1
                size_hint_min_y: 100
                BoxLayout: 
                    orientation: 'vertical'
                    size_hint: 1,None
                    spacing: 10
                    height: 70
                    pos_hint: {'top': 1}
                    Label:
                        id: title_label
                        size_hint: 1,None
                        #shorten: True
                        text: "3 Little Monkeys"
                        text_size: self.size
                        font_size: 18
                        height: 18
                        bold: True
                        halign: 'left'
                        valign: 'middle'
                        shorten: True
                        ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}

                    Label:
                        id: artist_label
                        size_hint: 1,None
                        height: 15
                        text: ""
                        color: .7,.7,.7,1
                        text_size: self.size
                        font_size: 15
                        halign: 'left'
                        valign: 'middle'
                        shorten: True
                        ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}

                    Label:
                        id: album_label
                        size_hint: 1,None
                        height: 15
                        text_size: self.size
                        text: ""
                        color: .7,.7,.7,1
                        halign: 'left'
                        valign: 'middle'
                        shorten: True
                        ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}
                        text: ""
                        font_size: 15
                ImageButton:
                    size_hint: None, None
                    size: 75,75
                    pos_hint: {'top': 1}
                    #text: 'SL'
                    image:'atlas://pydjay/gui/images/resources/add_to_shortlist'
                    on_press: root.short_list.add_shortlist_track(root._track) if root._track is not None else None
                ImageButton:
                    size_hint: None, None
                    size: 75,75
                    pos_hint: {'top': 1}
                    #text: 'queue'
                    image:'atlas://pydjay/gui/images/resources/add_to_queue'
                    on_press: root.queue.add_track(root._track) if root._track is not None else None

#                Widget:
#                    size_hint: 1,.5

            ##PPVolumeControls:
            #    size_hint: .5, 1
            #    volume_controls: root.volume_controls
                #canvas.after:
                #    Color:
                #        rgba: .6, .2, .6, 1
                #    Rectangle:
                #        pos:  0,0#self.pos
                #        size: 0,0#self.size#




                #BoxLayout:
                #    orientation: 'horizontal'
                #    size_hint: 1, None
                #    height: 20
                #    #spacing: 3
                #    Widget:
                #        size_hint: 1,None

                #    Label:
                #        #id: position_label
                #        size_hint: None, 1
                #        width: 70
                #        text_size: self.size
                #        text: "Volume:"
                #        color: .9,.9,.9,1
                #        halign: 'right'
                #        valign: 'middle'
                #        shorten: True
                #        ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}
                #        #text: ""
                #        font_size: 13

                #    Slider:
                #        id: volume_control
                #        pos_hint: {'center_y': 0.5}
                #        size_hint: 1,None
                #        min: 0
                #        max: 4
                #        step: 0.1
                #        value: 1.0
                #        height: 10
                #        on_value: root._set_preview_volume(self.value)
                #        #on_touch_down: root._do_seek(*args)

                #    Label:
                #        #id: length_label
                #        size_hint: None, 1
                #        width: 40
                #        text_size: self.size
                #        text: "%s"%(int(volume_control.value * 100)) + "%"
                #        color: .9,.9,.9,1
                #        halign: 'right'
                #        valign: 'middle'
                #        shorten: True
                #        ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}
                #        #text: ""
                #        font_size: 13


        Widget:
            size_hint: None, 1
        #HDivider:
        BoxLayout:
            orientation: 'vertical'
            spacing: 10
            size_hint: 1, None
            height: 300
            padding:[10,10,10,10]
            #Tickline:
            #    id: tick_line
            #    size_hint: 1, None
            #    height: 100
            #    orientation: 'horizontal'

            RelativeLayout:
                size_hint: 1,1
                WaveformSeekbar:
                    canvas.before:
                        Color:
                            rgba: 0,0,0,0
                        Rectangle:
                            pos:  0,0#self.pos[0] - root.pos[0], self.pos[1] - root.pos[1]
                            size: self.size

                    size_hint: 1, None
                    height: 200
                    pos:0,0
                    id: waveform

                TrackCutWindow:
                    id: cut_window
                    size_hint: 1,None
                    height: 200
                    pos:0,0
                    #track_length: root.track.info.length if root.track is not None else 0 
                    #window_start: 30000000000
                    #window_end: 60000000000

                TrackCuePointWindow:
                    id: cue_point_window
                    size_hint: 1,1

            RelativeLayout:
                size_hint: 1, None
                height: 15
                Label:
                    id: start_time_label
                    text: '0:00'
                    font_size: 13
                Label:
                    id: end_time_label
                    text: '0:00'
                    font_size: 13

            #BoxLayout:
            #    orientation: 'vertical'
            #    size_hint: 1, None
            #    height: 20
            #    padding:[0,0,0,0]
            #    ProgressBar:
            #        id: seekbar
            #        pos_hint: {'center_y': 0.5}
            #        size_hint: 1,None
            #        height: 10
            #        on_touch_down: root._do_seek(*args)

            #    BoxLayout:
            #        orientation: 'horizontal'
            #        size_hint: 1, None
            #        height: 20
            #        #spacing: 3
            #        Label:
            #            id: position_label
            #            size_hint: None, 1
            #            width: 40
            #            text_size: self.size
            #            text: "0:00"
            #            color: .9,.9,.9,1
            #            halign: 'left'
            #            valign: 'middle'
            #            shorten: True
            #            ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}
            #            #text: ""
            #            font_size: 13

            #        Widget:
            #            size_hint: 1,None

            #        Label:
            #            id: length_label
            #            size_hint: None, 1
            #            width: 40
            #            text_size: self.size
            #            text: "0:00"
            #            color: .9,.9,.9,1
            #            halign: 'right'
            #            valign: 'middle'
            #            shorten: True
           #             ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}
            #            font_size: 13
        Widget:
            size_hint: None, 1

"""

class TrackCutWindow(Widget):
    track_length = NumericProperty(0)
    track_start  = NumericProperty(0, allownone = True)
    track_end    = NumericProperty(0, allownone = True)

    def __init__(self, *args, **kwargs):
        super(TrackCutWindow, self).__init__(*args, **kwargs)
        self._redraw = Clock.create_trigger(self.draw_window)
        self.bind(track_length = self._redraw,
                  track_start  = self._redraw,
                  track_end    = self._redraw,
                  size         = self._redraw,
                  pos          = self._redraw)

        self.bind(on_touch_down = self._on_touch_down,
                  on_touch_up   = self._on_touch_up,
                  on_touch_move = self._on_touch_move)
        self._move_func = None

    def _move_start_time(self, x, y):
        x_factor = float(self.width) / self.track_length if self.track_length is not 0 else 1
        if x < 10:
            x = 0
        foo =   int(x / x_factor)
        if foo + 7000000000 <= self.track_end:
            self.track_start = foo if foo > 0 else 0
        pass
    
    def _move_end_time(self, x, y):
        x_factor = float(self.width) / self.track_length if self.track_length is not 0 else 1
        if x > self.width - 10:
            x = self.width
        foo =   int(x / x_factor)
        if foo - 7000000000 >= self.track_start:
            self.track_end = foo if foo < self.track_length else self.track_length

    def _on_touch_down(self, window, event):
        x_factor    = float(self.width) / self.track_length if self.track_length is not 0 else 1
        track_start = self.track_start if self.track_start is not None else 0
        track_end   = self.track_end if self.track_end is not None else self.track_length
        
        if self.collide_point(*event.pos):
            x, y = event.pos
            if x < track_start * x_factor + 10 and x > track_start * x_factor - 10:
                if y < self.height / 2 + 10 and y > self.height / 2 - 10:
                    #if self._move_func is not None:
                    self._move_func = self._move_start_time #print "MOVE START"
            if x < track_end * x_factor + 10 and x > track_end * x_factor - 10:
                if y < self.height / 2 + 10 and y > self.height / 2 - 10:
                    self._move_func = self._move_end_time #print "MOVE END"
            
        
        pass

    def _on_touch_up(self, window, event):
        self._move_func = None
        pass

    def _on_touch_move(self, window, event):
        if self.collide_point(*event.pos):
            if self._move_func is not None:
                self._move_func(*event.pos)
    
        
    def draw_window(self, *args):
        self.canvas.clear()
        zero_x      = self.x 
        x_factor    = float(self.width) / self.track_length if self.track_length is not 0 else 1
        track_start = self.track_start if self.track_start is not None else 0
        track_end   = self.track_end if self.track_end is not None else self.track_length
        
        with self.canvas:
            Color(.2,.2,.2,.8)
            Rectangle(size = (track_start * x_factor,
                              self.height),
                      pos = self.pos)
            window_end = (self.track_length - track_end) * x_factor
            Rectangle(size = (window_end, self.height),
                      pos = [self.pos[0] + self.width - window_end, self.pos[1]])
            Color(.7, .7, .7, 1)
            Line(rounded_rectangle = [track_start * x_factor, self.y,
                                      (track_end - track_start) * x_factor, self.height, 10],
                 width = 2)

            Ellipse(size = [16,16],
                    pos = [track_start * x_factor + self.x - 8, self.y+self.height / 2 - 8])
            Ellipse(size = [16,16],
                    pos = [track_end * x_factor + self.x - 8, self.y+self.height / 2 - 8])
            
Factory.register('TrackCutWindow', TrackCutWindow)


#class TrackCuePointWindow(Widget):
#    track_length = NumericProperty(0)
#    track_start  = NumericProperty(0, allownone = True)
#    track_end    = NumericProperty(0, allownone = True)

#    def __init__(self, *args, **kwargs):
#        super(TrackCuePointWindow, self).__init__(*args, **kwargs)
#        self._redraw = Clock.create_trigger(self.draw_window)
#        self.bind(track_length = self._redraw,
#                  track_start  = self._redraw,
#                  track_end    = self._redraw,
#                  size         = self._redraw,
#                  pos          = self._redraw)

#        self.bind(on_touch_down = self._on_touch_down,
#                  on_touch_up   = self._on_touch_up,
#                  on_touch_move = self._on_touch_move)
#        self._move_func = None
#        self._active_cue_point = None
#        self._cue_points = []


class TrackCuePointWindow(Widget):
    track_length = NumericProperty(0)
    track_start  = NumericProperty(0, allownone = True)
    track_end    = NumericProperty(0, allownone = True)

    def __init__(self, *args, **kwargs):
        super(TrackCuePointWindow, self).__init__(*args, **kwargs)
        self._redraw = Clock.create_trigger(self.draw_window)
        self._update_label_positions = Clock.create_trigger(self.update_label_positions)
        self.bind(track_length = self._redraw,
                  #track_start  = self._redraw,
                  #track_end    = self._redraw,
                  size         = self._redraw,
                  pos          = self._redraw)

        self.bind(track_length = self._update_label_positions)
                  #track_start  = self._update_label_positions,
                  #track_end    = self._update_label_positions)
        #size         = self._redraw,
        #          pos          = self._redraw)

        
        self.bind(on_touch_down = self._on_touch_down,
                  on_touch_up   = self._on_touch_up,
                  on_touch_move = self._on_touch_move)
        self._move_func = None
        self._active_cue_point = None
        self._cue_points = []
        self._time_labels = []

    def _on_touch_down(self, window, event):
        pass

    def _on_touch_up(self, window, event):
        pass

    def _on_touch_move(self, window, event):
        pass

    def add_cue_point(self, timestamp):
        self._cue_points.append(timestamp)
        self._cue_points = sorted(self._cue_points)
        self.draw_window()

    def remove_cue_point(self, timestamp):
        try:
            if timestamp > 0 and timestamp < self.track_end:
                self._cue_points.remove(timestamp)
                self._active_cue_point = max(min(self._active_cue_point, len(self._cue_points)), 0)
                self.previous_cue_point()
        except ValueError:
            pass
        
    def clear_cue_points(self):
        self._cue_points = [0, self.track_end] #sorted(self._cue_points)
        self._active_cue_point = None
        self.draw_window()


    def next_cue_point(self, timestamp = None):
        #if timestamp is not None:
        #    i = 0
        if self._active_cue_point == None:
            self._active_cue_point = 0
        else:
            self._active_cue_point += 1
            self._active_cue_point = max(min(self._active_cue_point, len(self._cue_points)), 0)

        self.draw_window()

    def previous_cue_point(self):
        if self._active_cue_point == None:
            self._active_cue_point = len(self._cue_points) - 1
        else:
            self._active_cue_point -= 1
            self._active_cue_point = max(min(self._active_cue_point, len(self._cue_points)), 0)

        self.draw_window()


    def get_cue_point_after(self, timestamp):
        i = 0

        for cue in self._cue_points:
            if cue > timestamp:
                return cue
        else:
            return self._cue_points[-1]

    def get_cue_point_before(self, timestamp):
        i = 0
        #print 'before', 
        for j in range(len(self._cue_points)):
            if self._cue_points[j] >= timestamp:
                if j > 0:
                    #print self._cue_points[j-1], timestamp
                    return self._cue_points[j-1]
                else:
                    return self._cue_points[j]
                    
        else:
            return self._cue_points[0]

        
    def current_cue_point(self):
        if self._active_cue_point is not None:
            return self._cue_points[self._active_cue_point]

    def modify_current_cue_point(self, amount):
        if self._active_cue_point is not None:
            try:
                t = self._cue_points[self._active_cue_point]
            except IndexError:
                return 
            t += amount
            if t > 0 and t < self.track_end:
                self._cue_points[self._active_cue_point] = t
                self._cue_points = sorted(self._cue_points)
                self.draw_window()
            
    def update_label_positions(self, *args):
        #self.canvas.clear()
        zero_x      = self.x 
        x_factor    = float(self.width) / self.track_length if self.track_length is not 0 else 1
        #track_start = self.track_start if self.track_start is not None else 0
        #track_end   = self.track_end if self.track_end is not None else self.track_length
        #print 'REDRAW'
        #with self.canvas:
        seconds = int(round(self.track_length / 1000000000))
        y = self.height - 40
        if seconds == 0:
            seconds = 300
        tick_space = (float(self.width) / seconds) * 3
        #if tick_space * seconds > self.width:
        #    tick_space -= 1
        #elif tick_space * seconds < self.width:
        #    tick_space += 1

        #overshoot = self.width - tick_space * seconds / 3
        for l in self._time_labels:
            self.remove_widget(l)
        #print seconds, self.width, overshoot
        #x = 0
        for i in range(seconds / 3):
            x = round(i * tick_space)
            if i % 5 == 0:
                l = Label(text = seconds_to_human_readable(i * 3))
                self.add_widget(l)
                self._time_labels.append(l)
                l.size_hint = (None, None)
                l.size  = 20, 12
                l.font_size = 11
                l.center_x = self.x + x
                l.y = y + 17
        
    def draw_window(self, *args):
        self.canvas.before.clear()
        zero_x      = self.x 
        x_factor    = float(self.width) / self.track_length if self.track_length is not 0 else 1
        track_start = self.track_start if self.track_start is not None else 0
        track_end   = self.track_end if self.track_end is not None else self.track_length
        #print 'REDRAW'
        with self.canvas.before:
            i = 0

            y = self.height - 40
            Color(1,1,1,1)
            Line(points = [self.x,y,self.width+self.x,y])

            seconds = int(round(self.track_length / 1000000000))
            
            if seconds == 0:
                seconds = 300
            tick_space = (float(self.width) / seconds) * 3
            #if tick_space * seconds > self.width:
            #    tick_space -= 1
            #elif tick_space * seconds < self.width:
            #    tick_space += 1

            overshoot = self.width - tick_space * seconds / 3
                
            #print seconds, self.width, overshoot
            x = 0
            for i in range(seconds / 3):
                x = round(i * tick_space)
                if i % 5 == 0:
                    Line(points = [self.x + x,
                                   y,
                                   self.x + x,
                                   y+15])
                else:
                    Line(points = [self.x + x,
                                   y,
                                   self.x + x,
                                   y+10])
                    
            i = 0
            for cue_point in self._cue_points:
                if i == self._active_cue_point:
                    Color(1,0,0,1)
                else:
                    Color(1,1,.1,1)
                Line(points = [cue_point * x_factor, self.y,
                               cue_point * x_factor, self.y + self.height - 40],
                     width = 1)
                Triangle(points = [cue_point * x_factor, self.y + self.height - 40,
                                   cue_point * x_factor - 5, self.y + self.height - 32,
                                   cue_point * x_factor + 5, self.y + self.height - 32])
                i += 1
            
Factory.register('TrackCuePointWindow', TrackCuePointWindow)




class TrackEditor(ModalView):
    seekbar        = ObjectProperty(None)
    turntable      = ObjectProperty(None)
    cut_window     = ObjectProperty(None)
    tick_line      = ObjectProperty(None)
    start_time_label = ObjectProperty(None)
    end_time_label   = ObjectProperty(None)
    album_cover    = ObjectProperty(None)
    track          = ObjectProperty(None)
    title_label    = ObjectProperty(None)
    artist_label   = ObjectProperty(None)
    queue          = ObjectProperty(None)
    short_list     = ObjectProperty(None)
    waveform       = ObjectProperty(None)
    volume         = NumericProperty(1.0)
    volume_controls = ObjectProperty(None)#NumericProperty(1.0)



    
    def __init__(self, player, volume_control = None, window = None, queue = None, short_list = None, *args, **kw):
        super(TrackEditor, self).__init__(*args, **kw)
        self._track              = None
        self._waveform_generator = None
        self._wave_buffer        = []
        #print player
        self._player             = pydjay.bootstrap.preview_player
        self.volume_controls     = pydjay.bootstrap.volume_control
        self._save_monitor_volume = 1.0
        #self._channel_layout     = channel_layout
        self._player.player.bind(on_end_of_stream = self._on_eos,
                                 track_duration   = self._update, #forward_track_duration,
                                 track_position   = self._update #forward_track_position
                          #is_connected     = self._update_is_connected,
                          #connected_host   = self._update_is_connected_to
                      )
        self.bind(on_dismiss = lambda *a: self.stop())
        
        # FOR NOW
        #self._player.connect_outputs(output_1 = "system:playback_5",
        #                             output_2 = "system:playback_6")


        self.bind(volume = self._set_volume)

        #v = self._volume_control.get_volume('main_player_monitor')
        
        #self._volume_control.set_volume(''value =  1.0, channels = self._channel_layout['main_player_monitor'])
        #self._restore_main_player = Animation(volume = 1.0, t = 'in_out_sine')
        
        #self._player.set_eos_callback(self._on_eos)
        self._duration = None
        #self.window = window
        self.queue = queue
        self.short_list = short_list


        #if self._current_selection is not None:
        #    self.master_list.adapter.get_view(self._current_selection)._update_background()



    
        Clock.schedule_once(self._post_init, -1)

    def _post_init(self, *a):
        self.cut_window.bind(track_length = self._update_track_labels,
                             track_start  = self._update_track_labels,
                             track_end    = self._update_track_labels,
                             size    = self._update_track_labels,
                             pos    = self._update_track_labels
        )
        self.cut_window.bind(#track_length = self._update_track_labels,
                             track_start  = self._update_track_start,
                             track_end    = self._update_track_end,
        )
        #self.tick_line.ticks=[Tick(tick_size=[4, 20])]
        #
        
        #self.tick_line.min_index = 0
        #self.tick_line.max_index = 30
        #self.tick_line.ticks = [Tick(tick_size=[4, 20], 
        #                            scale_factor = 60,
        #                            valign = 'top')]
        self._update_track_labels()

    def open(self):
        super(TrackEditor, self).open()
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self, 'text')
        self._keyboard.bind(on_key_down = self._on_keyboard_down)

    def dismiss(self):
        Window.release_keyboard(self)
        super(TrackEditor, self).dismiss()

        
    def _keyboard_closed(self):
        print('My keyboard have been closed!')
        self._keyboard.unbind(on_key_down = self._on_keyboard_down)
        self._keyboard = None


    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        #print('The key', keycode, 'have been pressed')
        #print(' - text is %r' % text)
        #print(' - modifiers are %r' % modifiers)

        key_seq = "+".join(modifiers+[keycode[1]])
        #print key_seq
        
        if key_seq == 'left': #activate previous cue point
            self.cue_point_window.previous_cue_point()
            pass
        elif key_seq == 'right': #activate next cue point
            self.cue_point_window.next_cue_point()
            pass
        elif key_seq == 'shift+left': #move start to previous cue point
            t = self.cue_point_window.get_cue_point_before(self.cut_window.track_start)
            self.cut_window.track_start = t
        
            #self.cut_window
            pass
        elif key_seq == 'shift+right': #move start to next cue point
            t = self.cue_point_window.get_cue_point_after(self.cut_window.track_start)
            self.cut_window.track_start = t

            pass
        elif key_seq == 'shift+ctrl+left': #move end to previous cue point
            t = self.cue_point_window.get_cue_point_before(self.cut_window.track_end)
            self.cut_window.track_end = t
            pass
        elif key_seq == 'shift+ctrl+right': #move end to next cue point
            t = self.cue_point_window.get_cue_point_after(self.cut_window.track_end)
            self.cut_window.track_end = t

            pass
        elif key_seq == 'backspace': #delete current cue point
            t = self.cue_point_window.current_cue_point()
            if t is not None:
                self.cue_point_window.remove_cue_point(t)
            
        elif key_seq == 'k': #move cue point to the left
            self.cue_point_window.modify_current_cue_point(-100000000)
            pass
        elif key_seq == 'l': #move cue point to the right
            self.cue_point_window.modify_current_cue_point(100000000)

        elif key_seq == 'shift+k': #move cue point to the left
            self.cue_point_window.modify_current_cue_point(-10000000)
        elif key_seq == 'shift+l': #move cue point to the right
            self.cue_point_window.modify_current_cue_point(10000000)
        elif key_seq == 'shift+ctrl+k': #move cue point to the left
            self.cue_point_window.modify_current_cue_point(-1000000000)
        elif key_seq == 'shift+ctrl+l': #move cue point to the right
            self.cue_point_window.modify_current_cue_point(1000000000)
        elif key_seq == 'c': #add cue point
            position = self._player.track_position or 0
            if position > 0:
                self.cue_point_window.add_cue_point(position)
            pass
        elif key_seq == 'escape':
            self.dismiss()

        elif key_seq == 'shift+s':
            #if self._current_selection is not None:
            self.short_list.add_shortlist_track(self._track)
            self.dismiss()
            #else:
            #    self.select(0)
            
        elif key_seq == 'shift+q':
            #if self._current_selection is not None:
            self.queue.add_track(self._track)
            self.dismiss()

            
        elif key_seq == 'enter': # start playback from current cue point
            t = self.cue_point_window.current_cue_point()
            self._player.play(self._track, t)
            #print 'track', t
            #pass
#            if self._current_selection is not None:
#                item = self.master_list.adapter[self._current_selection]
#                self.preview_player.play(item['item'].track)
        else:
            pydjay.core_logic.keyboard.key_map.key_pressed(keycode, modifiers)
        pass

        # Keycode is composed of an integer + a string
        # If we hit escape, release the keyboard
        #if keycode[1] == 'escape':
        #    keyboard.release()

        # Return True to accept the key. Otherwise, it will be used by
        # the system.
        return True


        
    def _update_track_labels(self, *a):
        if self._track is not None:
            self.start_time_label.opacity = 1
            self.end_time_label.opacity = 1

            self.start_time_label.text = seconds_to_human_readable(self._track.info.start_time / 1000000000) \
                                         if self._track.info.start_time is not None \
                                            else '0:00'
            self.end_time_label.text = seconds_to_human_readable(self._track.info.end_time / 1000000000) \
                                       if self._track.info.end_time is not None \
                                          else seconds_to_human_readable(self._track.info.stream_length / 1000000000)
            x_factor    = float(self.cut_window.width) / self.cut_window.track_length if self.cut_window.track_length is not 0 else 1
            self.start_time_label.center_x = self.cut_window.track_start * x_factor if self.cut_window.track_start is not None else 0
            self.end_time_label.center_x   = self.cut_window.track_end * x_factor if self.cut_window.track_end is not None else self.width
            #self.start_time_label.x   = max(self.start_time_label.x, 0) #self.cut_window.track_start*x_factor
            #self.end_time_label.right = min(self.end_time_label.right, self.width) #self.cut_window.track_end*x_factor
            
        else:
            self.start_time_label.opacity = 0
            self.end_time_label.opacity = 0

    def _update_track_start(self, *a):
        if self._track is not None:
            self._track.info.start_time = self.cut_window.track_start
        self._update_track_labels()


    def _update_track_end(self, *a):
        if self._track is not None:
            self._track.info.end_time = self.cut_window.track_end
        self._update_track_labels()
            #print "END", self._track.info.end_time

    def _on_eos(self, *a):
        #self.window.dismiss_preview_player()
        self._duck_main_player = Animation(volume = self._save_monitor_volume, #self._volume_control.get_volume('main_player_monitor'),
                                           t = 'in_out_sine', duration = 0.65)
        #self._duck_main_player.bind(on_complete = lambda *a: self.window.dismiss_preview_player())
        self._duck_main_player.start(self)

        
    def _set_volume(self, i, value):
        #print value
        self.volume_controls.set_volume('main_player_monitor', self.volume)#, self._channel_layout['main_player_monitor'])

    def _set_preview_volume(self, value):
        #print value
        self.volume_controls.set_volume('preview_player', value)#, self._channel_layout['preview_player'])

    #def _start_play(self):
    #    if self.queue is not None:
    #        track = self.queue.dequeue()
    #        self.seekbar.waveform.points = []
    #        self.set_track(track)
    #        self.play()

    #def play_pause(self):
    #    if self._track is not None:
    #        if self._player.is_playing:
    #            self.stop()
    #            #self.window.dismiss_preview_player()
    #        else:
    #            self.play()
        
    def play(self):
        self._player.play(self._track)
        #if self._track is not None:
        #    self._save_monitor_volume = self.volume_controls.get_volume('main_player_monitor')
        #    self._duck_main_player = Animation(volume = self.volume_controls.get_volume('main_player_monitor_mute'),
        #                                       t = 'in_out_sine', duration = 0.65)
        #    self._duck_main_player.bind(on_complete = self._do_play)
        #    self._duck_main_player.start(self)

    #def _do_play(self, *a):
    #    #print  self._track.info.start_time, self._track.info.end_time
    #    self._player.play(self._track.location, self._track.info.start_time, self._track.info.end_time)
    #        #Clock.schedule_interval(self._update, .1)


    def stop(self):
        #if self._track is not None:
        self._player.stop()
        #self._duck_main_player = Animation(volume = self._save_monitor_volume, #self._volume_control.get_volume('main_player_monitor'),
        #                                   t = 'in_out_sine', duration = 0.65)
        ##self._duck_main_player.bind(on_complete = lambda *a: self.window.dismiss_preview_player())
        #s#elf._duck_main_player.start(self)
        ##Clock.unschedule(self._update)
        


    def _do_seek(self, window, event):
        if self.seekbar.collide_point(*event.pos):
            x_coord = event.pos[0] - self.seekbar.x
            factor = float(x_coord) / self.seekbar.width
            val = factor * self.seekbar.max
            self._player.seek(int(val))
            #print val
            return False
        return True
        
            
    def set_track(self, track):
        self._player.stop()
        self._track = track
        self._duration = None
        #self.length_label.text   = seconds_to_human_readable(0)
        #self.position_label.text = seconds_to_human_readable(0)
        #self.seekbar.value = 0
        #self.seekbar.max = 1
        if self._track is not None:
            self.artist_label.text = self._track.metadata.artist
            self.title_label.text  = self._track.metadata.title
            self.album_label.text  = self._track.metadata.album
            if self._track.metadata.album_cover is not None:
                try:
                    self.album_cover.source = self._track.metadata.album_cover['small']#self.album_cover.memory_data = self._track.metadata.album_cover
                except:
                    self.album_cover.source = 'atlas://pydjay/gui/images/resources/default_album_cover'
            else:
                self.album_cover.source = 'atlas://pydjay/gui/images/resources/default_album_cover'


            if self._track.info.length is not None:
                self.waveform.max_value      = self._track.info.stream_length    
                self.waveform.waveform.x_max = self._track.info.stream_length
                self.cut_window.track_length = self.cue_point_window.track_length = self._track.info.stream_length
                self.cut_window.track_start  = self.cue_point_window.track_start = self._track.info.start_time if self._track.info.start_time is not None else 0
                self.cut_window.track_end    = self.cue_point_window.track_end = self._track.info.end_time if self._track.info.end_time is not None else self._track.info.stream_length
                self.cue_point_window.clear_cue_points()
                        
                #print  self.cut_window.track_start,  self.cut_window.track_end
            try:
                f = open(self._track.metadata.waveform, 'rb')
                arr = array.array('f')
                num_points = int(f.readline().split('\n')[0])
                arr.fromfile(f, num_points)
                ll = arr.tolist()
                offset = 0
                points = [ll[offset:offset+2] for offset in range(0, len(ll) - 1, 2)]
                points = sorted(points, cmp = lambda x,y: cmp(x[0], y[0]))
                self.waveform.waveform.points =  points#self._track.metadata.waveform
            except EOFError:
                ll = arr.tolist()
                offset = 0
                points = [ll[offset:offset+2] for offset in range(0, len(ll) - 1, 2)]
                points = sorted(points, cmp = lambda x,y: cmp(x[0], y[0]))
                self.waveform.waveform.points =  points#self._track.metadata.waveform                        
            except Exception, details:
                print details
                self.waveform.waveform.points = []
            finally:
                try:
                    f.close()
                except:
                    pass
                

    def _update(self, *a):
        if self._duration is None:
            self._duration = self._player.track_duration
            if self._duration is not None:
                self.waveform.max_value      = self._duration #self.queue.deck.track_duration
                self.waveform.waveform.x_max = self._duration #self.queue.deck.track_duration
            else:
                self.waveform.max_value = 1
            #if self._duration is not None:
            #    self.seekbar.max = self._duration
            #    self.length_label.text = seconds_to_human_readable(self._duration / 1000000000)
            #else:
            #    self.length_label.text = seconds_to_human_readable(0)
            #    self.seekbar.max = 1
        position = self._player.track_position or 0
        duration = self._duration
        if duration is None:
            pass
            #self.time_remaining_label.text = ""
        else:
            position = min(position, duration)
            #self.time_remaining_label.text = "-"+seconds_to_human_readable((duration - position) / 1000000000)
            self.waveform.value = position
        #if duration is not None:
        #    self.seekbar.value = position
        #    self.position_label.text = seconds_to_human_readable(position / 1000000000)
        #else:
        #    self.position_label.text = seconds_to_human_readable(0)

Builder.load_string(kv_string)
Factory.register('TrackEditor', TrackEditor)


buffer = []
if __name__ == '__main__':
    from pydjay.audio.player.player import AudioPlayer
    from pydjay.audio.player.volume import VolumeController
    main_player    = AudioPlayer("MainPlayer", 2)
    preview_player = AudioPlayer("PreviewPlayer", 2)
    volume_control_o = VolumeController("VolumeControl", num_channels = 6)
    #preview_volume_control = VolumeController("PrecuePlayerVolume")

    preview_player.connect_outputs(output_1 = "VolumeControl:input_5",
                                   output_2 = "VolumeControl:input_6")

    #preview_volume_control.connect_outputs(output_1 = "system:playback_5",
    #                                       output_2 = "system:playback_6")
    main_player.connect_outputs(output_1 = "VolumeControl:input_1",
                                output_2 = "VolumeControl:input_2")
    main_player.connect_outputs(output_1 = "VolumeControl:input_3",
                                output_2 = "VolumeControl:input_4")
    volume_control_o.connect_outputs(output_1 = "system:playback_1",
                                   output_2 = "system:playback_2",
                                   output_3 = "system:playback_5",
                                   output_4 = "system:playback_6",
                                   output_5 = "system:playback_5",
                                   output_6 = "system:playback_6")



    class VolumeControl:
        def __init__(self):
            self.channel_layout =  {'main_player':         [1,2],
                                    'main_player_monitor': [3,4],
                                    'preview_player':      [5,6]}
            self.volumes =  {'main_player':         1.0,
                             'main_player_monitor': 1.0,
                             'preview_player':      1.0,
                             'main_player_monitor_mute': 0.07}
            self.controller = volume_control_o


        def set_volume(self, channel, value):
            self.volumes[channel] = value
            if channel in self.channel_layout:
                self.controller.set_volumes(channels = self.channel_layout[channel], value = value)

        def get_volume(self, channel):
            return self.volumes[channel]

    volume_control = VolumeControl()
    volume_control.set_volume('main_player', 1.0)
    volume_control.set_volume('main_player_monitor', 1.0)
    volume_control.set_volume('preview_player', 1.0)
    volume_control.set_volume('main_player_monitor_mute', .07)


    
    from kivy.base import runTouchApp
    #from mediacentre.database.TVShows import database_pickle
    from kivy.core.window import Window
    from kivy.clock import Clock
    from kivy.uix.button import Button
    ## red background color
    #from jmc.gui import config


    import gi
    import pprint
    import sys
    import urllib
    gi.require_version("Gst", "1.0")
    #gi.require_version('Gtk', '3.0')
    from gi.repository import Gst, GObject as gobject, GLib
    
    from struct import unpack_from


    from pydjay.library.track import load_file
    
  


    Window.clearcolor = (0.0,0,0, 1)
    #Window.width = 350
    #Window.height = 475
    Window.size = (950, 375) #(700, 150)
    #index = 0
    #def add_item(*a):
    #    global index
    #    index += 1
    #    #print index
    #    item = Button(text= '%s'%index)
    #    bar.add_page(item)
    
    #foo = WaveformGenerator("/Users/jihemme/Python/DJ/pydjay/audio/test.mp3", 35000)




   

    
    #def add_point(total_time, timestamp, value):
    #    global buffer
    #    bar.seekbar.waveform.x_max = total_time
    #    buffer.append((timestamp, value))
    #    if len(buffer) == 150:
    #        bar.seekbar.waveform.points.extend(buffer)
    #        buffer = []

            
    #def done_points(points):
    #    bar.seekbar.waveform.points = points
    #    #x = open('ttt.txt','w')
    #    #x.write(str(points))
    #    #x.close()
    #foo.set_data_point_callback(add_point)
    #foo.set_process_done_callback(done_points)
    #def _foo(*a):
    #    Clock.schedule_interval(add_item, 1)
    #db = database_pickle.Database('/Users/jihemme/mediaserver_data')
    #from kivy.clock import Clock
    #foo = AnchorLayout(size_hint = (1,1), anchor_x = 'center', anchor_y = 'center')
    #init_gui()
    
    bar = PreviewPlayer(preview_player, volume_control)#Builder.load_string(kv_string)#FilesScreen(size_hint = (1,1))#size = (450,550))
    tra = load_file("/Users/jihemme/Python/DJ/test_audio/Algiers Hoodooo Woman - Dr. Michael White (Dancing in the Sky) .mp3")
    bar.set_track(tra)
    #bar.play()
    #bar.location_browser.set_default_locations()
    #bar.set_list(locations)
    #add_item()
    #add_item()
    
    #add_item()
    
    #add_item()
    
    #add_item()
    #Clock.schedule_once(add_item, 5)
    #button = Button(test="FOO",size_hint = (1,1))
    #bar.set_seasons(12)
    #bar.set_episodes(123, 45)
    #foo.add_widget(bar)
    #foo.add_widget(button)
    #button.bind(on_press = lambda *x: 
    #bar.set_show(db.get_tv_show('stargate-sg-1'))#db.get_tv_shows())
    runTouchApp(bar)#size=(400,200)))#, size_hint = (None, None)))
    #bar.shutdown()
    main_player.shutdown()
    preview_player.shutdown()
    volume_control_o.close()
    #bar.unload()
