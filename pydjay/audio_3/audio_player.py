import os
import re
import mimetypes
import threading
import socket
import functools
import json
import time
import cPickle as pickle
import array

from functools import partial
from threading import Thread
from os.path import getsize
from datetime import datetime

from kivy.clock import mainthread, Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty, AliasProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.bubble import Bubble
from kivy.uix.popup import Popup
from kivy.uix.button import Button

from kivy.properties import ObjectProperty
from kivy.factory import Factory
from kivy.event import EventDispatcher
from pydjay.audio.wavegen import WaveformGenerator
from pydjay.audio.gst import AudioDecoder
from pydjay.audio.remote import SlavePlayer

from pydjay.library import save_to_current_session

from pydjay.uix import waveform_seekbar#screen, paged_grid, paged_display
from pydjay.gui.turntable import turntable
#from track_upload import UploadTrack
from pydjay.gui.utils import seconds_to_human_readable
from pydjay.utils.protocol import MAGIC
#from pydjay.uix import clickable_area
#from pydjay.uix import long_press_button
from pydjay.uix.slider import XSlider

#from pydjay.gui.files_screen import file_browser, location_browser
#from mediacentre.skins.default.theme import get_path

from kivy.logger import Logger




class AudioPlayer(EventDispatcher):
    state                = StringProperty(None, allownone = True)
    track                = ObjectProperty(None, allownone = True)
    track_duration       = NumericProperty(None, allownone = True)
    track_position       = NumericProperty(None, allownone = True)
    is_connected         = BooleanProperty(False)
    connected_host       = StringProperty(None, allownone = True)

    #show_force_skip  = BooleanProperty(False)
    
    #uploading       = BooleanProperty(False)
    #upload_progress = NumericProperty(0)
    #upload_track    = ObjectProperty(None, allownone = True)

    
    def __init__(self, *args, **kw):
        super(AudioPlayer, self).__init__(*args, **kw)
        self.register_event_type('on_end_of_stream')
        self._player             = AudioDecoder()
        self._player.set_eos_callback(self._on_eos)
        #self.register_event_type('on_play')
        #self.register_event_type('on_stop')
        #self._current_session = set([])
        #self._is_connected = False
        self._track_promise = None
        self._current_time = None
                
    #def set_current_session(self, session):
    #    self._current_session = set(session)

    #def has_played(self, location):
    #    if self.track is not None and (location == self.track.location):
    #        return True
    #    return location in self._current_session

    #def _connect_remote(self):
    #    if not self._is_connected:
    #        popup = ConnectToRemote(self)
    #    else:
    #        popup = DisconnectFromRemote(self)
    #    popup.open()
            
    def on_end_of_stream(self, *args):
        pass

#    def on_play(self, *args):
#        pass

