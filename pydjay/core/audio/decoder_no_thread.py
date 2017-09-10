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

import gi
gi.require_version('Gst', '1.0')

import warnings
warnings.simplefilter("ignore")
from gi.repository import GLib

from gi.repository import Gst
from gi.repository import GObject


import sys
import threading
import os
import array
#from kivy.utils import platform

try:
    import queue
except ImportError:
    import Queue as queue

try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote


QUEUE_SIZE = -1
BUFFER_SIZE = 100
SENTINEL = '__GSTDEC_SENTINEL__'


# Exceptions.

class GStreamerError(Exception):
    pass


class UnknownTypeError(GStreamerError):
    """Raised when Gstreamer can't decode the given file type."""

    def __init__(self, streaminfo):
        super(UnknownTypeError, self).__init__(
            "can't decode stream: " + streaminfo
        )
        self.streaminfo = streaminfo


class FileReadError(GStreamerError):
    """Raised when the file can't be read at all."""
    pass


class NoStreamError(GStreamerError):
    """Raised when the file was read successfully but no audio streams
    were found.
    """

    def __init__(self):
        super(NoStreamError, self).__init__('no audio streams found')


class MetadataMissingError(GStreamerError):
    """Raised when GStreamer fails to report stream metadata (duration,
    channels, or sample rate).
    """
    pass


class IncompleteGStreamerError(GStreamerError):
    """Raised when necessary components of GStreamer (namely, the
    principal plugin packages) are missing.
    """

    def __init__(self):
        super(IncompleteGStreamerError, self).__init__(
            'missing GStreamer base plugins'
        )


# Managing the Gobject main loop thread.

_shared_loop_thread = None
_loop_thread_lock = threading.RLock()

GObject.threads_init()
Gst.init(None)


def get_loop_thread():
    """Get the shared main-loop thread.
    """
    global _shared_loop_thread
    with _loop_thread_lock:
        if not _shared_loop_thread:
            # Start a new thread.
            _shared_loop_thread = MainLoopThread()
            _shared_loop_thread.start()
        return _shared_loop_thread


class MainLoopThread(threading.Thread):
    """A daemon thread encapsulating a Gobject main loop.
    """

    def __init__(self):
        super(MainLoopThread, self).__init__()
        self.loop = GLib.MainLoop()
        self.daemon = True

    def run(self):
        self.loop.run()

# The decoder.


