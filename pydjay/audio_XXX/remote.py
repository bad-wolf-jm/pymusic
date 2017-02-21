import os
import gi
import pprint
import sys
import urllib
import socket
import threading
import json
import socket
import time

gi.require_version("Gst", "1.0")
from gi.repository import Gst, GObject, GLib
from kivy.clock import mainthread, Clock

from kivy.event import EventDispatcher
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from pydjay.utils.protocol import ControlServer
from pydjay.utils.protocol import ControlClient
#install_gobject_iteration()

from kivy.logger import Logger

class SlavePlayer(EventDispatcher):
    is_connected    = BooleanProperty(False)
    is_connected_to = StringProperty(None, allownone = True)
    
    def __init__(self, host_ip, port):


        self._control_client = ControlClient(ip_address = host_ip, port = port, command_listener = self)
        self._control_client.bind(is_connected = self.set_is_connected,
                                  is_connected_to = self.set_is_connected_to)

        
        self._host         = host_ip
        self._port         = port
        self._file_port    = None
        self._connected_ip = None
        #self._name = name
        #self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self._sock.settimeout(1)

        self._current_path = None
        self._current_uri = None
        self._is_playing = False
        self._is_paused = False
        #self._shutdown = False

        self._length = None
        self._position = None
        self._run_position_update = True
        self._pipeline_state = None
       # self._connect_thread = None
        self._eos_callback = None


        self._uploading = False
        self._upload_complete_callback = None
        self._uploading_thread = None
        

    def connect(self, abort = None):
        self._control_client.connect(abort)

    def disconnect(self, abort = None):
        self.stop()
        self._control_client.disconnect()

        
    @mainthread
    def set_is_connected(self, foo, value):
        self.is_connected = value

    @mainthread
    def set_is_connected_to(self, foo, value):
        self.is_connected_to = value

    @mainthread
    def handle_TIME(self, pos, dur):
        self._position = int(pos)
        try:
            self._length = int(dur)
        except:
            self._length = None

        #print self._position, self._length

    @mainthread
    def handle_EOS(self):
        self._on_eos(None)


    #@@mainthread
    #@def handle_UPLOAD_COMPLETED(self, filename, time_):
    #    filename = filename.decode('utf-8') #json.loads(filename)
    #    Logger.info("RemotePlayer: Upload of '%s' reported as finished by %s after %s seconds", filename, self._connected_ip, time_)
    #    #print filename, self._uploading_track.location, type(filename), type(self._uploading_track.location)
    #    if filename == self._uploading_track.location.decode('utf-8'):
    #        Logger.info("RemotePlayer: Adding track data for '%s' to the remote database", self._uploading_track )
    #        t = time.time()
    #        track_data = {}
    #        track_data['location'] = self._uploading_track.location
    #        track_data['title']    = self._uploading_track.metadata.title
    #        track_data['artist']   = self._uploading_track.metadata.artist
    #        track_data['cover']    = None
    #        #track_data['waveform'] = self._uploading_track.metadata.waveform
    #        if self._uploading_track.metadata.album_cover is not None:
    #            #Logger.info("RemotePlayer: Uploading file '%s'", self._uploading_track.metadata.album_cover['original'])
    #            #self._upload_file(self._uploading_track.metadata.album_cover['original'])
    #            track_data['cover'] = self._uploading_track.metadata.album_cover['original']
    #        self._control_client.send_command('ADD_TRACK', json.dumps(track_data))
    #        t2 = time.time()
    #        t = t2-2
    #        if self._uploading_track is not None and self._upload_complete_callback is not None:
    #            self._upload_complete_callback(float(time_)+t)

        
    @mainthread
    def handle_HOST(self, name, ip, files):
        self._connected_ip   = ip
        self._file_port      = int(files)
        self.is_connected_to = name
        Logger.info("RemotePlayer: Connected to host '%s' at '%s', file upload server at %s:%s",
                    self.is_connected_to,
                    self._connected_ip,
                    self._connected_ip,
                    self._file_port)
        #Logger.info("RemotePlayer: Connected to file host %s at '%s:%s'", self.is_connected_to, self._connected_ip, self._file_port)
          
    def set_eos_callback(self, cb):
        self._eos_callback = cb

    @property
    def is_playing(self):
        return (self._is_playing) # pipeline_state == Gst.State.PLAYING)

    @property
    def is_paused(self):
        return (self._is_paused) #(self._pipeline_state == Gst.State.PAUSED)

    @property
    def length(self):
        return self._length


    #def _upload_file(self, filename):
    #    #Logger.info('RemotePlayer: Uploading %s to the re', filename)
    #    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #    sock.connect((self._connected_ip, self._file_port))
    #    sock.sendall(urllib.quote(filename,"") + '\n')
    #    f = open(filename, 'rb')
    #    data = f.read(4096)
    #    while data != '' and self._uploading:
    #        #print 'read', len(data)
    #        sock.sendall(data)
    #        data = f.read(4096)
    #    #self._uploading = False
    #    f.close()
    #    sock.close()
    #    Logger.info('RemotePlayer: Done uploading %s', filename)

    #def _upload_track_process(self):
    #    if None not in [self._connected_ip, self._file_port]:
    #        #sock = socket.socket
    #        self._uploading = True
    #        track_data = {}
    #        Logger.info("RemotePlayer: Uploading file '%s'", self._uploading_track.location)
    #        self._upload_file(self._uploading_track.location)
    #        if self._uploading_track.metadata.album_cover is not None:
    #            Logger.info("RemotePlayer: Uploading file '%s'", self._uploading_track.metadata.album_cover['original'])
    #            self._upload_file(self._uploading_track.metadata.album_cover['original'])
    #            #track_data['cover'] = self._uploading_track.metadata.album_cover['original']
    #        #if self._upload_complete_callback is not None:
    #        #    self._upload_complete_callback()
                
    #def _cancel_upload(self):
    #    Logger.info("RemotePlayer: Cancelled upload of '%s' to the remote database", self._uploading_track)
    #    self._uploading = False
    #    self._uploading_thread.join()
    #    self._uploading_thread = None
    #    self._uploading_track = None
    #    self._upload_complete_callback = None
     #   
     #   pass
    
    #d#ef upload_track(self, track, on_process_complete):
     #   if self._uploading:
     #       self._cancel_upload()
    #    self._uploading_track = track
    #    self._upload_complete_callback = on_process_complete
    #    self._uploading_thread = threading.Thread(target = self._upload_track_process)
    #    self._uploading_thread.start()
    #    Logger.info("RemotePlayer: Uploading '%s' to the remote database", self._uploading_track)

        
    #def set_volume(self, value):
    #    self._control_client.send_command('SET_VOLUME', str(value))
    #    #self.player.set_property('volume', value)
            
    #@property
    def get_position(self):
        return self._position

    def set_position(self, pos):
        #if self.is_playing or self.is_paused:
        self._control_client.send_command('SEEK', str(pos))
