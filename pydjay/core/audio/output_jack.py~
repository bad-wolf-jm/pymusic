# This file is part of audioread.
# Copyright 2011, Adrian Sampson.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

"""Use Gstreamer to decode audio files.
To read an audio file, pass it to the constructor for GstAudioFile()
and then iterate over the contents:
    >>> f = GstAudioFile('something.mp3')
    >>> try:
    >>>     for block in f:
    >>>         ...
    >>> finally:
    >>>     f.close()
Note that there are a few complications caused by Gstreamer's
asynchronous architecture. This module spawns its own Gobject main-
loop thread; I'm not sure how that will interact with other main
loops if your program has them. Also, in order to stop the thread
and terminate your program normally, you need to call the close()
method on every GstAudioFile you create. Conveniently, the file can be
used as a context manager to make this simpler:
    >>> with GstAudioFile('something.mp3') as f:
    >>>     for block in f:
    >>>         ...
Iterating a GstAudioFile yields strings containing short integer PCM
data. You can also read the sample rate and channel count from the
file:
    >>> with GstAudioFile('something.mp3') as f:
    >>>     print f.samplerate
    >>>     print f.channels
    >>>     print f.duration
"""
from __future__ import with_statement
from __future__ import division

#import gi
#gi.require_version('Gst', '1.0')
#from gi.repository import GLib, Gst

import sys
import threading
import os
import traceback
import jack
import time
import array
from multiprocessing import Process, Queue

#from . import DecodeError
#from kivy.utils import platform

from decoder import get_loop_thread, GstAudioFile
try:
    import queue
except ImportError:
    import Queue as queue

#try:
#    from urllib.parse import quote
#except ImportError:
#    from urllib import quote
#import multiprocessing, logging
#logger = multiprocessing.log_to_stderr()
#logger.setLevel(logging.DEBUG)
#logger.warning('doomed')

QUEUE_SIZE = 100
BUFFER_SIZE = 100

class JackOutputDriver(object):
    def __init__(self, client_name = "PYDjayJackClient", num_channels = 2):
        self.num_channels = num_channels
        self.client_name  = client_name

        self._jack_client   = jack.Client(client_name)
        self.client_name    = self._jack_client.name
        self.samplerate     = self._jack_client.samplerate
        self.block_size     = self._jack_client.blocksize
        self._output_ports  = []
        self._outputs       = {}
        self._input_buffers = [] #array.array('f')
        self.stream_time    = 0
        self.closed          = False

        self._buffer_time   = int(self.block_size * 1.0 / self.samplerate * 1000000000)
 
    
        for i in range(num_channels):
            port_name = "output_%s"%(i+1)
            self._output_ports.append(self._jack_client.outports.register(port_name))
            self._outputs[port_name] = self._output_ports[i]
            self._input_buffers.append(array.array('f'))
        self.queue = queue.Queue(256)

        self._left_over = None

        self._buffer_not_full = threading.Lock() 
        self._max_buffer_size = self.block_size * 30
        self._buffer_size     = 0
        #for i in range(self.num_channels):
            
        
        self._jack_client.set_process_callback(self._process)
        self._jack_client.set_blocksize_callback(self._blocksize_changed)
        self._jack_client.set_shutdown_callback(self._on_server_shutdown)
        self._jack_client.activate()


    def connect_outputs(self, **kwargs):
        for key in kwargs:
            port = self._outputs[key]
            self._jack_client.connect(port, kwargs[key])
        

    def disconnect_outputs(self, **kwargs):
        for key in kwargs:
            port = self._outputs[key]
            self._jack_client.disconnect(port, kwargs[key])
    
    def flush_buffer(self):
        pass

    def reset_timer(self, timestamp = 0):
        self.stream_time = timestamp

    def _process(self, length):
        #print self.client_name, 'xxx', length, self._buffer_size
        set_time = False
        for channel_index in range(self.num_channels):
            foo = self._output_ports[channel_index].get_array()
            foo.fill(0)
            if self._buffer_size >= length:
                set_time = True
                try:
                    foo[:] = self._input_buffers[channel_index][:length]
                    self._input_buffers[channel_index] = self._input_buffers[channel_index][length:]
                except ValueError:
                    pass
            #else:
            #    print self.client_name, 'underrun'
        if set_time:
            self.stream_time += self._buffer_time
        self._buffer_size -= length
        self._buffer_size = max(self._buffer_size, 0)
        if self._buffer_size < self._max_buffer_size:
            waiting_for_space = not self._buffer_not_full.acquire(False)
            if waiting_for_space:
                self._buffer_not_full.release()

    def _blocksize_changed(self, block_size):
        self.block_size = block_size
        self._max_buffer_size = self.block_size * 30
        
    def _on_server_shutdown(self, *a):
        pass
    
    def close(self):
        self._jack_client.deactivate()
        self._jack_client.close()
        self.closed = True
        
    def send(self, data):
        #print self.client_name, 'send', len(data)
        if self._buffer_size >= self._max_buffer_size:
            self._buffer_not_full.acquire()
        #data = data[1]
        for offset in range(0, len(data), self.num_channels):
            for channel_index in range(self.num_channels):
                self._input_buffers[channel_index].append(data[offset+channel_index])
        self._buffer_size += int(len(data) / 2)



