import os
import gi
import pprint
import sys
import urllib
gi.require_version("Gst", "1.0")
    
#gi.require_version('Gtk', '3.0')
from gi.repository import Gst, GObject, GLib
#import sounddevice
import platform



from kivy.support import install_gobject_iteration

try:
    from pydjay.audio import decoder
except:
    import decoder
#install_gobject_iteration()

Gst.init(None)     
GObject.threads_init()

_sinks = {'Windows': 'directsoundsink',
          'Darwin':  'osxaudiosink'}

class AudioDecoder(object):
    def __init__(self):
        object.__init__(self)
        self.player     = Gst.ElementFactory.make("playbin", "decoder")
        #self.audio_sink = Gst.ElementFactory.make('jackaudiosink', "audio_sink")
        self.audio_sink = Gst.ElementFactory.make(_sinks[platform.system()], "audio_sink")
        self.video_sink = Gst.ElementFactory.make("fakesink", "video_sink")
        #self.audio_sink.set_property('client-name', "PYDJAY")
        #self.audio_sink.set_property('connect', "none")
        self.player.set_property('video-sink', self.video_sink)
        self.player.set_property('audio-sink', self.audio_sink)
        #print "SOUND CARD", self.audio_sink.get_property('device')
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)


        self._current_path = None
        self._current_uri = None
        self._is_playing = False

        self._length = None
        self._position = None
        self._run_position_update = True
        self._pipeline_state = None

        self._eos_callback = None
        self.thread = decoder.get_loop_thread()
        #gobject.timeout_add(43, self._update_position)
        

        self._message_handlers = {
            Gst.MessageType.UNKNOWN:   None,
            Gst.MessageType.EOS:       self._on_eos,
            Gst.MessageType.ERROR:     self._on_error,
            Gst.MessageType.WARNING:   None,
            Gst.MessageType.INFO:      None,
            Gst.MessageType.TAG:       None,
            Gst.MessageType.BUFFERING:     None,
            Gst.MessageType.STATE_CHANGED: self._on_state_changed,
            Gst.MessageType.STATE_DIRTY:   None,
            Gst.MessageType.STEP_DONE:     None,
            Gst.MessageType.CLOCK_PROVIDE: None,
            Gst.MessageType.CLOCK_LOST:    None,
            Gst.MessageType.NEW_CLOCK:     None,
            Gst.MessageType.STRUCTURE_CHANGE: None,
            Gst.MessageType.STREAM_STATUS:    None,
            Gst.MessageType.APPLICATION:      None,
            Gst.MessageType.ELEMENT:          None,
            Gst.MessageType.SEGMENT_START:    None,
            Gst.MessageType.SEGMENT_DONE:     None,
            Gst.MessageType.DURATION_CHANGED: self._on_duration_changed,
            Gst.MessageType.LATENCY:          None, #self._on_latency,
            Gst.MessageType.ASYNC_START:      None,
            Gst.MessageType.ASYNC_DONE:       None,
            Gst.MessageType.REQUEST_STATE:    None,
            Gst.MessageType.STEP_START:       None,
            Gst.MessageType.QOS:              None,
            Gst.MessageType.PROGRESS:         self._on_progress,
            Gst.MessageType.TOC:              None,
            Gst.MessageType.RESET_TIME:       None,
            Gst.MessageType.STREAM_START:     None,
            Gst.MessageType.NEED_CONTEXT:     None,
            Gst.MessageType.HAVE_CONTEXT:     None,
            Gst.MessageType.EXTENDED:         None,
            Gst.MessageType.DEVICE_ADDED:     None,
            Gst.MessageType.DEVICE_REMOVED:   None,
            #Gst.MessageType.PROPERTY_NOTIFY:None,
            #Gst.MessageType.STREAM_COLLECTION:None,
            #Gst.MessageType.STREAMS_SELECTED:None,
            #Gst.MessageType.REDIRECT:None,
            
            }

    #def set_decoder_target(self, sink_element):
    #    print sink_element
    #    self.audio_sink = sink_element
    #    self.player.set_property('audio-sink', self.audio_sink)
    def set_eos_callback(self, cb):
        self._eos_callback = cb

    def _on_progress(self, *args):
        pass#print args


    def _on_latency(self, *args):
        pass#print args


        
    def _on_state_changed(self, message):
        old, new, pending = message.parse_state_changed()
        #print old, new, pending
        self._pipeline_state = new


    @property
    def is_playing(self):
        return self._is_playing #(self._pipeline_state == Gst.State.PLAYING)

    @property
    def is_paused(self):
        return (self._pipeline_state == Gst.State.PAUSED)

        
    def _on_duration_changed(self, message):
        #print message.parse_duration()
        success, value = self.player.query_duration(Gst.Format.TIME)
        if success and value > 0:
            self._length = value
            #print "LENGTH::", value
        else:
            self._length = None

    @property
    def length(self):
        return self._length
            #print "LENGTH", self._length

    def set_volume(self, value):
        self.player.set_property('volume', value)
            
    #@property
    def get_position(self):
        if self.is_playing:
            success, value = self.player.query_position(Gst.Format.TIME)
            if success:
                #print "POS:", value
                return value
            else:
                return None
        else:
            return None
    def set_position(self, pos):
        #print 'seekinf', pos
        if self.is_playing or self.is_paused:
            self.player.seek_simple(Gst.Format.TIME,
                                    Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT,
                                    pos)
    position = property(get_position, set_position)

    
    def _on_eos(self, message):
        self._is_playing   = False
        self._current_uri  = None
        self._current_path = None
        self.player.set_state(Gst.State.NULL)
        if self._eos_callback is not None:
            self._eos_callback()
            
    def _on_error(self, message):
        self._is_playing   = False
        self._current_uri  = None
        self._current_path = None
        self.player.set_state(Gst.State.NULL)
        print message.parse_error()

    #def _update_position(self):
    #    if self._length is None:
    #        success, value = self.player.query_duration(Gst.Format.TIME)
    #        if success and value > 0:
    #            self._length = value
    #    success, value = self.player.query_position(Gst.Format.TIME)
    #    if success:
    #        self._position = value
    #    else:
    #        self._position = None
            
    #    #print self._length, self._position
    #    return self._is_playing

    def send_wave_points(self, points):
        pass
    
    
    def load_path(self, path, auto_start = False):
        self.player.set_state(Gst.State.NULL)
        self._is_playing = False
        if os.path.isfile(path):
            filepath = os.path.realpath(path)
            #self.player.set_state(Gst.State.NULL)
            uri = 'file:' + urllib.pathname2url(path) #'file://' + path
            #print uri
            self._current_path = path
            self._current_uri  = uri
            self.player.set_property("uri", uri)
            if auto_start:
                self.start_decoder()
        else:
            self._current_path = None
            self._current_uri  = None
            print path, "is not a file"

    def start_decoder(self):
        self._length   = None
        self._position = None
        if self._current_uri is not None:
            if not self._is_playing:
                ret = self.player.set_state(Gst.State.PLAYING)
                if ret == Gst.StateChangeReturn.FAILURE:
                    print("ERROR: Unable to set the pipeline to the playing state")
                    self._is_playing = False
                else:
                    #print("Aable to set the pipeline to the playing state")
                    self._is_playing = True
                    #GObject.timeout_add(43, self._update_position)

    def pause(self):
        #self._length   = None
        #self._position = None
        #if self._current_uri is not None:
        if self.is_playing:
            ret = self.player.set_state(Gst.State.PAUSED)
            if ret == Gst.StateChangeReturn.FAILURE:
                print("ERROR: Unable to set the pipeline to the playing state")
                #self._is_playing = False
            else:
                #print("Aable to set the pipeline to the playing state")
                self._is_playing = False
                #GObject.timeout_add(43, self._update_position)

    def stop(self):
        #self._length   = None
        #self._position = None
        #if self._current_uri is not None:
        print "STOPPING PLAYER"
        if self.is_playing:
            ret = self.player.set_state(Gst.State.NULL)
            if ret == Gst.StateChangeReturn.FAILURE:
                print("ERROR: Unable to set the pipeline to the playing state")
                #self._is_playing = False
            else:
                #print("Aable to set the pipeline to the playing state")
                self._is_playing = False
                self._length = None
                #GObject.timeout_add(43, self._update_position)


    def get_volume(self, volume):
        self.player.get_property('volume')
    def set_volume(self, volume):
        self.player.set_property('volume', volume)
    volume = property(get_volume, set_volume)
            
    def on_message(self, bus, message):
        typ = message.type
        #print typ
        handler = self._message_handlers.get(typ, None)
        if handler is not None:
            handler(message)
            
        #print typ


#import wavegen
        

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