#
#            self.playbin.seek_simple(Gst.Format.TIME,
#                                     Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT,
#                                     pos * Gst.MSECOND)
    position = property(get_position, set_position)

    
    def _on_eos(self, message):
        self._is_playing   = False
        self._current_uri  = None
        self._current_path = None
        self._length = None
        #self.player.set_state(Gst.State.NULL)
        if self._eos_callback is not None:
            self._eos_callback()
            
    def _on_error(self, message):
        self._is_playing   = False
        self._current_uri  = None
        self._current_path = None
        self._length = None
        self.player.set_state(Gst.State.NULL)
        print message.parse_error()


    def shutdown(self):
        self._control_client.shutdown()
                    
    def load_path(self, path, auto_start = False):
        self._is_playing = False
        self.stop()
        if os.path.isfile(path):
            filepath = os.path.realpath(path)
            self._current_path = path
            self._current_uri  = None
            if auto_start:
                self.start_decoder()
        else:
            self._current_path = None
            self._current_uri  = None
            print path, "is not a file"

    def send_wave_points(self, points):
        send_points =  json.dumps(points)
        self._control_client.send_command("WAVE_POINTS", send_points)
            
    def start_decoder(self):
        self._length   = None
        self._position = None
        if self._current_path is not None:
            if not self._is_playing:
                self._control_client.send_command('PLAY', json.dumps(self._current_path))
                print "FOO"
                self._is_playing = True

    def pause(self):
        if self.is_playing:
            ret = self.player.set_state(Gst.State.PAUSED)
            if ret == Gst.StateChangeReturn.FAILURE:
                print("ERROR: Unable to set the pipeline to the playing state")
            else:
                print("Aable to set the pipeline to the playing state")
                self._is_playing = False

    def stop(self):
        if self.is_playing and self._control_client is not None:
            self._control_client.send_command('STOP')
        self._is_playing = False
        self._length = None

    def get_volume(self, volume):
        self._control_client.send_command("GET_VOLUME")
        #self.player.get_property('volume')
    def set_volume(self, volume):
        self._control_client.send_command("SET_VOLUME", str(volume))
        #self.player.set_property('volume', volume)
    volume = property(get_volume, set_volume)
            

if __name__ == "__main__":
    Gst.init(None)     
    GObject.threads_init()

    foo = AudioDecoder()
    foo.load_path("/Users/jihemme/Python/DJ/pydjay/audio/test.mp4")
    foo.start_decoder()
    loop = GLib.MainLoop()
    loop.run()

#%msg = bus.timed_pop_filtered(Gst.CLOCK_TIME_NONE,Gst.MessageType.ERROR | Gst.MessageType.EOS)
#%print msg.parse_error()
#sys.exit(1)

 
# Free resources.
#foo.player.set_state(Gst.State.NULL)