#    def on_stop(self, *args):
#        pass
    
    def connect_to_remote(self, name, address, port):
        Logger.info('MainPlayer: Connecting to remote player <%s> at <%s:%s>', name, address, port)
        #self.start_queue_button.disabled = True
        #self._stop_waveform()
        #print address
        
        self._player = SlavePlayer(address, port)
        self._player.set_eos_callback(self._on_eos)
        self._player.bind(is_connected = self._update_is_connected,
                          is_connected_to = self._update_is_connected_to)
        self._player.connect(abort = self._abort_connection)
        #self.turntable.player = self._player
        Logger.info('MainPlayer: Connected to remote player %s at %s', name, address)


    def disconnect_from_remote(self):
        try:
            self._player.disconnect()
        except:
            pass
        finally:
            self._abort_connection()

    @mainthread
    def _abort_connection(self):
        #Logger.info('MainPlayer: Aborting connection')
        #if self.queue is not None:
        #    self.queue.disconnect_from_remote()
        self._player = AudioDecoder()
        self._player.set_eos_callback(self._on_eos)
        #self.turntable.player = self._player
        #self.start_queue_button.disabled = False
        self._connected = False

    def _update_is_connected(self, foo, value):
        if self._player.is_connected:
            self.is_connected = True
            self.connected_host = 'Not Connected'
        else:
            Logger.warning("MainPlayerDeck: Connection to remote player has been lost, reverting to local player")
            self.stop()
            self._player = AudioDecoder()
            self.is_connected = False
            


    def _update_is_connected_to(self, foo, value):
        #print value
        if value == "":
            self.connected_host = 'Not Connected' #if not self.is_connected else "Unknown host"
            #if self.queue is not None:
            #    self.queue.disconnect_from_remote()
        else:
            self.connected_host = value
            #$if self.queue is not None:
            #    self.queue.connect_to_remote(self._player._host, self._player._file_port, self._player._control_client)



    def shutdown(self):
        try:
            self._player.shutdown()
        except:
            pass


    def _get_remaining_time(self):
        if None not in [ self.track_duration, self.track_position]:
            return self.track_duration - self.track_position
        return 0
    def _set_remaining_time(self, value):
        return False
    remaining_track_time = AliasProperty(_get_remaining_time, _set_remaining_time, bind = ['track_position', 'track_duration'])
        
                
    def _on_eos(self):
        Logger.info('MainPlayer: End of stream %s', self.track)
        self.dispatch('on_end_of_stream', self.track)
        Clock.unschedule(self._update)
        self.track          = None
        self.track_duration = None
        self.track_position = None




    def load_track(self, track):
        def _do_set_track(track):
            self._track_promise = None
        def _cancel_set_track():
            self.track = None
            self._track_promise = None
            
        #self.track = track
        self.stop()
        #if isinstance(track, UploadTrack):
        #    track.add_completion_callback(_do_set_track)
        #    track.add_cancelled_callback(_cancel_set_track)
        #    self.track = track._track.track
        #    self._track_promise = track
        #else:
        self.track = track
        self._track_promise = None
        if track is None:
            self.state = 'empty'
            #self.play()
            #self.dismiss_countdown()


    
    #def _load_next(self, *args):
    #    def _do_play_track(track):
    #        self.finish_set_track()
    #        self.play()
            
    #    Logger.info('MainPlayer: Loading next track')
    #    self.seekbar.waveform.points = []
    #    if self.queue is not None and not self.queue.is_empty:
     #       if not self._stop_counter:
     #           track = self.queue.dequeue(incomplete = _do_play_track)
     #           if isinstance(track, UploadTrack):
     #               track.add_completion_callback(_do_play_track)
     #               track.add_cancelled_callback(self._load_next)
     #               self._set_track_metadata(track._track.track)
     #               self.dismiss_countdown()
     #               #self._track = track._track
     #           else:
     #               self.set_track(track)
     #               self.play()
     #               self.dismiss_countdown()
     #   elif self.queue.is_empty:
     #       self._queue_playing = False
     #       self._watch_queue_data()
