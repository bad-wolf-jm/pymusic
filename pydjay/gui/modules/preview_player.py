import os
import re
import mimetypes
import array

from functools import partial
from threading import Thread
from os.path import getsize
from datetime import datetime


from kivy.graphics import Mesh, Color, Rectangle, Line, RoundedRectangle, Ellipse
from kivy.clock import mainthread, Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget

from kivy.properties import ObjectProperty, NumericProperty
from kivy.factory import Factory

from kivy.uix.popup import Popup

#from pydjay.audio.wavegen import WaveformGenerator
#from pydjay.audio.gst import AudioDecoder

#from pydjay.audio.player.player import AudioPlayer

from pydjay.uix import waveform_seekbar#screen, paged_grid, paged_display
from pydjay.gui import volume_slider
#from pydjay.gui.turntable import turntable
from pydjay.gui.utils import seconds_to_human_readable
#from pydjay.uix import memory_image, clickable_area
from kivy.animation import Animation
#from pydjay.uix import long_press_button
#from pydjay.uix import screen
import pydjay.bootstrap

#from pydjay.gui.files_screen import file_browser, location_browser
#from mediacentre.skins.default.theme import get_path


#kv_string = """
#<PPVolumeKnob@BoxLayout>:
#    orientation: 'vertical'
#    max: 2.0
#    knob: volume_slide
#    text: ""
#    channel: ""
#    controller: None
#    volume_controls: None
#    size_hint: 1,1
#    padding:[5,2,7,10]
#    spacing: 10
#    canvas:
#        Color:
#            rgba: 0.1,0.1,0.1,1
#        Rectangle:
#            size:self.size
#            pos: self.pos
#
#    Slider:
#        orientation: 'vertical'
#        id: volume_slide
#        size_hint: 1,1
#        min: 0
#        max: root.max
#        value: 1.0
#        on_value: root.volume_controls.set_volume(root.channel, self.value) if root.volume_controls is not None else False
#    Label:
#        size_hint: 1, None
#        height: 25
#        text: "%s"%int(volume_slide.value * 100) + "%"
#        font_size: 12
#    Label:
#        size_hint: 1, None
#        height: 25
#        text: root.text
#        text_size: self.size
#        font_size: 12
#        halign: 'center'
#        valign: 'middle'
##
#
##    #main_player_slider: main_player_slider
##    orientation: 'horizontal'
##    size_hint: 1,1
##    #title: "Volume setup:"
##    #auto_dismiss: True
##    #size_hint: None, None
##    #size: 700,500
##    canvas:
##        Color:
##            rgba: 0.1, 0.1, 0.1,1
##        Rectangle:
##            size:self.size
##            pos: self.pos#
##
##    BoxLayout:
#<PPVolumeControls>:
#    main_player_monitor_slider: monitor_slider
#    preview_player_slider: preview_slider
#    main_player_monitor_mute_slider:main_player_monitor_mute_slider
#
#    orientation: 'horizontal'
#    padding: [10,10,10,10]
#    spacing: 20
#    size_hint: 1,1
#
#    #PPVolumeKnob:
#    #    id: main_player_slider
#    #    text: "Main player"
#    #    max: 4.0
#    #    channel: 'main_player'
#    #    volume_controls: root.volume_controls
#
#    PPVolumeKnob:
#        id: monitor_slider
#        text: "Monitor"
#        max: 4.0
#        channel: 'main_player_monitor'
#        volume_controls: root.volume_controls
#        size_hint: 1,1
#
#    PPVolumeKnob:
#        id: preview_slider
#        text: "Preview player"
#        max: 4.0
#        channel: 'preview_player'
#        volume_controls: root.volume_controls
#        size_hint: 1,1
#
#    PPVolumeKnob:
#        id: main_player_monitor_mute_slider
#        text: "Monitor mute"
#        max: 0.5
#        channel: 'main_player_monitor_mute'
#        volume_controls: root.volume_controls
#        size_hint: 1,1
##
#
#"""


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
"""





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

<PreviewPlayer>:
    seekbar: seekbar
    #waveform: waveform
    #cut_window: cut_window
    #start_time_label: start_time_label
    #end_time_label: end_time_label
    #turntable:turntable
    album_cover: album_art
    artist_label: artist_label
    title_label:  title_label
    album_label:  album_label
    length_label:  length_label
    position_label:  position_label
    preview_volume: preview_volume
    monitor_volume: monitor_volume

    title: "PREVIEW"
    #time_remaining_label: time_remaining
    #orientation: 'horizontal'
    #size_hint: 1, 1
    #height:75

    BoxLayout:
        orientation: 'horizontal'

        size_hint: 1, 1

        BoxLayout:
            orientation: 'horizontal'
            size_hint: None, 1
            width: 140
            padding: [10,10,10,10]
            spacing: 20

            BoxLayout:
                orientation: 'vertical'
                size_hint: None, 1
                width: 50
                spacing: 10
                VolumeSlider:
                    id: preview_volume
                    size_hint: 1, 1
                Label:
                    text: "Preview"
                    font_size: 11
                    text_size: self.size
                    halign: 'center'
                    valign: 'middle'
                    size_hint: 1, None
                    height: 11

            BoxLayout:
                orientation: 'vertical'
                size_hint: None, 1
                width: 50
                spacing: 10
                VolumeSlider:
                    id: monitor_volume
                    size_hint: None, 1
                    width: 50
                Label:
                    text: "Monitor"
                    font_size: 11
                    text_size: self.size
                    halign: 'center'
                    valign: 'middle'
                    size_hint: 1, None
                    height: 11

        VDivider:

        BoxLayout:
            orientation: 'vertical'

            padding: [7,7,7,7]
            spacing: 0
            size_hint: 1, 1
            #canvas.before:
            #    Color:
            #        rgba: .3, .3, .3, 1
            #    Rectangle:
            #        pos:  self.pos
            #        size: self.size



            BoxLayout:
                orientation: 'horizontal'
                size_hint: 1, 1
                #height: 100
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

               # BoxLayout:
               #     orientation: 'vertical'
               #     size_hint: 1,1
               #     BoxLayout:
               #         orientation: 'horizontal'
               #         size_hint: 1,1
               #         size_hint_min_y: 100
                BoxLayout: 
                    orientation: 'vertical'
                    size_hint: 1,1
                    spacing: 6
                    Label:
                        id: title_label
                        size_hint: 1,1
                        #shorten: True
                        text: "<No track being previewed>"
                        text_size: self.size
                        font_size: 15
                        bold: True
                        halign: 'left'
                        valign: 'middle'
                        shorten: True
                        ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}

                    Label:
                        id: artist_label
                        size_hint: 1,1
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
                        size_hint: 1,1
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
                    size: 50,50
                    pos_hint: {'top': 1}
                    #text: 'SL'
                    image:'atlas://pydjay/gui/images/resources/add_to_shortlist'
                    on_press:
                        root.stop() 
                        root.window.show_preview_player(root._track, None, None, None)  #short_list.add_shortlist_track(root._track) if root._track is not None else None
                    Widget:
                        size_hint: 1,.5

            #BoxLayout:
            #    orientation: 'vertical'
            #    spacing: 10
            #    padding:[5,10,5,10]




            BoxLayout:
                orientation: 'vertical'
                size_hint: 1,None
                height: 30
                padding:[0,0,0,0]
                ProgressBar:
                    id: seekbar
                    pos_hint: {'center_y': 0.5}
                    size_hint: 1,None
                    height: 10
                    on_touch_down: root._do_seek(*args)

                BoxLayout:
                    orientation: 'horizontal'
                    size_hint: 1, None
                    height: 15
                    #spacing: 3
                    Label:
                        id: position_label
                        size_hint: None, 1
                        width: 40
                        text_size: self.size
                        text: "0:00"
                        color: .9,.9,.9,1
                        halign: 'left'
                        valign: 'middle'
                        shorten: True
                        ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}
                        #text: ""
                        font_size: 13

                    Widget:
                        size_hint: 1,None

                    Label:
                        id: length_label
                        size_hint: None, 1
                        width: 40
                        text_size: self.size
                        text: "0:00"
                        color: .9,.9,.9,1
                        halign: 'right'
                        valign: 'middle'
                        shorten: True
                        ellipsis_options: {'color':(1,0.5,0.5,1),'underline':True}
                        font_size: 13


            BoxLayout:
                orientation: 'horizontal'
                spacing: 5
                size_hint: 1, None
                height: 30
                Widget:
                    size_hint: 1,1
                ImageButton:
                    size_hint: None, None
                    size: 30,30
                    image_height: 30
                    image_width: 30
                    pos_hint: {'top': 1}
                    #text: 'SL'
                    image:'atlas://pydjay/gui/images/resources/pause'
                    on_press: root.stop() #short_list.add_shortlist_track(root._track) if root._track is not None else None
                ImageButton:
                    size_hint: None, None
                    size: 30,30
                    image_height: 30
                    image_width: 30

                    pos_hint: {'top': 1}
                    #text: 'SL'
                    image:'atlas://pydjay/gui/images/resources/play'
                    on_press: root.play(root._track) #short_list.add_shortlist_track(root._track) if root._track is not None else None
                Widget:
                    size_hint: 1,1


        #RelativeLayout:
        #    size_hint: 1,1
        #    id: player_stopped
        #    disabled: False
        #    #opacity: 1 if root.show_force_skip else 0
        #    canvas:
        #        Color:
        #            rgba: 0,0,0,.9
        #        Rectangle:
        #            size: self.size
        #            pos: 0,0 #self.pos

        #    BoxLayout:
        #        orientation: 'vertical'
        #        size_hint: .5, 1
        #        pos_hint: {'center_x':.5, 'center_y':.5}
        #        height: 50
        #        spacing: 10
        #        padding:[0,10,0,10]
        #        Label:
        #            size_hint: 1,1
        #            height: 40
        #            font_size: 20
        #            markup: True
        #            halign: 'center'
        #            valign: 'middle'
        #            text_size: self.size
#                    text: "No track currently playing" 
#
"""

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
        #print x, foo
        if foo + 7000000000 <= self.track_end:
            self.track_start = foo if foo > 0 else 0
        
            
        #if self.track_end < self.track_start:
        #    self.track_end = self.track_start + 7000000000
        pass
    def _move_end_time(self, x, y):
        x_factor = float(self.width) / self.track_length if self.track_length is not 0 else 1
        #self.track_end =  int(x / x_factor)
        if x > self.width - 10:
            x = self.width
        foo =   int(x / x_factor)
        if foo - 7000000000 >= self.track_start:
            self.track_end = foo if foo < self.track_length else self.track_length

        ##if self.track_end < self.track_start:
        #    self.track_start = self.track_end - 7000000000
        #pass

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
        zero_x   = self.x 
        x_factor = float(self.width) / self.track_length if self.track_length is not 0 else 1
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
"""

class PreviewPlayer(RelativeLayout):
    seekbar          = ObjectProperty(None)
    turntable        = ObjectProperty(None)
    cut_window       = ObjectProperty(None)
    start_time_label = ObjectProperty(None)
    end_time_label   = ObjectProperty(None)
    album_cover      = ObjectProperty(None)
    track            = ObjectProperty(None)
    title_label      = ObjectProperty(None)
    artist_label     = ObjectProperty(None)
    queue            = ObjectProperty(None)
    monitor_volume   = ObjectProperty(None)
    preview_volume   = ObjectProperty(None)
    short_list       = ObjectProperty(None)
    window           = ObjectProperty(None)
    volume           = NumericProperty(1.0)
    volume_controls  = ObjectProperty(None)
    player           = ObjectProperty(None)#NumericProperty(1.0)
    
    def __init__(self, *args, **kwargs): #player, volume_control = None, window = None, queue = None, short_list = None, *args, **kw):
        super(PreviewPlayer, self).__init__(*args, **kwargs)
        self._track              = None
        #self._waveform_generator = None
        #self._wave_buffer        = []
        #print player
        self.player = pydjay.bootstrap.preview_player  #, player
        self.player.player.bind(on_end_of_stream = self._on_eos,
                                track_duration   = self._update, #forward_track_duration,
                                track_position   = self._update #forward_track_position
                         #is_connected     = self._update_is_connected,
                         #connected_host   = self._update_is_connected_to
                     )
        self.volume_controls     = None #volume_control
        self._save_monitor_volume = 1.0
        pydjay.bootstrap.volume_control.bind(main_player_monitor = self._update_monitor_volume,
                                        preview_player = self._update_preview_volume)
        #self._channel_layout     = channel_layout
        #self.bind(player = self._connect_player)
        
        #self.bind(on_dismiss = lambda *a: self.stop())
        
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
        #self.queue = queue
        #self.short_list = short_list
        Clock.schedule_once(self._post_init, -1)


    def _update_monitor_volume(self, *args):
        self.monitor_volume.volume = pydjay.bootstrap.volume_control.main_player_monitor
        
    def _update_preview_volume(self, *args):
        self.preview_volume.volume = pydjay.bootstrap.volume_control.preview_player

    def _set_monitor_volume(self, *args):
        pydjay.bootstrap.volume_control.main_player_monitor = self.monitor_volume.volume
        
    def _set_preview_volume(self, *args):
        pydjay.bootstrap.volume_control.preview_player = self.preview_volume.volume 
        
    def _post_init(self, *a):
        self.preview_volume.bind(volume = self._set_preview_volume)
        self.monitor_volume.bind(volume = self._set_monitor_volume)

        pass
        #self.cut_window.bind(track_length = self._update_track_labels,
        #                     track_start  = self._update_track_labels,
        #                     track_end    = self._update_track_labels,
        #                     size    = self._update_track_labels,
        #                     pos    = self._update_track_labels
        #)
        #self.cut_window.bind(#track_length = self._update_track_labels,
        #                     track_start  = self._update_track_start,
        #                     track_end    = self._update_track_end,
        #)
        ##
        #self._update_track_labels()

    #def _connect_player(self, *args):
    #    #self.player.bind(on_end_of_stream = self._on_eos,
    #    #                  track_duration   = self._update, #forward_track_duration,
    #    #                  track_position   = self._update #forward_track_position
    #    #                  #is_connected     = self._update_is_connected,
    #    #                  #connected_host   = self._update_is_connected_to
    #    #              )
    #    pass
        
        
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
        pass
        ##self.window.dismiss_preview_player()
        #self._duck_main_player = Animation(volume = self._save_monitor_volume, #self._volume_control.get_volume('main_player_monitor'),
        #                                   t = 'in_out_sine', duration = 0.65)
        ##self._duck_main_player.bind(on_complete = lambda *a: self.window.dismiss_preview_player())
        #self._duck_main_player.start(self)

        
    def _set_volume(self, i, value):
        #print value
        self.volume_controls.set_volume('main_player_monitor', self.volume)#, self._channel_layout['main_player_monitor'])

    #def _set_preview_volume(self, value):
    #    #print value
    #    self.volume_controls.set_volume('preview_player', value)#, self._channel_layout['preview_player'])

    #def _start_play(self):
    #    if self.queue is not None:
    #        track = self.queue.dequeue()
    #        self.seekbar.waveform.points = []
    #        self.set_track(track)
    #        self.play()

    #def play_pause(self):
    #    if self._track is not None:
    #        if self.player.is_playing:
    #            self.stop()
    #            #self.window.dismiss_preview_player()
    #        else:
    #            self.play()
        
    def play(self, track):
        self.set_track(track)
        if self._track is not None:
            self.player.play(track)


    def pause(self):
        self.player.pause()

        #if self.player is not None:
        #    if self._track is not None:
        #        self._save_monitor_volume = self.volume_controls.get_volume('main_player_monitor')
        #        self._duck_main_player = Animation(volume = self.volume_controls.get_volume('main_player_monitor_mute'),
        #                                           t = 'in_out_sine', duration = 0.5)
        #        self._duck_main_player.bind(on_complete = self._do_play)
        #        self._duck_main_player.start(self)

    #def _do_play(self, *a):
    #    #print  self._track.info.start_time, self._track.info.end_time
    #    self.player.play(self._track.location, self._track.info.start_time, self._track.info.end_time)
    #    self._is_playing = True
    #        #Clock.schedule_interval(self._update, .1)


    def stop(self):
        #if self._track is not None:
        self.player.stop()
        #self._duck_main_player = Animation(volume = self._save_monitor_volume, #self._volume_control.get_volume('main_player_monitor'),
        #                                   t = 'in_out_sine', duration = 0.5)
        ##self._duck_main_player.bind(on_complete = lambda *a: self.window.dismiss_preview_player())
        #self._duck_main_player.start(self)
        ##Clock.unschedule(self._update)
        


    def _do_seek(self, window, event):
        if self.seekbar.collide_point(*event.pos):
            x_coord = event.pos[0] - self.seekbar.x
            factor = float(x_coord) / self.seekbar.width
            val = factor * self.seekbar.max
            self.player.seek(int(val))
            #print val
            return False
        return True
        
            
    def set_track(self, track):
        self.player.stop()
        self._track = track
        self._duration = None
        self.length_label.text   = seconds_to_human_readable(0)
        self.position_label.text = seconds_to_human_readable(0)
        self.seekbar.value = 0
        self.seekbar.max = 1
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


            #if self._track.info.length is not None:
            #    self.waveform.max_value      = self._track.info.stream_length    
            #    self.waveform.waveform.x_max = self._track.info.stream_length
            #    self.cut_window.track_length = self._track.info.stream_length
            #    self.cut_window.track_start  = self._track.info.start_time if self._track.info.start_time is not None else 0
            #    self.cut_window.track_end    = self._track.info.end_time if self._track.info.end_time is not None else self._track.info.stream_length
                
                        
                #print  self.cut_window.track_start,  self.cut_window.track_end
            #try:
            #    f = open(self._track.metadata.waveform, 'rb')
            #    arr = array.array('f')
            #    num_points = int(f.readline().split('\n')[0])
             #   arr.fromfile(f, num_points)
             #   ll = arr.tolist()
             #   offset = 0
             #   points = [ll[offset:offset+2] for offset in range(0, len(ll) - 1, 2)]
             #   points = sorted(points, cmp = lambda x,y: cmp(x[0], y[0]))
             #   self.waveform.waveform.points =  points#self._track.metadata.waveform
            #except EOFError:
            #    ll = arr.tolist()
            #    offset = 0
            #    points = [ll[offset:offset+2] for offset in range(0, len(ll) - 1, 2)]
            #    points = sorted(points, cmp = lambda x,y: cmp(x[0], y[0]))
            #    self.waveform.waveform.points =  points#self._track.metadata.waveform                        
            #except Exception, details:
            #    print details
            #    self.waveform.waveform.points = []
            #finally:
            #    try:
            #        f.close()
            #    except:
            #        pass
                

    def _update(self, *a):
        if self._duration is None:
            self._duration = self.player.track_duration
            if self._duration is not None:
                self.seekbar.max = self._duration
                self.length_label.text = seconds_to_human_readable(self._duration / 1000000000)
            else:
                self.length_label.text = seconds_to_human_readable(0)
                self.seekbar.max = 1
        position = self.player.track_position or 0
        duration = self._duration
        if duration is not None:
            self.seekbar.value = position
            self.position_label.text = seconds_to_human_readable(position / 1000000000)
        else:
            self.position_label.text = seconds_to_human_readable(0)

Builder.load_string(kv_string)
Factory.register('PreviewPlayer', PreviewPlayer)


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
