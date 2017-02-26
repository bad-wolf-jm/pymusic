import os
import threading
#import time
#import sys
#from os.path import getsize
#from datetime import datetime
from decoder import GstAudioFile
from output_jack import JackOutput

from kivy.properties import StringProperty, NumericProperty, AliasProperty
from kivy.event import EventDispatcher
from kivy.clock import mainthread, Clock

from multiprocessing import Process, Queue

try:
    import queue
except ImportError:
    import Queue as queue

class AudioPlayer(EventDispatcher):
    state                = StringProperty(None, allownone = True)
    track_duration       = NumericProperty(None, allownone = True)
    track_position       = NumericProperty(None, allownone = True)
#(Process):
    def __init__(self, player_name, num_channels = 2, in_queue = None, out_queue = None, *args, **kw):
        super(AudioPlayer, self).__init__(*args, **kw)
        self._track_promise = None
        self._current_time  = None
        self.player_name = player_name
        self.num_channels = num_channels
        self._is_playing    = False
        self._player_thread = None
        self._decoder       = None
        self._tr_time = None
        self._tr_dur  = None
        self._state   = 'stopped'
        self._eos_callbacks = []
        self._output        = JackOutput(self.player_name, self.num_channels)

        self.state = None
        self.track_duration = None
        self.track_position = None
        self.in_queue  = in_queue
        self.out_queue = out_queue
        self.register_event_type("on_end_of_stream")

        
    def on_end_of_stream(self, *args):
       pass


    def _get_remaining_time(self, *a):
        if self.track_duration is not None and self.track_position is not None:
            return self.track_duration - self.track_position
        return 0

    remaining_time  = AliasProperty(_get_remaining_time, bind = ['track_duration', 'track_position'])
   
    def connect_outputs(self, **kwargs):
        self._output.connect_outputs(**kwargs)

    def disconnect_outputs(self, **kwargs):
        self._output.disconnect_outputs(**kwargs)

    def _player_loop(self):
        eos = False
        #if self._decoder is not None:
        has_duration = False
        iteration = 0
        while self._is_playing:
            #if self.state == 'paused':

            try:
                timestamp, samples = self._decoder.next()
                if self._decoder.duration is not None and not has_duration:
                    has_duration = True
                    self.track_duration = self._decoder.duration
                    #self.out_queue.put(('signal_stream_duration', (self._decoder.duration,), {}))
                if iteration == 20:
                    self.track_position = self._output.stream_time
                    iteration = 0
                else:
                    iteration += 1
                    #self.out_queue.put(('signal_stream_time', (self._output.stream_time,), {}))
                self._output.send(samples)
            except StopIteration:
                eos = True
                break
        self._decoder.close()
        self._is_playing = False
        self._player_thread = None
        if eos:
            self.dispatch('on_end_of_stream')
            #self.out_queue.put(('signal_end_of_stream', (), {}))

    def play(self, filename, start_time = None, end_time = None):
        self.stop()
        self._file          = filename
        self._decoder       = GstAudioFile(self._file, self._output.num_channels, self._output.samplerate, 'F32LE', None, start_time, end_time)
        if start_time is not None:
            self._decoder.seek(start_time)
            self._output.reset_timer(start_time)
        else:
            self._output.reset_timer(0)
        self._player_thread = threading.Thread(target = self._player_loop)
        self._is_playing    = True
        self._player_thread.start()
        self.state = "playing"

    def stop(self):
        self._is_playing = False
        self._output.flush_buffer()
        self._output.reset_timer()
        if self._player_thread is not None:
            self._player_thread.join()
        self._player_thread = None
        self._decoder       = None
        self.track_duration = None
        self.track_position = None
        self.state          = "stopped"
        
    def pause(self):
        self.state = "paused"

    def seek(self, timestamp):
        if self._decoder is not None:
            self._decoder.seek(timestamp)
            self._output.reset_timer(timestamp)

    def seek_relative(self, time):
        if self._is_playing:
            p = self.track_position
            if p is not None:
                d = self.track_duration
                if d is not None:
                    p += time
                    p = max(min(p, d), 0)
                    self.seek(p)

    @property
    def is_playing(self):
        return self.state == 'playing'

    #def shutdown(self):
    def shutdown(self):
        #self.out_queue.put(('close', (), {}))
        #self.out_queue.cancel_join_thread()
        #self.in_queue.cancel_join_thread()
        #self._running = False
        #self._foo.join()
        pass

    def run(self):
        self._output        = JackOutput(self.player_name, self.num_channels)
        self.out_queue.put(('_init', (), {}))
        while True: 
            try:
                command, args, kwargs = self.in_queue.get_nowait()
                if command == 'close':
                    print "CLOSING player:", self.player_name
                    self.stop()
                    self._output.close()
                    print "shutting down player::", self.player_name
                    break
                try:
                    getattr(self, command)(*args, **kwargs)
                except AttributeError, details:
                    pass 
                except Exception, details:
                    print 'y', details
                    break
            except queue.Empty, details:
                pass
        print "Closing Queue"
        
