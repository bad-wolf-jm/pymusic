import os
import re
import mimetypes
import array

#from functools import partial
#from threading import Thread
#from os.path import getsize
#from datetime import datetime


#from kivy.graphics import Mesh, Color, Rectangle, Line, RoundedRectangle, Ellipse
from kivy.clock import mainthread, Clock
#from kivy.lang import Builder
#from kivy.properties import ObjectProperty
#from kivy.uix.boxlayout import BoxLayout
#from kivy.uix.relativelayout import RelativeLayout
#from kivy.uix.widget import Widget
from kivy.event import EventDispatcher

from kivy.properties import ObjectProperty, NumericProperty
#from kivy.factory import Factory

#from kivy.uix.popup import Popup

#from pydjay.audio.wavegen import WaveformGenerator
#from pydjay.audio.gst import AudioDecoder

#from pydjay.audio.player.player import AudioPlayer

#from pydjay.uix import waveform_seekbar#screen, paged_grid, paged_display
#from pydjay.gui.turntable import turntable
#from pydjay.gui.utils import seconds_to_human_readable
#from pydjay.uix import memory_image, clickable_area
from kivy.animation import Animation
#from pydjay.uix import long_press_button
#from pydjay.uix import screen
#import pydjay.core

class PreviewPlayer(EventDispatcher):#RelativeLayout):
    #seekbar          = ObjectProperty(None)
    #turntable        = ObjectProperty(None)
    #cut_window       = ObjectProperty(None)
    #start_time_label = ObjectProperty(None)
    #end_time_label   = ObjectProperty(None)
    #album_cover      = ObjectProperty(None)
    #track            = ObjectProperty(None)
    #title_label      = ObjectProperty(None)
    #artist_label     = ObjectProperty(None)
    #queue            = ObjectProperty(None)
    #short_list       = ObjectProperty(None)
    #window           = ObjectProperty(None)
    volume           = NumericProperty(1.0)
    track_duration   = NumericProperty(None, allownone = True)
    track_position   = NumericProperty(None, allownone = True)
    #volume_controls  = ObjectProperty(None)
    #player           = ObjectProperty(None)#NumericProperty(1.0)
    
    def __init__(self, player, volume, *args, **kwargs): #player, volume_control = None, window = None, queue = None, short_list = None, *args, **kw):
        super(PreviewPlayer, self).__init__(*args, **kwargs)
        self._track  = None
        self.player  = player#, pydjay.core.preview_player  #, player
        self.player.bind(on_end_of_stream = self._on_eos,
                         track_duration   = self._forward_track_duration,
                         track_position   = self._forward_track_position)
        self.volume_controls      = volume
        self._save_monitor_volume = 1.0
        self._is_playing          = False
        
        self._pause_track_timestamp = None #self.player.track_position
        self._pause_track = None #self._track
        self.bind(volume = self._set_volume)



    def _forward_track_duration(self, *a):
        self.track_duration = self.player.track_duration

    def _forward_track_position(self, *a):
        self.track_position = self.player.track_position

        
    def _on_eos(self, *a):
        self._duck_main_player = Animation(volume = self._save_monitor_volume, #self._volume_control.get_volume('main_player_monitor'),
                                           t = 'in_out_sine', duration = 0.5)
        self._duck_main_player.start(self)

        
    def _set_volume(self, i, value):
        #print value
        self.volume_controls.main_player_monitor = self.volume#, self._channel_layout['main_player_monitor'])

    #def _set_preview_volume(self, value):
    #    self.volume_controls.set_volume('preview_player', value)#, self._channel_layout['preview_player'])

    #def play_pause(self):
    #    if self._track is not None:
    #        if self.player.is_playing:
    #            self.stop()
    #        else:
    #            self.play()
        
    def play(self, track, start_time = None, end_time = None):
        if self._is_playing:
            self._track = track
            self._start_time = start_time if start_time is not None else self._track.info.start_time
            self._end_time   = end_time if end_time is not None else self._track.info.end_time
            self._do_play(self._start_time, self._end_time)
        else:
            if self._fade_state == 'fading_out':
                self._track = track
                self._start_time = start_time if start_time is not None else self._track.info.start_time
                self._end_time   = end_time if end_time is not None else self._track.info.end_time
            elif self._fade_state == 'fading_in':
                self._track = track
                self._start_time = start_time if start_time is not None else self._track.info.start_time
                self._end_time   = end_time if end_time is not None else self._track.info.end_time
                self._duck_main_player.cancel(self)
            self._duck_main_player = Animation(volume = self.volume_controls.get_volume('main_player_monitor_mute'),
                                               t = 'in_out_sine', duration = 0.5)
            self._duck_main_player.start(self)
            self._duck_main_player.bind(on_complete = self._do_play)
            self._fade_state = 'fading_out'
            #else:
                
        
        #if not self._is_playing:
        #    self._save_monitor_volume = self.volume_controls.get_volume('main_player_monitor')
        #    if self._duck_main_player is None:
        #        self._duck_main_player = Animation(volume = self.volume_controls.get_volume('main_player_monitor_mute'),
        #                                           t = 'in_out_sine', duration = 0.5)
        #        self._duck_main_player.start(self)
        #        self._duck_main_player.bind(on_complete = self._do_play)
        #        self._fade_state = 'fading_out'
        #    
        #else:
        #    if self._duck_main_player is not None:
        #        self._duck_main_player.bind(on_complete = self._do_play)
        #    else:
        #        self._do_play()
    def pause(self):
        #if self._is_playing:
        #pass#self.player.pause()
        print "TRACK PAUSING"
        if self._is_playing:
            if self._track is not None:
                self._pause_track_timestamp = self.player.track_position
                self._pause_track = self._track
                self.player.stop()
            self._is_playing = False
        else:
            if self._pause_track is not None:
                if self._pause_track == self._track:
                    s_t = self._pause_track_timestamp if self._pause_track_timestamp is not None else 0
                    self.player.play(self._track.location, s_t, self._track.info.end_time)
                    self._is_playing = True
                    return
            if self._track is not None:
                print 'foobar'
                self.play(self._track, self._start_time, self._end_time)

    def _do_play(self, *a):
        #print  self._track.info.start_time, self._track.info.end_time
        #s_t = start_time if start_time is not None else self._track.info.start_time
        #e_t = end_time if end_time is not None else self._track.info.end_time
        
        self.player.play(self._track.location, self._start_time, self._end_time) #s_t, e_t) #self._track.info.start_time, self._track.info.end_time)
        self._is_playing = True
        self._duck_main_player = None
        self._fade_state = 'idle'

    def __stopped(self, *a):
        #print  self._track.info.start_time, self._track.info.end_time
        self._fade_state = 'idle'



    def stop(self):
        #if self._track is not None:
        self.player.stop()
        self._fade_state = 'fading_in'
        self._duck_main_player = Animation(volume = self._save_monitor_volume, #self._volume_control.get_volume('main_player_monitor'),
                                           t = 'in_out_sine', duration = 0.5)
        self._duck_main_player.bind(on_complete = self.__stopped)
        self._duck_main_player.start(self)
        self._is_playing = False
        #Clock.unschedule(self._update)
        


    def seek(self, timestamp):
        #if self.seekbar.collide_point(*event.pos):
        #    x_coord = event.pos[0] - self.seekbar.x
        #    factor = float(x_coord) / self.seekbar.width
        #    val = factor * self.seekbar.max
        self.player.seek(timestamp)
        #    #print val
        #    return False
        #return True
        
    def shutdown(self):
        self.player.shutdown()
        #self.stop()
        #self._output.close()
        #print "shutting down", self.player_name
    #def set_track(self, track):
    #    self.player.stop()
    #    self._track = track
    #    self._duration = None
        #self.length_label.text   = seconds_to_human_readable(0)
        #self.position_label.text = seconds_to_human_readable(0)
        #self.seekbar.value = 0
        #self.seekbar.max = 1
        #if self._track is not None:
        #    self.artist_label.text = self._track.metadata.artist
        #    self.title_label.text  = self._track.metadata.title
        #    self.album_label.text  = self._track.metadata.album
        #    if self._track.metadata.album_cover is not None:
        #        try:
        #            self.album_cover.source = self._track.metadata.album_cover['small']#self.album_cover.memory_data = self._track.metadata.album_cover
        #        except:
        #            self.album_cover.source = 'atlas://pydjay/gui/images/resources/default_album_cover'
        #    else:
        #        self.album_cover.source = 'atlas://pydjay/gui/images/resources/default_album_cover'


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
                

    #def _update(self, *a):
    #    if self._duration is None:
    #        self._duration = self.player.track_duration
    #        if self._duration is not None:
    #            self.seekbar.max = self._duration
    #            self.length_label.text = seconds_to_human_readable(self._duration / 1000000000)
    #        else:
    #            self.length_label.text = seconds_to_human_readable(0)
    #            self.seekbar.max = 1
    #    position = self.player.track_position or 0
    #    duration = self._duration
    #    if duration is not None:
    #        self.seekbar.value = position
    #        self.position_label.text = seconds_to_human_readable(position / 1000000000)
    #    else:
    #        self.position_label.text = seconds_to_human_readable(0)

#Builder.load_string(kv_string)
#Factory.register('PreviewPlayer', PreviewPlayer)


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