#
#                    #track.add_completion_callback(self._upload_queue_head)
 
        
#    def _start_play(self):
#        if self.queue is not None and not self.queue.is_empty:
#            Clock.schedule_once(self._load_next, 0)
            
    #def start_queue(self):
    #    if not self._queue_playing:
    #        if self.queue is not None and not self.queue.is_empty:
    #            Logger.info('MainPlayer: Starting queue')
    #            self._queue_playing = True
    #            self._stop_counter = False
    #            self._start_play()
    #            self.start_queue_button.text = 'STOP'
    #    else:
    #        if self._stop_counter:
    #            Logger.info('MainPlayer: Cancel stop')
    #            self._stop_counter = False
    #            self.start_queue_button.text = 'STOP'
    #            self.stopping_message.text = ""
    #        else:
    #            Logger.info('MainPlayer: Setting queue to stop after the current track')
    #            self._stop_counter = True
    #            self.start_queue_button.text = 'CANCEL'
    #            self.stopping_message.text = "Queue will stop after this song"
        
    def play(self):
        def _do_play_track(track):
            self._player.load_path(self.track.location)
            #self.set_track(track)
            self._current_time = time.time()
            self._player.start_decoder()
            Clock.schedule_interval(self._update, .1)
            self.state = 'playing'
            
        if self.track is not None:
            Logger.info('MainPlayer: Starting playback of %s', self.track)
            #if isinstance(self._track_promise, UploadTrack):
            #    self._track_promise.add_completion_callback(_do_play_track)
            #else:
            _do_play_track(self.track)
            
            

    def stop(self):
        self._player.stop()
        Clock.unschedule(self._update)
        self.track          = None
        self.track_duration = None
        self.track_position = None
        self.state = 'stopped'

    def pause(self):
        self._player.pause()
        Clock.unschedule(self._update)
        #$self.track          = None
        #$self.track_duration = 0
        #$self.track_position = 0
        self.state = 'paused'
        
    #def set_track(self, track):
    #    self._set_track_metadata(track)
    #    self.finish_set_track()
            
    #def _set_track_metadata(self, track):
    #    Logger.info('MainPlayer: Setting track')
    #    self._track = track
    #    self.track = track
    #    if self._track is not None:
    #        #self._player.load_path(self._track.location)
    #        self.artist_label.text = self._track.metadata.artist
    #        self.title_label.text = self._track.metadata.title
    #        self.turntable.set_track(self._track)
    #        self._duration = None
    #        self._stop_waveform()
            
            #if self._track.metadata.waveform is None:
            #    Logger.info('MainPlayer: No waveform found for [%s], generating a new one', self._track)
            #    self._generate_track_waveform()
            #else:
            #    try:
            #        Logger.info('MainPlayer: Setting the waveform to the track\'s waveform')
            #        if self._track.info.length is not None:
            #            self.seekbar.waveform.x_max = self._track.info.length * 1000000                        
            #        self.seekbar.waveform.points = self._track.metadata.waveform
            #        if self._track.metadata.waveform is not None:
            #            self._wave_buffer = self._track.metadata.waveform
            #            Clock.schedule_interval(self._send_wavepoints_to_remote_player, 0.1)
            #    except:
            #        Logger.info('MainPlayer: Setting the waveform failed for [%s]... generating a new one', self._track)
            #        self._generate_track_waveform()


    #def finish_set_track(self):
    #    Logger.info('MainPlayer: Setting track')
    #    #self._track = track
    #    if self._track is not None:
    #        self._player.load_path(self._track.location)
    #        #self.artist_label.text = self._track.metadata.artist
    #        #self.title_label.text = self._track.metadata.title
    #        #self.turntable.set_track(self._track)
    #        #self._duration = None
    #        #self._stop_waveform()
    #        
    #        if self._track.metadata.waveform is None:
    #            Logger.info('MainPlayer: No waveform found for [%s], generating a new one', self._track)
    #            self._generate_track_waveform()
    #        else:
    #            try:
    #                Logger.info('MainPlayer: Setting the waveform to the track\'s waveform, track length: %s', self._track.info.length)
    #                if self._track.info.length is not None:
    #                    self.seekbar.max_value      = self._track.info.length * 1000000    
    #                    self.seekbar.waveform.x_max = self._track.info.length * 1000000                        
    #                    #Logger.info('MainPlayer: Setting the waveform to the track\'s waveform %s')
    #                #if self._track.metadata.waveform is not None:
    #                try:
    #                    f = open(self._track.metadata.waveform, 'rb')
    #                    arr = array.array('f')
    #                    arr.fromfile(f, 70000)
    #                    ll = arr.tolist()
    #                    offset = 0
    #                    points = [ll[offset:offset+2] for offset in range(0, len(ll) - 1, 2)]
    #                    points = sorted(points, cmp = lambda x,y: cmp(x[0], y[0]))
    #                    self.seekbar.waveform.points =  points#self._track.metadata.waveform
    #                except EOFError:
    #                    ll = arr.tolist()
    #                    offset = 0
    #                    points = [ll[offset:offset+2] for offset in range(0, len(ll) - 1, 2)]
    #                    points = sorted(points, cmp = lambda x,y: cmp(x[0], y[0]))
    #                    self.seekbar.waveform.points =  points#self._track.metadata.waveform                        
    #                except Exception:
    #                     self.seekbar.waveform.points = []
    #                finally:
    #                    try:
    #                        f.close()
    #                    except:
    #                        pass
    #                    #Clock.schedule_interval(self._send_wavepoints_to_remote_player, 0.1)
    #            except Exception, details:
    #                Logger.error('MainPlayer: Setting the waveform failed for [%s]... generating a new one, %s', self._track, details)
    #                self._generate_track_waveform()


    #def _send_wavepoints_to_remote_player(self, *args):
    #    if len(self._wave_buffer) >= 150:
    #        self._player.send_wave_points(self._wave_buffer[0:150])
    #        self._wave_buffer = self._wave_buffer[150:]
    #    elif len(self._wave_buffer) > 0:
    #        self._player.send_wave_points(self._wave_buffer)
    #        self._wave_buffer = []
    #    else:
    #        Clock.unschedule(self._send_wavepoints_to_remote_player)
                    
                    
    #def _generate_track_waveform(self):
    #    self._wave_buffer = []
    #    #self._waveform_generator.start_generator_thread(self._track.location)
    #    #self._waveform_generator = WaveformGenerator(self._track.location, 35000)
    #    #self._waveform_generator.set_data_point_callback(self._new_wave_point)
    #    #self._waveform_generator.set_process_done_callback(self._update_track_waveform)

    #@mainthread
    #def _new_wave_point(self, total_time, timestamp, value):
    #    #global buffer
    #    print total_time, timestamp, value
    #    self.seekbar.waveform.x_max = total_time
    #    self._wave_buffer.append((timestamp, value))
    #    if len(self._wave_buffer) >= 200:
    #        self.seekbar.waveform.points.extend(self._wave_buffer[0:200])
    #        try:
    #            self._player.send_wave_points(self._wave_buffer[0:200])
    #        except AttributeError:
    #            pass
    #            
    #        #send_points =  json.dumps(self._wave_buffer)
    #        self._wave_buffer = self._wave_buffer[200:]
    #        #self._player.send_command("WAVE_POINTS", send_points)

    #@mainthread
    #def _update_track_waveform(self, points):
    #    self.seekbar.waveform.points = points
    #    #print 'SETTING WAVEFORM'
        
    #    self._track.metadata.waveform = points
    #    #print self._track.metadata._metadata['waveform']
    #    # points
    #    #print self._track.metadata.waveform

    def _update(self, *a):
    #    if self.player is not None:
        #if self.track_duration is None:
        self.track_duration = self._player.length
            #if self._duration is not None:
            #    self.seekbar.max_value      = self._duration
            #    self.seekbar.waveform.x_max = self._duration
            #else:
            #    self.seekbar.max_value = 1
        position = self._player.position or 0
        duration = self.track_duration
        #print position, duration
        if duration is not None:
            #self.time_remaining_label.text = ""
            #self.show_force_skip = True
        #else:
            #if (duration - position) <= 16 * 1000000000:
            #    self.show_force_skip = True
            #else:
            #    if position > 1000000000:
            #        self.show_force_skip = False
            self.track_position = min(position, duration)
            #self.time_remaining_label.text = "-"+seconds_to_human_readable((duration - position) / 1000000000)
            #self.seekbar.value = position



#Builder.load_string(kv_string)
#Factory.register('MainPlayerDeck', MainPlayerDeck)


buffer = []
if __name__ == '__main__':
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
    Window.size = (1448, 350)
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
    
    bar = MainPlayerDeck()#Builder.load_string(kv_string)#FilesScreen(size_hint = (1,1))#size = (450,550))
    tra = load_file("/Users/jihemme/Python/DJ/Algiers Hoodooo Woman - Dr. Michael White (Dancing in the Sky) .mp3")
    bar.set_track(tra)
    bar.play()
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
    bar.unload()
