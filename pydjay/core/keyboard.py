#from kivy.core.window import Window
from kivy.event import EventDispatcher
#from kivy.base import EventLoop

__enable_keyboard_shortcuts = True


def enable_keyboard_shortcuts():
    global __enable_keyboard_shortcuts
    __enable_keyboard_shortcuts = True

def disable_keyboard_shortcuts():
    global __enable_keyboard_shortcuts
    __enable_keyboard_shortcuts = False


def key_pressed(key, mods):
    print __enable_keyboard_shortcuts,  key, mods
    k_map = {'q': None, #main volume up
             'a': None, #main volume down
             'p': None, #monitor volume up
             ';': None, #monitor volume down
             '[': None, #preview volume up
             "'": None, #preview volume down
             'k': None, #play/pause preview
             'j': None, #stop preview
             ',': None, #preview seek back
             '.': None, #preview seek forward
             'shift+,': None, #preview long seek back
             'shift+.': None} #preview long seek forward

    key_seq = "+".join(mods+[key[1]])
    action = k_map.get(key_seq, None)
    if action is not None:
        action()
             
    #if __enable_keyboard_shortcuts:
    #    print key, scan, codepoint, mods

class KeyMappings(EventDispatcher):
    def __init__(self, *a, **k):
        super(KeyMappings, self).__init__(*a, **k)
        self.register_event_type('on_main_volume_up')
        self.register_event_type('on_main_volume_down')
        self.register_event_type('on_monitor_volume_up')
        self.register_event_type('on_monitor_volume_down')
        self.register_event_type('on_preview_volume_up')
        self.register_event_type('on_preview_volume_down')
        
        self.register_event_type('on_play_pause_preview')
        self.register_event_type('on_stop_preview')
        self.register_event_type('on_seek_preview')
        self.register_event_type('on_seek_preview_back')

        self.register_event_type('on_cycle_focus')
        self.register_event_type('on_edit_track')

    def on_main_volume_up(self):
        pass

    def on_main_volume_down(self):
        pass

    def on_monitor_volume_up(self):
        pass

    def on_monitor_volume_down(self):
        pass

    def on_preview_volume_up(self):
        pass

    def on_preview_volume_down(self):
        pass

    def on_play_pause_preview(self):
        pass

    def on_stop_preview(self):
        pass

    def on_seek_preview_back(self):
        pass

    def on_seek_preview(self, value):
        pass

    def on_cycle_focus(self, i):
        pass

    def on_edit_track(self):
        pass



        #EventLoop.window.bind(on_keyboard = _keyboard_key_pressed)


    def key_pressed(self, key, mods):
#        print __enable_keyboard_shortcuts,  key, mods
        k_map = {'q':       lambda: self.dispatch('on_main_volume_up'), #main volume up
                 'a':       lambda: self.dispatch('on_main_volume_down'), #main volume down
                 '[':       lambda: self.dispatch('on_monitor_volume_up'), #monitor volume up
                 '\'':      lambda: self.dispatch('on_monitor_volume_down'), #monitor volume down
                 'p':       lambda: self.dispatch('on_preview_volume_up'), #preview volume up
                 ":":       lambda: self.dispatch('on_preview_volume_down'), #preview volume down
                 'spacebar':       lambda: self.dispatch('on_play_pause_preview'), #play/pause preview
                 'shift+spacebar': lambda: self.dispatch('on_stop_preview'), #stop preview
                 ',':       lambda: self.dispatch('on_seek_preview', -1), #preview seek back
                 '.':       lambda: self.dispatch('on_seek_preview', 1), #preview seek forward
                 'shift+,': lambda: self.dispatch('on_seek_preview', -5), #preview long seek back
                 'shift+.': lambda: self.dispatch('on_seek_preview', 5),
                 'shift+ctrl+,': lambda: self.dispatch('on_seek_preview', -10), #preview long seek back
                 'shift+ctrl+.': lambda: self.dispatch('on_seek_preview', 10), #preview long seek back
                 'right':          lambda: self.dispatch('on_cycle_focus', 1),
                 'left':    lambda: self.dispatch('on_cycle_focus', -1),
                 'ctrl+e':    lambda: self.dispatch('on_edit_track')} #preview long seek forward

        key_seq = "+".join(mods+[key[1]])
        #print key_seq
        action = k_map.get(key_seq, None)
        if action is not None:
            action()

key_map = KeyMappings()
