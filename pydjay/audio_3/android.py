import os
#import gi
import pprint
import sys
import urllib
#gi.require_version("Gst", "1.0")
#gi.require_version('Gtk', '3.0')
#$from gi.repository import Gst, GObject, GLib
#import sounddevice


from kivy.logger import Logger
from kivy.support import install_gobject_iteration

from jnius import autoclass
from jnius import PythonJavaClass, java_method
#from time import sleep

# get the MediaPlayer java class
MediaPlayer = autoclass('android.media.MediaPlayer')
OnCompletionListener = autoclass('android.media.MediaPlayer$OnCompletionListener')

#install_gobject_iteration()

class PythonOnComplete(PythonJavaClass):                                     
     __javainterfaces__ = ['android/media/MediaPlayer$OnCompletionListener']  
     def __init__(self, decoder, *args, **kwargs):                          
         self.decoder = decoder                                                 
         super(PythonOnComplete, self).__init__(*args, **kwargs)              
#

     @java_method('(Landroid/media/MediaPlayer;)V')                           
     def onCompletion(self, mp):
         Logger.info("FOO: COMPLETION")
         self.decoder.onCompletion()                                                
         #print "[PYTHON_ON_COMPLETE]" + " termino el tema"   

class AudioDecoder:
    def __init__(self):
        self._current_path = None
        self._is_playing = False
        self._length = None
        self._position = None
        self._run_position_update = True
        self._pipeline_state = None
        self._eos_callback = None
        self._m_player = None
        self._on_eos = None

    def set_eos_callback(self, cb):
        self._eos_callback = cb

    def _on_progress(self, *args):
        pass#print args


    def _on_latency(self, *args):
        pass#print args


        
    def _on_state_changed(self, message):
        old, new, pending = message.parse_state_changed()
        #print new
        self._pipeline_state = new


    @property
    def is_playing(self):
        return self._is_playing #self._m_player is not None and self._m_player.isPlaying()
        #return (self._pipeline_state == Gst.State.PLAYING)

    @property
    def is_paused(self):
        return self._is_paused
        #return (self._pipeline_state == Gst.State.PAUSED)

        
    #def _on_duration_changed(self, message):
    #    #print message.parse_duration()
    #    success, value = self.player.query_duration(Gst.Format.TIME)
    #    if success and value > 0:
    #        self._length = value
    #        #print "LENGTH::", value
    #    else:
    #        self._length = None

    @property
    def length(self):
        if self._m_player is not None:
            return self._m_player.getDuration() * 1000000
        else:
            return None




    #@property
    def get_position(self):
        try:
            if self._m_player is not None:
                return self._m_player.getCurrentPosition() * 1000000
            else:
                return -1
        except:
            return -1
    def set_position(self, pos):
        pass
    position = property(get_position, set_position)

    
    def onCompletion(self, *message):
        self._is_playing   = False
        self._current_uri  = None
        self._current_path = None
        #self.player.set_state(Gst.State.NULL)
        if self._m_player is not None:
            self._m_player.release()
        self._m_player = None
        self._is_playing = False
        self._on_eos = None
        if self._eos_callback is not None:
            self._eos_callback()
            
    def _on_error(self, message):
        self._is_playing   = False
        self._current_uri  = None
        self._current_path = None
        #self.player.set_state(Gst.State.NULL)
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
        
    def load_path(self, path, auto_start = False):
        #self.player.set_state(Gst.State.NULL)
        self._is_playing = False
        self.stop()
        if os.path.isfile(path):
            filepath = os.path.abspath(path)
            #self.player.set_state(Gst.State.NULL)
            #uri = 'file://' + path
            #print uri
            self._current_path = filepath
            self._current_uri  = filepath
            
            self._m_player = MediaPlayer()
            self._m_player.setDataSource(self._current_uri)
            self._on_eos = PythonOnComplete(self)
            self._m_player.setOnCompletionListener(self._on_eos)
            self._m_player.prepare()
            self._is_playing = False
            #self._length = self._m_player.getDuration() * 1000000
            #self.player.set_property("uri", uri)
            if auto_start:
                self.start_decoder()
        else:
            self._current_path = None
            self._current_uri  = None
            print path, "is not a file"

    def start_decoder(self):
        #self._length   = None
        #self._position = None
        if self._m_player is not None:
            self._m_player.start()
            self._is_playing = True
        else:
            self._is_playing = False

            
        #$if self._current_uri is not None:
        #$    if not self._is_playing:
        #        ret = self.player.set_state(Gst.State.PLAYING)
        #        if ret == Gst.StateChangeReturn.FAILURE:
        #            print("ERROR: Unable to set the pipeline to the playing state")
        #            self._is_playing = False
        #        else:
        #            #print("Aable to set the pipeline to the playing state")
        #            self._is_playing = True
        #            #GObject.timeout_add(43, self._update_position)

    def pause(self):
        #self._length   = None
        #self._position = None
        #if self._current_uri is not None:
        if self._m_player is not None:
            self._m_player.pause()

        #if self.is_playing:
        #    ret = self.player.set_state(Gst.State.PAUSED)
        #    if ret == Gst.StateChangeReturn.FAILURE:
        #        print("ERROR: Unable to set the pipeline to the playing state")
        #        #self._is_playing = False
        #    else:
        #        #print("Aable to set the pipeline to the playing state")
        #        self._is_playing = False
        #        #GObject.timeout_add(43, self._update_position)

    def stop(self):
        #self._length   = None
        #self._position = None
        #if self._current_uri is not None:
        if self._m_player is not None:
            #try:
            self._m_player.stop()
            #except:
            #    pass
            self._m_player.release()
            self._m_player = None
            self._is_playing = False
            #self._on_eos = None

            
        #if self.is_playing:
        #    ret = self.player.set_state(Gst.State.READY)
        #    if ret == Gst.StateChangeReturn.FAILURE:
        #        print("ERROR: Unable to set the pipeline to the playing state")
        #        #self._is_playing = False
        #    else:
        #        #print("Aable to set the pipeline to the playing state")
        #        self._is_playing = False
        #        #GObject.timeout_add(43, self._update_position)


    def get_volume(self, volume):
        return self.player.get_property('volume')
    def set_volume(self, volume):
        self.player.set_property('volume', volume)
    volume = property(get_volume, set_volume)
            
    #def on_message(self, bus, message):
    #    typ = message.type
    #    #print typ
    #    handler = self._message_handlers.get(typ, None)
    #    if handler is not None:
    #        handler(message)
    #        
    #    #print typ


#import wavegen
        

if __name__ == "__main__":
    #Gst.init(None)     
    #GObject.threads_init()

    #foo = AudioDecoder()
    #foo.load_path("/Users/jihemme/Python/DJ/pydjay/audio/test.mp4")
    #foo.start_decoder()
    #loop = GLib.MainLoop()
    #loop.run()


    from jnius import autoclass
    from time import sleep

    # get the MediaPlayer java class
    MediaPlayer = autoclass('android.media.MediaPlayer')

    # create our player
    mPlayer = MediaPlayer()
    mPlayer.setDataSource('/sdcard/testrecorder.3gp')
    mPlayer.prepare()

    #play
    print 'duration:', mPlayer.getDuration()
    mPlayer.start()
    print 'current position:', mPlayer.getCurrentPosition()
    sleep(5)
    
    # then after the play:
    mPlayer.release()

#%msg = bus.timed_pop_filtered(Gst.CLOCK_TIME_NONE,Gst.MessageType.ERROR | Gst.MessageType.EOS)
#%print msg.parse_error()
#sys.exit(1)

 
# Free resources.
#foo.player.set_state(Gst.State.NULL)
