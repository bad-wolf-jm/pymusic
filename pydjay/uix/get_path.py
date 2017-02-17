import os

#from kivy.uix.button import Button
#from kivy.properties import ObjectProperty, StringProperty
#from pydjay.uix import aligned_label


def get_path(path):
    #print  os.path.join(os.path.expanduser('~/Python/DJ'), os.path.dirname(__file__), path + '.png')
    return os.path.join(os.path.dirname(__file__), path + '.png')
