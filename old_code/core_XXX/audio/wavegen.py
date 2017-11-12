#!/usr/bin/env python

# decodebin.py - Audio autopluging example using 'decodebin' element
# Copyright (C) 2006 Jason Gerard DeRose <jderose@jasonderose.org>

# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301, USA.

# import sys


# import os
import gi
# import pprint
# import sys
# import urllib
# import threading

gi.require_version("Gst", "1.0")
#gi.require_version('Gtk', '3.0')
from gi.repository import Gst, GObject as gobject

Gst.init(None)
gobject.threads_init()


# from struct import unpack_from
from kivy.clock import mainthread


#import gobject
# gobject.threads_init()
#
##import pygst
# pygst.require('0.10')
#import gst
import array
import numpy
# from player
import decoder


class WaveformGenerator:
    #    """ A basic, buffer forwarding gstreamer element """

    # here we register our plugin details
    #    __gstdetails__ = (
    #        "Wafeform Image Generator",
    #        "wavegen.py",
    #        "gst.Element, that passes a buffer from source to sink (a filter)",
    #        "Stephen Griffiths <scgmk5@gmail.com>")

    # source pad (template): we send buffers forward through here
    # print dir(Gst.PadTemplate)
    #    _srctemplate = Gst.PadTemplate.new('src',
    #        Gst.PadDirection.SRC,
    #        Gst.PadPresence.ALWAYS,
    #        Gst.Caps.new_any())

    # sink pad (template): we recieve buffers from our sink pad
    # print dir(Gst.Caps)
    #    _sinktemplate = Gst.PadTemplate.new('sink',
    #                                        Gst.PadDirection.SINK,
    #                                        Gst.PadPresence.ALWAYS,
    #                                        Gst.Caps.new_any())

    # register our pad templates
    #    __gsttemplates__ = (_sinktemplate, )

    def __init__(self, num_data_points, new_data_point_cb=None, process_done_cb=None, *args, **kwargs):
        #        Gst.Element.__init__(self, *args, **kwargs)
        #        self.srcpad = Gst.Pad.new_from_template(self._srctemplate)
     #       self.srcpad.set_chain_function(self._sink_chain)

        #        self.sinkpad = Gst.Pad.new_from_template(self._sinktemplate)
        #        self.sinkpad.set_chain_function(self._sink_chain)
        #        self.sinkpad.set_event_function(self._sink_event)
        #        self.forms = {'(string)S16LE': 'i','(string)S32LE': 'l'}#,4)}

        #        self.add_pad(self.sinkpad)
        #        self.add_pad(self.srcpad)
        self._num_data_points = num_data_points
        self._duration = None
#        self._parent = parent
        self._idx = 0
        self._eos = False
        self._force_stop = False
        self._packet_queue = []
        self._data_points = []
        # self.srcpad.set_query_function(self._handle_src_query)
        # self.sinkpad.set_query_function(self._handle_sink_query)
        self._generator_thread = None
        self._generator_thread_running = False
        self._new_data_point_cb = new_data_point_cb
        self._process_done_cb = process_done_cb

    def set_data_point_callback(self, cb):
        self._new_data_point_cb = cb

    def set_process_done_callback(self, cb):
        self._process_done_cb = cb

    def get_data_points(self):
        return self._data_points

    # def _run_generator_thread(self, filename):
    #    self.sample_generator = decoder.GstAudioFile(filename, format = 'S16LE')
    #    self._duration = None
    #    self._data_points = []
    #    self._generator_thread_running = True
    #    with self.sample_generator as generator:
    #        self.stream_rate  = generator.samplerate
    #        self.num_channels = generator.channels
    #        for buf in generator:
    #            if not self._generator_thread_running:
    #                break
    #            if self._duration is None:
    #                self._duration = generator.duration
    #            self._sink_chain(buf)
    #            #print 'f '
    #        else:
    #            if self._process_done_cb is not None:
    #                self._process_done_cb(self._data_points)
    #        self._generator_thread_running = False
    #        self._generator_thread = None

    # def stop_generator_thread(self):
    # if self._generator_thread is not None:
    #        self._generator_thread_running = False
    #        self._generator_thread.join()

    # def start_generator_thread(self, filename):
    #    self.stop_generator_thread()
    #    self._generator_thread = threading.Thread(target = self._run_generator_thread, args = (filename, ))
    #    self._generator_thread.start()

    def force_stop(self):
        self._force_stop = True

    def generate_waveform(self, filename):
        self.sample_generator = decoder.GstAudioFile(
            filename, format='S16LE', timeout=2, samplerate=250)
        self._duration = None
        self._force_stop = False
        self._data_points = []
        with self.sample_generator as generator:
            self.stream_rate = generator.samplerate
            self.num_channels = generator.channels
            for buf in generator:
                if self._duration is None:
                    self._duration = generator.duration
                if self._force_stop:
                    break
                self._sink_chain(buf)
        # print "WAVEGEN DONE"
        return self._data_points
        # if self._process_done_cb is not None:
        #    self._process_done_cb(self._data_points)