class GstAudioFile(object):
    """Reads raw audio data from any audio file that Gstreamer
    knows how to decode.
        >>> with GstAudioFile('something.mp3') as f:
        >>>     print f.samplerate
        >>>     print f.channels
        >>>     print f.duration
        >>>     for block in f:
        >>>         do_something(block)
    Iterating the object yields blocks of 16-bit PCM data. Three
    pieces of stream information are also available: samplerate (in Hz),
    number of channels, and duration (in seconds).
    It's very important that the client call close() when it's done
    with the object. Otherwise, the program is likely to hang on exit.
    Alternatively, of course, one can just use the file as a context
    manager, as shown above.
    """

    def __init__(self, path, num_channels=2, samplerate=44100, format="F32LE", timeout=None, start_time=None, end_time=None, use_threaded_gloop=True):
        self.duration = None
        self.track_length = None
        self.running = False
        self.finished = False
        self._num_channels = num_channels
        self._samplerate = samplerate
        self._format = format
        self._queue_timeout = timeout
        self._start_time = start_time
        self._end_time = end_time
        self.pipeline = Gst.Pipeline()
        self._use_threaded_gloop = use_threaded_gloop

        self.src = Gst.ElementFactory.make("filesrc", None)
        self.dec = Gst.ElementFactory.make("decodebin", None)
        self.conv = Gst.ElementFactory.make("audioconvert", None)
        self.resample = Gst.ElementFactory.make("audioresample", None)
        self.sink = Gst.ElementFactory.make("appsink", None)

        if self.src is None or \
           self.dec is None or \
           self.conv is None or \
           self.sink is None or \
           self.resample is None:
            # uridecodebin, audioconvert, or appsink is missing. We need
            # gst-plugins-base.
            raise IncompleteGStreamerError()

        # Register for bus signals.
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message::eos", self._message)
        bus.connect("message::error", self._message)

        # Configure the input.
        if path.startswith('file://'):
            path = path[7:]
        uri = os.path.abspath(path)

        self.src.set_property("location", uri)
        # The callback to connect the input.
        self.dec.connect("pad-added", self._pad_added)
        self.dec.connect("no-more-pads", self._no_more_pads)
        # And a callback if decoding failes.
        self.dec.connect("unknown-type", self._unkown_type)

        # Configure the output.
        # We want short integer data.
        self.sink.set_property(
            'caps',
            Gst.Caps.from_string('audio/x-raw, format=(string)F32LE, rate=(int)%s, channels=(int)%s' %
                                 (self._samplerate, self._num_channels)),
        )

        # TODO set endianness?
        # Set up the characteristics of the output. We don't want to
        # drop any data (nothing is real-time here); we should bound
        # the memory usage of the internal queue; and, most
        # importantly, setting "sync" to False disables the default
        # behavior in which you consume buffers in real time. This way,
        # we get data as soon as it's decoded.
        self.sink.set_property('drop', False)
        self.sink.set_property('max-buffers', BUFFER_SIZE)
        self.sink.set_property('sync', False)
        # The callback to receive decoded data.
        self.sink.set_property('emit-signals', True)
        self.sink.connect("new-sample", self._new_sample)

        # We'll need to know when the stream becomes ready and we get
        # its attributes. This semaphore will become available when the
        # caps are received. That way, when __init__() returns, the file
        # (and its attributes) will be ready for reading.
        self.ready_sem = threading.Semaphore(0)
        self.caps_handler = self.sink.get_static_pad("sink").connect(
            "notify::caps", self._notify_caps
        )

        # Link up everything but the decoder (which must be linked only
        # when it becomes ready).
        self.pipeline.add(self.src)
        self.pipeline.add(self.dec)
        self.pipeline.add(self.conv)
        self.pipeline.add(self.resample)
        self.pipeline.add(self.sink)

        self.src.link(self.dec)
        self.conv.link(self.resample)
        self.resample.link(self.sink)

        # Set up the queue for data and run the main thread.
        self.queue = queue.Queue(QUEUE_SIZE)
        self.thread = None
        if use_threaded_gloop:
            self.thread = get_loop_thread()

        # This wil get filled with an exception if opening fails.
        self.read_exc = None

        # Return as soon as the stream is ready!
        self.running = True
        self.got_caps = False
        self.pipeline.set_state(Gst.State.PLAYING)

        if use_threaded_gloop:
            self.ready_sem.acquire()

        if self.read_exc:
            # An error occurred before the stream became ready.
            self.close(True)
            raise self.read_exc

    # Gstreamer callbacks.

    def _notify_caps(self, pad, args):
        """The callback for the sinkpad's "notify::caps" signal.
        """
        # The sink has started to receive data, so the stream is ready.
        # This also is our opportunity to read information about the
        # stream.
        self.got_caps = True
        info = pad.get_current_caps().get_structure(0)

        # Stream attributes.
        self.channels = info.get_int('channels')[1]
        self.samplerate = info.get_int('rate')[1]

        # Query duration.
        success, length = pad.get_peer().query_duration(Gst.Format.TIME)
        if success:
            self.track_length = length  # / 1000000000
            if self._end_time is not None:
                if self._start_time is not None:
                    self.duration = self._end_time - self._start_time
                else:
                    self.duration = self._end_time
            else:
                if self._start_time is not None:
                    self.duration = length - self._start_time
                else:
                    self.duration = length

        else:
            self.duration = None

        # Allow constructor to complete.
        if self._use_threaded_gloop:
            self.ready_sem.release()
        self.seek(self._start_time)

    _got_a_pad = False

    def _pad_added(self, element, pad):
        """The callback for GstElement's "pad-added" signal.
        """
        # Decoded data is ready. Connect up the decoder, finally.
        name = pad.query_caps(None).to_string()
        if name.startswith('audio/x-raw'):
            nextpad = self.conv.get_static_pad('sink')
            if not nextpad.is_linked():
                self._got_a_pad = True
                pad.link(nextpad)

    def _no_more_pads(self, element):
        """The callback for GstElement's "no-more-pads" signal.
        """
        # Sent when the pads are done adding (i.e., there are no more
        # streams in the file). If we haven't gotten at least one
        # decodable stream, raise an exception.
        if not self._got_a_pad:
            self.read_exc = NoStreamError()
            if self._use_threaded_gloop:
                self.ready_sem.release()  # No effect if we've already started.

    def _new_sample(self, sink):
        """The callback for appsink's "new-sample" signal.
        """
        # print 'new sample'
        if self.running:
            # New data is available from the pipeline! Dump it into our
            # queue (or possibly block if we're full).
            success, position = self.pipeline.query_position(Gst.Format.TIME)
            if not success:
                position = 0

            buf = sink.emit('pull-sample').get_buffer()
            if self._end_time is not None and (position >= self._end_time):
                self.queue.put(SENTINEL)
            else:
                result, data = buf.map(Gst.MapFlags.READ)
                if result:
                    buffer_bytes = array.array('f', data.data)
                    buf.unmap(data)

                self.queue.put((position, buffer_bytes))
        return Gst.FlowReturn.OK

    def _unkown_type(self, uridecodebin, decodebin, caps):
        """The callback for decodebin's "unknown-type" signal.
        """
        # This is called *before* the stream becomes ready when the
        # file can't be read.
        streaminfo = caps.to_string()
        if not streaminfo.startswith('audio/'):
            # Ignore non-audio (e.g., video) decode errors.
            return
        self.read_exc = UnknownTypeError(streaminfo)
        if self._use_threaded_gloop:
            self.ready_sem.release()

    def _message(self, bus, message):
        """The callback for GstBus's "message" signal (for two kinds of
        messages).
        """
        print message.type

        if not self.finished:
            if message.type == Gst.MessageType.EOS:
                # The file is done. Tell the consumer thread.
                self.queue.put(SENTINEL)
                if not self.got_caps:
                    # If the stream ends before _notify_caps was called, this
                    # is an invalid file.
                    self.read_exc = NoStreamError()
                    # self.ready_sem.release()
                    if self._use_threaded_gloop:
                        self.ready_sem.release()

            elif message.type == Gst.MessageType.ERROR:
                gerror, debug = message.parse_error()
                print debug
                if 'not-linked' in debug:
                    self.read_exc = NoStreamError()
                elif 'No such file' in debug:
                    self.read_exc = IOError('resource not found')
                else:
                    self.read_exc = FileReadError(debug)
