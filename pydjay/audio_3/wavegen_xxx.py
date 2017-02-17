import os
import gi
import pprint
import sys
import urllib
gi.require_version("Gst", "1.0")
#gi.require_version('Gtk', '3.0')
from gi.repository import Gst, GObject, GLib


#%foo = Gst.ElementFactory.make("fakesync", "None")
#%caps = foo.get_pad('sink').get_caps()


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
        print "FOO"
        #return self.srcpad.push(buf)

#here we register our class with glib, the c-based object system used by
#gstreamer
GObject.type_register(WaveformGen)





## this code creates the following pipeline, equivalent to 
## gst-launch-0.10 videotestsrc ! videoscale ! ffmpegcolorspace !
### NewElement ! autovideosink

# first create individual gstreamer elements

#source = gst.element_factory_make("videotestsrc")
#print "making new element"
#newElement = NewElement()
#print "made new element"
#vscale = gst.element_factory_make("videoscale")
#cspace = gst.element_factory_make("ffmpegcolorspace")
#vsink  = gst.element_factory_make("autovideosink")

# create the pipeline

#p = gst.Pipeline()
#p.add(source, vscale, cspace, newElement,
#    vsink)
#gst.element_link_many(source, vscale, cspace, newElement,
#    vsink)
# set pipeline to playback state

#p.set_state(gst.STATE_PLAYING)

# start the main loop, pitivi does this already.

#gtk.main()