#    def _sink_event(self, pad, event):
#        typ =  event.type
#        retval = False
#        #print typ
#        if typ == Gst.EventType.CAPS:
#            new_caps = event.parse_caps()
#            #print "I KNOW THE STREAM FORMAT!!!:", new_caps
#            foo = new_caps.to_string().split(', ')
#            format = {}
#            for data in foo[1:]:
#                key, value = data.split('=')
#                format[key] = value
#            #retval = True

#            self.stream_format   = format.get('format', None)
#            stream_layout   = format.get('layout', None)
#            stream_rate     = format.get('rate', None)
#            if stream_rate is not None:
#                self.stream_rate = int(stream_rate[5:])

#            stream_channels = format.get('channels', None)
#            if stream_channels is not None:
#                self.num_channels = int(stream_channels[5:])


#            return True
#        if typ == Gst.EventType.EOS:
#            if self._process_done_cb is not None:
#                self._process_done_cb(self._data_points)
#            #new_caps = event.parse_eos()
#            #print "END OF StREEAM"
#            return False

#        if Gst.EventType.get_flags(typ) == Gst.EventTypeFlags.DOWNSTREAM:
#            return self.srcpad.send_event(event)
#        return  True#self.srcpad.send_event(event)

    def _sink_chain(self, buf):
        # this is where we do filtering
        # and then push a buffer to the next element, returning a value saying
        # it was either successful or not.
        time_per_packet = int(1.0 / self.stream_rate * 1000000000)  # in nanoseconds

        # if self._duration is not None:
        #foo = self._parent.query_duration(Gst.Format.TIME)
        # print foo
        # if foo[0]:
        # self._duration =
        #self._duration = [1]
        # self._duration / (time_per_packet * self._num_data_points * 2)
        self._packets_per_data_point = 1

        # print "FOO", self._idx, buf.get_size(), buf.get_sizes(), buf.pts, buf.duration, self._duration, self._packets_per_data_point, len(self._packet_queue)
        # if buf is None:

        pts, data = buf  # .map(Gst.MapFlags.READ)
        # try:
        #assert res
        offset = 0
        buffer_bytes = array.array('f', data)
        num_samples = len(buffer_bytes)
        packets = []
        timestamp = pts

        while offset + self.num_channels < num_samples:
            self._packet_queue.append(
                (timestamp, tuple(buffer_bytes[offset:offset + self.num_channels])))
            offset += self.num_channels
            timestamp += time_per_packet

        # finally:
        #    buf.unmap(mapinfo)

        self._process_packet_queue()

        # if self._eos:
        #    return Gst.FlowReturn.EOS
        # return self.srcpad.push(buf)

    def _process_packet_queue(self):
        def _av(x):
            # print x
            return float(x[0] + x[1]) / 2

        if self._duration is not None:
            while len(self._packet_queue) >= 1:  # self._packets_per_data_point:#

                #min_timestamp = self._packet_queue[0][0]
                #max_timestamp = self._packet_queue[self._packets_per_data_point-1][0]
                # average_timestamp = float(max_timestamp + min_timestamp) / 2 #numpy.mean([foo[0] for foo in self._packet_queue[0:self._packets_per_data_point]])

                timestamp = self._packet_queue[0][0]
                #max_timestamp = self._packet_queue[self._packets_per_data_point-1][0]
                # average_timestamp = float(max_timestamp + min_timestamp) / 2 #numpy.mean([foo[0] for foo in self._packet_queue[0:self._packets_per_data_point]])
                sample = self._packet_queue[0][1]

                value = (sample[0] + sample[1]) / 2

                # print min_timestamp, max_timestamp, average_timestamp
                #sams = [sample[1] for sample in self._packet_queue[0:self._packets_per_data_point]]
                #vals = map(numpy.mean, [sample[1] for sample in self._packet_queue[0:self._packets_per_data_point]])

                # = [sample[1] for sample in self._packet_queue[0:self._packets_per_data_point]]
                # print sams
                #a_vals = [_av(x) for x in sams]
                # max_points = numpy.amax(a_vals)#map(numpy.mean, [sample[1] for sample in self._packet_queue[0:self._packets_per_data_point]]))
                # min_points = numpy.amin(a_vals)#map(numpy.mean, [sample[1] for sample in self._packet_queue[0:self._packets_per_data_point]]))
                self._idx += 1
                new_data_point = (self._duration, timestamp, value)  # (max_points+min_points) / 2)
                # print new_data_point
                if self._new_data_point_cb is not None:
                    self._new_data_point_cb(*new_data_point)
                self._data_points.append((timestamp, value))  # (max_points+min_points) / 2))
                del self._packet_queue[0]


#    def _process_packet_queue(self):
#        if self._duration is not None:
#            while len(self._packet_queue) > self._packets_per_data_point:
#                average_timestamp = numpy.mean([foo[0] for foo in self._packet_queue[0:self._packets_per_data_point]])
#                points = numpy.mean(map(numpy.mean, [sample[1] for sample in self._packet_queue[0:self._packets_per_data_point]]))
#                self._idx += 1
#                print self._idx, (average_timestamp, points)
#                self._data_points.append((average_timestamp, points))
#                del self._packet_queue[0:self._packets_per_data_point]