class AudioPlayer_XXX(EventDispatcher):
    state                = StringProperty(None, allownone = True)
    track_duration       = NumericProperty(None, allownone = True)
    track_position       = NumericProperty(None, allownone = True)

    def __init__(self, player_name, num_channels = 2, *args, **kw):
        super(AudioPlayer, self).__init__(*args, **kw)

        self.out_queue  = Queue(maxsize = 10)
        self.in_queue   = Queue(maxsize = 1000)
        self.ready_sem = threading.Semaphore(0)
        self._output_process = AudioPlayerDriver(player_name, num_channels,
                                                 self.out_queue, self.in_queue)
        self._output_process.start()
        self._running = True
        self._foo = threading.Thread(target = self._print_info)
        self._foo.start()
        self.stream_time = 0
        self.ready_sem.acquire()



        
        self.register_event_type("on_end_of_stream")
        self._current_time  = None
        self.player_name = player_name
        self._is_playing    = False
        self._player_thread = None
        self._decoder       = None
        self._tr_time = None
        self._tr_dur  = None
        self.stream_time = 0

        self._state   = 'stopped'
        self._eos_callbacks = []


    def _init(self):
        self.ready_sem.release()
        
    def on_end_of_stream(self, *args):
       pass

    def connect_outputs(self, **kwargs):
        self.out_queue.put(('connect_outputs', (), kwargs))

    def disconnect_outputs(self, **kwargs):
        self.out_queue.put(('disconnect_outputs', (), kwargs))

    def _get_remaining_time(self, *a):
        if self.track_duration is not None and self.track_position is not None:
            return self.track_duration - self.track_position
        return 0

    remaining_time  = AliasProperty(_get_remaining_time, bind = ['track_duration', 'track_position'])

    def _print_info(self):
        while self._running:
            try:
                command, args, kwargs = self.in_queue.get_nowait()
                if command == 'QUIT':
                    
                    break
                try:
                    #print command, args, kwargs
                    getattr(self, command)(*args, **kwargs)
                    #time.sleep(.1)
                except AttributeError, details:
                    print details
                    pass 
                except Exception, details:
                    print 'y', details
            except queue.Empty, details:
                pass
            finally:
                pass
        
    @mainthread
    def signal_stream_time(self, timestamp):
        self.track_position = timestamp

    @mainthread
    def signal_stream_duration(self, time):
        self.track_duration = time

    @mainthread
    def signal_end_of_stream(self):
        self.dispatch('on_end_of_stream')


    def play(self, filename, start_time = None, end_time = None):
        self.out_queue.put(('play', (filename, start_time , end_time), {}))
        self.state = "playing"

    def stop(self):
        self.out_queue.put(('stop', (), {}))
        self.track_duration = None
        self.track_position = None
        self.state          = "stopped"
        
    def pause(self):
        self.state = "paused"

    def seek(self, timestamp):
        self.out_queue.put(('seek', (timestamp,), {}))

    def seek_relative(self, time):
        self.out_queue.put(('seek_relative', (time,), {}))

    @property
    def is_playing(self):
        return self.state == 'playing'

    def shutdown(self):
        self.out_queue.put(('close', (), {}))
        self.out_queue.cancel_join_thread()
        self.in_queue.cancel_join_thread()
        self._running = False
        self._foo.join()

    
#buffer = []
#if __name__ == '__main__':#
#
#    path = os.path.abspath(os.path.expanduser(sys.argv[1]))
#    player = AudioPlayer("TestPlayer", 2)
#    player.connect_outputs(output_1 = "system:playback_1",
#                           output_2 = "system:playback_2")
#    player.play(path)
#    #time.sleep(45)
#    #player.stop()