#                self.ready_sem.release()

                if self._use_threaded_gloop:
                    self.ready_sem.release()    # Iteration.

    def next(self):
        # Wait for data from the Gstreamer callbacks.
        # print 'next'
        try:
            val = self.queue.get(True, self._queue_timeout)
            if self._end_time is not None and val[0] >= self._end_time:
                raise StopIteration
        except queue.Empty:
            print 'empty queue'
            raise StopIteration
        if val == SENTINEL:
            raise StopIteration
        if (self._end_time is not None and (val[0] >= self._end_time)):
            raise StopIteration
        return val

    # For Python 3 compatibility.
    __next__ = next

    def __iter__(self):
        return self

    def set_start_time(self, timestamp):
        self._start_time = timestamp
        self.seek(self._start_time)

    def seek(self, timestamp):
        self.pipeline.seek_simple(Gst.Format.TIME,
                                  Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT,
                                  timestamp)
        while not self.queue.empty():
            try:
                discard = self.queue.get_nowait()
            except queue.Empty:
                break

    # Cleanup.
    def close(self, force=False):
        """Close the file and clean up associated resources.
        Calling `close()` a second time has no effect.
        """
        if self.running or force:
            self.running = False
            self.finished = True

            # Unregister for signals, which we registered for above with
            # `add_signal_watch`. (Without this, GStreamer leaks file
            # descriptors.)
            self.pipeline.get_bus().remove_signal_watch()

            # Stop reading the file.
            #self.dec.set_property("uri", None)
            #self.src.set_property("location", None)
            # Block spurious signals.
            self.sink.get_static_pad("sink").disconnect(self.caps_handler)

            # Make space in the output queue to let the decoder thread
            # finish. (Otherwise, the thread blocks on its enqueue and
            # the interpreter hangs.)
            try:
                self.queue.get_nowait()
            except queue.Empty:
                pass

            # Halt the pipeline (closing file).
            self.pipeline.set_state(Gst.State.NULL)

            # Delete the pipeline object. This seems to be necessary on Python
            # 2, but not Python 3 for some reason: on 3.5, at least, the
            # pipeline gets dereferenced automatically.
            del self.pipeline

    def __del__(self):
        self.close()

    # Context manager.
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