# class Decodebin:
#    def __init__(self, location, num_data_points):

        # Create bus and connect several handlers

#        self._num_data_points = num_data_points
#        self._new_data_point_cb = None
#        self._process_done_cb = None

#    def set_filename(self, name):
#        #self.pipeline.set_state(Gst.State.READY)
#        # Create elements
#        self.pipeline = Gst.Pipeline()
#        self.bus = self.pipeline.get_bus()
#        self.bus.add_signal_watch()
#        self.bus.connect('message::eos', self.on_eos)
#        #self.bus.connect('message::tag', self.on_tag)
#        self.bus.connect('message::error', self.on_error)
#
#        self.src     = Gst.ElementFactory.make('filesrc')
#        self.dec     = Gst.ElementFactory.make('decodebin')
#        self.conv    = Gst.ElementFactory.make('audioconvert')
#        self.rsmpl   = Gst.ElementFactory.make('audioresample')
#        self.wavegen = WaveformGen(self.pipeline, self._num_data_points, self._on_new_data_point, self._on_process_done)#Gst.ElementFactory.make('fakesink')
#        self.sink    = Gst.ElementFactory.make('fakesink')

        # Set 'location' property on filesrc

        # Connect handler for 'new-decoded-pad' signal
#        self.dec.connect('pad-added', self.on_new_decoded_pad)

        # Add elements to pipeline
#        self.pipeline.add(self.src, self.dec, self.conv, self.rsmpl, self.wavegen, self.sink)
#
        # Link *some* elements
        # This is completed in self.on_new_decoded_pad()
#        self.src.link(self.dec)

#        self.conv.link(self.rsmpl)
#        self.rsmpl.link(self.wavegen)
#        self.wavegen.link(self.sink)
 #
 #       self.apad = self.conv.get_static_pad('sink')

        #self.mainloop = gobject.MainLoop()

        # And off we go!
        # self.pipeline.set_state(Gst.State.PLAYING)
       # self.mainloop.run()


#        self.src.set_property('location', name)


#        self.pipeline.set_state(Gst.State.PLAYING)

 #   def set_data_point_callback(self, cb):
 #       self._new_data_point_cb = cb

 #   def set_process_done_callback(self, cb):
 #       self._process_done_cb = cb

 #   def _on_new_data_point(self, total_time, timestamp, point):
 #       #print timestamp, point
 #       if self._new_data_point_cb is not None:
 #           self._new_data_point_cb(total_time, timestamp, point)

    #@mainthread
 #   def _on_process_done(self, data_points):
 #       #self.pipeline.set_state(Gst.State.READY)
 #       if self._process_done_cb is not None:
 #           self._process_done_cb(data_points)

 #   def on_new_decoded_pad(self, element, pad):
 #       string = pad.query_caps(None).to_string()
 #       #name = caps[0].get_name()
 #       #print 'on_new_decoded_pad:', string
 #       if string.startswith('audio/x-raw') or string.startswith('audio/x-raw-int'):
 #           if not self.apad.is_linked(): # Only link once
 #               pad.link(self.apad)

 #   def on_eos(self, bus, msg):
 #       print 'on_eos'
 #       print self.dec.query_duration(Gst.Format.TIME)

        # self.mainloop.quit()

 #   def on_tag(self, bus, msg):
 #       taglist = msg.parse_tag()
 #       #print 'on_tag:', taglist
 #       #for key in taglist.keys():
 #       #    print '\t%s = %s' % (key, taglist[key])

 #   def on_error(self, bus, msg):
 #       error = msg.parse_error()
 #       print 'on_error:', error[1]
 #       #self.mainloop.quit()


# class WaveformGenerator(Decodebin):
#    def __init__(self, filename, num_data_points):
#        Decodebin.__init__(self, filename, num_data_points)
#        #self.mainloop = gobject.MainLoop()
#        # And off we go!
#        #self.pipeline.set_state(Gst.State.PLAYING)
#        #self.mainloop.run()


#    def stop(self):
#        self.pipeline.set_state(Gst.State.READY)
#    #def _on_new_data_point(self, timestamp, point):
#    #    if self._new_data_point_cb is not None:
#    #        self._new_data_point_cb(timestamp, point)

#    def get_data_points(self):
#        return self.wavegen.get_data_points()


#    def _on_process_done(self, data_points):
#        #self.mainloop.quit()
#        Decodebin._on_process_done(self,data_points)
#        #self.pipeline.set_state(Gst.State.NULL)
#        #if self._process_done_cb is not None:
#        #    self._process_done_cb(data_points)

# if __name__ == '__main__':
#	if len(sys.argv) == 2:
#WaveformGenerator("/Users/jihemme/Python/DJ/pydjay/audio/test.mp3", 20000)
#	else:
#		print 'Usage: %s /path/to/media/file' % sys.argv[0]
