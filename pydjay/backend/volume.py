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

from __future__ import with_statement
from __future__ import division

# import sys
import threading
# import os
# import traceback
import jack
# import time
# import array
from multiprocessing import Process, Queue

#from decoder import get_loop_thread
try:
    import queue
except ImportError:
    import Queue as queue

QUEUE_SIZE = 100
BUFFER_SIZE = 100


class VolumeControllerDriver(object):
    def __init__(self, client_name="PYDjayJackClient", num_channels_in=2):
        super(VolumeControllerDriver, self).__init__()
        self.num_channels = num_channels_in
        self.client_name = client_name

        self.volume = 1.0

        self._jack_client = jack.Client(client_name)
        self.client_name = self._jack_client.name
        self.samplerate = self._jack_client.samplerate
        self.block_size = self._jack_client.blocksize
        self._output_ports = []
        self._input_ports = []
        self._volumes = []
        self._outputs = {}
        self._inputs = {}
        self._input_buffers = []  # array.array('f')
        self.stream_time = 0
        self.closed = False

        self._buffer_time = int(self.block_size * 1.0 / self.samplerate * 1000000000)

        for i in range(self.num_channels):
            self._volumes.append(1.0)
            port_name = "input_%s" % (i + 1)
            self._input_ports.append(self._jack_client.inports.register(port_name))
            self._inputs[port_name] = self._input_ports[i]
            port_name = "output_%s" % (i + 1)
            self._output_ports.append(self._jack_client.outports.register(port_name))
            self._outputs[port_name] = self._output_ports[i]

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

    def _process(self, length):
        set_time = False
        for channel_index in range(self.num_channels):
            in_ = self._input_ports[channel_index].get_array()
            out = self._output_ports[channel_index].get_array()
            if self._volumes[channel_index] == 1.0:
                out[:] = in_
            elif self._volumes[channel_index] == 0:
                out.fill(0)
            else:
                out[:] = self._volumes[channel_index] * in_

    def _blocksize_changed(self, block_size):
        self.block_size = block_size
        self._max_buffer_size = self.block_size * 30

    def _on_server_shutdown(self, *a):
        pass

    def close(self):
        self._jack_client.deactivate()
        self._jack_client.close()
        self.closed = True

    def set_volumes(self, value=1.0, channels=None):
        if channels is not None:
            if isinstance(channels, list):
                for i in range(len(channels)):
                    if isinstance(value, list):
                        self._volumes[channels[i] - 1] = value[i]
                    else:
                        self._volumes[channels[i] - 1] = value
            else:
                if not isinstance(value, list):
                    self._volumes[channels - 1] = value


class VolumeControllerProcess(Process):
    def __init__(self, name="", num_channels=2, in_queue=None, out_queue=None):
        super(VolumeControllerProcess, self).__init__()
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.client_name = name
        self.num_channels = num_channels
        self.player = None

    def run(self):
        self.output_driver = VolumeControllerDriver(self.client_name, self.num_channels)
        self.out_queue.put(('_init', (), {"client_name":  self.output_driver.client_name,
                                          "block_size":   self.output_driver.block_size,
                                          "samplerate":   self.output_driver.samplerate,
                                          "num_channels": self.output_driver.num_channels}))
        while True:
            try:
                command, args, kwargs = self.in_queue.get_nowait()
                if command == 'close':
                    print "CLOSING:", self.client_name
                    self.output_driver.close()
                    break
                try:
                    getattr(self.output_driver, command)(*args, **kwargs)
                except AttributeError, details:
                    pass
                except Exception, details:
                    print 'y', details
            except queue.Empty, details:
                pass
        print "Closing Queue VC"


class VolumeController(object):
    def __init__(self, client_name="PYDjayJackClient", num_channels=2, *args, **kw):
        # print 'GGGG'
        #super(VolumeController, self).__init__()
        object.__init__(self)
        # print 'FFFF'
        self.out_queue = Queue(maxsize=10)
        self.in_queue = Queue(maxsize=1000)
        self.ready_sem = threading.Semaphore(0)
        self._output_process = VolumeControllerProcess(client_name, num_channels,
                                                       self.out_queue, self.in_queue)
        self._output_process.daemon = True
        self._output_process.start()
        self._running = True
        self._foo = threading.Thread(target=self._print_info)
        self._foo.start()
        self.stream_time = 0
        self.ready_sem.acquire()

    def _init(self, block_size=0, samplerate=0, client_name="", num_channels=0):
        self.block_size = block_size
        self.samplerate = samplerate
        self.client_name = client_name
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

    def reset_timer(self, timestamp=0):
        self.out_queue.put(('reset_timer', (), {'timestamp': timestamp}))

    def set_stream_time(self, time):
        self.stream_time = time

    def set_volumes(self, *data, **kw):
        self.out_queue.put(('set_volumes', data, kw))

    def close(self):
        self.out_queue.put(('close', (), {}))
        self.out_queue.cancel_join_thread()
        self.in_queue.cancel_join_thread()
        self._running = False
        self._foo.join()
        self.out_queue.close()
        self.in_queue.close()
    shutdown = close