class JackOutputProcess(Process):
    def __init__(self, name = "", num_channels = 2, in_queue = None, out_queue = None):
        super(JackOutputProcess, self).__init__()
        self.in_queue  = in_queue
        self.out_queue = out_queue
        #self.position = position
        #self.duration = duration
        #self.state    = state
        #self.eos      = eos
        self.client_name  = name
        self.num_channels = num_channels
        self.player    = None #AP(name, num_channels)

    def run(self):
        #def _end_of_stream():
        #    self.eos.value = 1
        self.output_driver    = JackOutputDriver(self.client_name, self.num_channels)
        self.out_queue.put(('_init', (), {"client_name":  self.output_driver.client_name,
                                          "block_size":   self.output_driver.block_size,
                                          "samplerate":   self.output_driver.samplerate,
                                          "num_channels": self.output_driver.num_channels}))
        while True: #not self.output_driver.closed:
            #print "xxx"
            try:
                command, args, kwargs = self.in_queue.get_nowait()
                if command == 'close':
                    print "CLOSING:", self.client_name
                    #self.output_driver.close()
                    #print threading.enumerate()
                    #self.terminate()
                    break
                try:
                    getattr(self.output_driver, command)(*args, **kwargs)
                    #time.sleep(.01)
                except AttributeError, details:
                    pass 
                except Exception, details:
                    print 'y', details
            except queue.Empty, details:
                pass
            self.out_queue.put(('set_stream_time', (self.output_driver.stream_time,), {}))
        #print "Closing Queue"
        #self.out_queue.close()
        #print threading.enumerate()

class JackOutput(object):
    def __init__(self, client_name = "PYDjayJackClient", num_channels = 2, *args, **kw):
        super(JackOutput, self).__init__()
        self.out_queue  = Queue(maxsize = 10)
        self.in_queue   = Queue(maxsize = 100)
        self.ready_sem = threading.Semaphore(0)
        self._output_process = JackOutputProcess(client_name, num_channels,
                                                 self.out_queue, self.in_queue)
      #                                           self._position, self._duration)
        #self._state, self._eos)
        self._output_process.daemon = True
        self._output_process.start()
        self._running = True
        self._foo = threading.Thread(target = self._print_info)
        self._foo.start()
        self.stream_time = 0
        self.ready_sem.acquire()
    

    def _init(self, block_size = 0, samplerate = 0, client_name = "", num_channels = 0):
        self.block_size   = block_size
        self.samplerate   = samplerate
        self.client_name  = client_name
        self.num_channels = num_channels
        self.ready_sem.release()

    def _print_info(self):
        while self._running:
            try:
                command, args, kwargs = self.in_queue.get_nowait()
                if command == 'QUIT':
                    break
                try:
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
 
    def connect_outputs(self, **kwargs):
        self.out_queue.put(('connect_outputs', (), kwargs))

    def disconnect_outputs(self, **kwargs):
        self.out_queue.put(('disconnect_outputs', (), kwargs))

    def flush_buffer(self):
        pass

    def reset_timer(self, timestamp = 0):
        self.out_queue.put(('reset_timer', (), {'timestamp': timestamp}))

    def set_stream_time(self, time):
        self.stream_time = time
        
    def send(self, data):
        #print 'sending'
        self.out_queue.put(('send', (data,), {}))
        
    def close(self):
        self.out_queue.put(('close', (), {}))
        #self.out_queue.cancel_join_thread()
        #self.out_queue.close()
        #self.in_queue.close()
        self._running = False
        self._foo.join()
        #self._jack_client.deactivate()
        #self._jack_client.close()
        
# Smoke test.
if __name__ == '__main__':
    
    #for path in sys.argv[1:]:
    path = os.path.abspath(os.path.expanduser(sys.argv[1]))
    #for f in os.listdir(path):
    #    pp = os.path.join(path, f)
    #    p, ext = os.path.splitext(pp)
    #    if ext in ['.mp3', '.mp4']:
    foo = JackOutput()

    print foo.client_name
    print foo.block_size
    print foo.samplerate
    #time.sleep(5)
    try:
        
        with GstAudioFile(path) as decoded:
            #print pp
            #out = GstOutput()
            #print decoded.channels, decoded.samplerate,
            #print(decoded.duration)
            i = 0
            for s in decoded:
                #if decoded.duration is not None:
                #    print decoded.duration
                    #break
                i += 1
                #print s[0], decoded.duration#, len(s[1])
                #time.sleep(.1)
                print len(s[1])
                foo.send(s[1])
                        #if decoded.duration is not None:
                        #    print decoded.duration, s[0]
                        #    break
                    #print (f.duration, s[0], len(s[1]), ord(s[1][0]))
    except Exception, details:
        print details
        sys.exit(1)
