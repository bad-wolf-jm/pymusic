import os
import re
import mimetypes

from functools import partial
from threading import Thread
from os.path import getsize
from datetime import datetime

from kivy.clock import mainthread
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.selectableview import SelectableView
from kivy.adapters.simplelistadapter import SimpleListAdapter


from kivy.properties import ObjectProperty
from kivy.factory import Factory

from pydjay.library.track import load_file
from pydjay.gui.utils import seconds_to_human_readable


from kivy.graphics import *
from kivy.uix.image import Image
from kivy.core.image.img_pygame import ImageLoaderPygame
#from pydjay.uix import screen, paged_grid, paged_display
#from pydjay.uix import clickable_area
#from pydjay.uix import long_press_button
#from pydjay.uix import screen

#from pydjay.gui.files_screen import file_browser, location_browser
#from mediacentre.skins.default.theme import get_path



import io
from kivy.core.image import Image as CoreImage
from kivy.graphics.texture import Texture
from pydjay.utils import tmpfile

_tmp_files = []

class MemoryImage(Image):
    """Display an image already loaded in memory."""
    memory_data = ObjectProperty(None)

    def __init__(self, memory_data = None, **kwargs):
        super(MemoryImage, self).__init__(**kwargs)
        #self._core_image = None
        self.memory_data = memory_data
        self.bind(on_size = self.on_memory_data)

    def on_memory_data(self, *args):
        """Load image from memory."""
        if self.memory_data is not None:
            ext = {'image/jpeg': 'jpg','image/png': 'png'}.get(self.memory_data[0], None)
            if ext is not None:
                self._tmp_file = tmpfile.new_temp_file(prefix = 'cover', extension='.'+ext)
                foo = open(self._tmp_file, 'w+b')
                foo.write(self.memory_data[1])
                foo.close()
                self.source = self._tmp_file

Factory.register('MemoryImage', MemoryImage)    
