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

import sys


import os
import gi
import pprint
import sys
import urllib
gi.require_version("Gst", "1.0")
#gi.require_version('Gtk', '3.0')
from gi.repository import Gst, GObject as gobject, GLib

Gst.init(None)     
gobject.threads_init()

#import gobject
#gobject.threads_init()
#
##import pygst
#pygst.require('0.10')
#import gst


class WaveformGen(Gst.Element):
    """ A basic, buffer forwarding gstreamer element """

    #here we register our plugin details
    __gstdetails__ = (
        "Wafeform Image Generator",
        "wavegen.py",
        "gst.Element, that passes a buffer from source to sink (a filter)",
        "Stephen Griffiths <scgmk5@gmail.com>")
    
    #source pad (template): we send buffers forward through here
    #print dir(Gst.PadTemplate)
    #_srctemplate = Gst.PadTemplate ('src',
    #    Gst.PadDirection.SRC,
    #    Gst.Pad.ALWAYS,
    #    Gst.caps_new_any())
    
    #sink pad (template): we recieve buffers from our sink pad
    #print dir(Gst.Caps)
    _sinktemplate = Gst.PadTemplate.new('sink',
                                        Gst.PadDirection.SINK,
                                        Gst.PadPresence.ALWAYS,
                                        Gst.Caps.new_any())
    
    #register our pad templates
    __gsttemplates__ = (_sinktemplate, )

    def __init__(self, *args, **kwargs):   
        #initialise parent class
        Gst.Element.__init__(self, *args, **kwargs)
        
        #source pad, outgoing data
        #self.srcpad = gst.Pad(self._srctemplate)
        
        #sink pad, incoming data
        self.sinkpad = Gst.Pad.new_from_template(self._sinktemplate)
        #self.sinkpad2 = Gst.Pad.new_from_template(self._sinktemplate)
        #print self.sinkpad.get_caps()
        #pprint.pprint(dir(self.sinkpad))
        #self.sinkpad.set_setcaps_function(self._sink_setcaps)
        self.sinkpad.set_chain_function(self._sink_chain)
        #self.sinkpad.set_active(True)
        #self.sinkpad2.set_chain_function(self._sink_chain)
        #self.sinkpad2.set_active(True)
        
        #make pads available
        #self.add_pad(self.srcpad)
        self.add_pad(self.sinkpad)
        #self.add_pad(self.sinkpad2)
    
    def _sink_setcaps(self, pad, caps):
        #we negotiate our capabilities here, this function is called
        #as autovideosink accepts anything, we just say yes we can handle the
        #incoming data
        return True
    
    def _sink_chain(self, pad, buf):
        #this is where we do filtering
        #and then push a buffer to the next element, returning a value saying
        # it was either successful or not.
        print "FOO", len(buf)
        return Gst.FlowReturn.OK
        #return self.srcpad.push(buf)


        
class Decodebin:
    def __init__(self, location):
        # The pipeline
        self.pipeline = Gst.Pipeline()
        
        # Create bus and connect several handlers
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message::eos', self.on_eos)
        #self.bus.connect('message::tag', self.on_tag)
        self.bus.connect('message::error', self.on_error)
        
        # Create elements
        self.src = Gst.ElementFactory.make('filesrc')
        self.dec = Gst.ElementFactory.make('decodebin')
        self.conv = Gst.ElementFactory.make('audioconvert')
        self.rsmpl = Gst.ElementFactory.make('audioresample')
        self.sink = WaveformGen()#Gst.ElementFactory.make('fakesink')
        
        # Set 'location' property on filesrc
        self.src.set_property('location', location)
        
        # Connect handler for 'new-decoded-pad' signal 
        self.dec.connect('pad-added', self.on_new_decoded_pad)
        
        # Add elements to pipeline
        self.pipeline.add(self.src, self.dec, self.conv, self.rsmpl, self.sink)
        
        # Link *some* elements 
        # This is completed in self.on_new_decoded_pad()
        self.src.link(self.dec)
        
        self.conv.link(self.rsmpl)
        self.rsmpl.link(self.sink)
        
        self.apad = self.conv.get_static_pad('sink')

        self.mainloop = gobject.MainLoop()
        
        # And off we go!
        self.pipeline.set_state(Gst.State.PLAYING)
        self.mainloop.run()
		
		
    def on_new_decoded_pad(self, element, pad):
        string = pad.query_caps(None).to_string()
        #name = caps[0].get_name()
        print 'on_new_decoded_pad:', string
        if string.startswith('audio/x-raw') or string.startswith('audio/x-raw-int'):
            if not self.apad.is_linked(): # Only link once
                pad.link(self.apad)
			
			
    def on_eos(self, bus, msg):
        print 'on_eos'
        self.mainloop.quit()
		
		
    def on_tag(self, bus, msg):
        taglist = msg.parse_tag()
        print 'on_tag:', taglist
        for key in taglist.keys():
            print '\t%s = %s' % (key, taglist[key])
			
			
    def on_error(self, bus, msg):
        error = msg.parse_error()
        print 'on_error:', error[1]
        self.mainloop.quit()
        




#if __name__ == '__main__':
#	if len(sys.argv) == 2:
Decodebin("/Users/jihemme/Python/DJ/pydjay/audio/test.mp3")
#	else:
#		print 'Usage: %s /path/to/media/file' % sys.argv[0]
