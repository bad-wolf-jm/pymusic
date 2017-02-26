#Core of audio part
from pydjay.core.audio.player import AudioPlayer
from pydjay.core.audio.volume import VolumeController
from pydjay.core.precue import PreviewPlayer
from pydjay.core.keyboard import key_map

main_player      = AudioPlayer("MainPlayer", 2)
preview_player_o = AudioPlayer("PreviewPlayer", 2)
volume_control_o = VolumeController("VolumeControl", num_channels = 6)
#preview_volume_control = VolumeController("PrecuePlayerVolume")

preview_player_o.connect_outputs(output_1 = "VolumeControl:input_5",
                                 output_2 = "VolumeControl:input_6")

#preview_volume_control.connect_outputs(output_1 = "system:playback_5",
#                                       output_2 = "system:playback_6")
main_player.connect_outputs(output_1 = "VolumeControl:input_1",
                            output_2 = "VolumeControl:input_2")

main_player.connect_outputs(output_1 = "VolumeControl:input_3",
                            output_2 = "VolumeControl:input_4")

volume_control_o.connect_outputs(output_1 = "system:playback_1",
                                 output_2 = "system:playback_2",
                                 output_3 = "system:playback_5",
                                 output_4 = "system:playback_6",
                                 output_5 = "system:playback_5",
                                 output_6 = "system:playback_6")

from kivy.properties import AliasProperty
from kivy.event import EventDispatcher

class VolumeControl(EventDispatcher):
    def __init__(self):
        super(VolumeControl, self).__init__()
        
        self.channel_layout =  {'main_player':         [1,2],
                                'main_player_monitor': [3,4],
                                'preview_player':      [5,6]}
        self.volumes =  {'main_player':         1.0,
                         'main_player_monitor': 1.0,
                         'preview_player':      1.0,
                         'main_player_monitor_mute': 0.07}
        self.controller = volume_control_o


    def set_volume(self, channel, value):
        self.volumes[channel] = value
        if channel in self.channel_layout:
            self.controller.set_volumes(channels = self.channel_layout[channel], value = value)
        return True

    def get_volume(self, channel):
        return self.volumes[channel]

    main_player = AliasProperty(lambda self: self.get_volume('main_player'),
                                lambda self, value: self.set_volume('main_player', value))

    preview_player = AliasProperty(lambda self: self.get_volume('preview_player'),
                                   lambda self, value: self.set_volume('preview_player', value))

    main_player_monitor = AliasProperty(lambda self: self.get_volume('main_player_monitor'),
                                        lambda self, value: self.set_volume('main_player_monitor', value))
    
volume_control = VolumeControl()
volume_control.set_volume('main_player', 1.0)
volume_control.set_volume('main_player_monitor', 1.0)
volume_control.set_volume('preview_player', 1.0)
volume_control.set_volume('main_player_monitor_mute', .07)

def set_volume(channel, volume):
    volume_control.set_volume(channel, volume)
    #pass

def get_volume(channel):
    return volume_control.get_volume(channel)
    #pass

def _increase_main_volume(*a):
    v =  volume_control.main_player
    v += .1
    v = min(v, 8)
    volume_control.main_player = v
    
def _decrease_main_volume(*a):
    v =  volume_control.main_player
    v -= .1
    v = max(v, 0)
    volume_control.main_player = v
    
key_map.bind(on_main_volume_up =   _increase_main_volume,
             on_main_volume_down = _decrease_main_volume)



def _increase_monitor_volume(*a):
    v =  volume_control.main_player_monitor
    v += .1
    v = min(v, 8)
    volume_control.main_player_monitor = v
    
def _decrease_monitor_volume(*a):
    v =  volume_control.main_player_monitor
    v -= .1
    v = max(v, 0)
    volume_control.main_player_monitor = v
    
key_map.bind(on_monitor_volume_up =   _increase_monitor_volume,
             on_monitor_volume_down = _decrease_monitor_volume)


def _increase_preview_volume(*a):
    v =  volume_control.preview_player
    v += .1
    v = min(v, 8)
    volume_control.preview_player = v
    
def _decrease_preview_volume(*a):
    v =  volume_control.preview_player
    v -= .1
    v = max(v, 0)
    volume_control.preview_player = v
    
key_map.bind(on_preview_volume_up =   _increase_preview_volume,
             on_preview_volume_down = _decrease_preview_volume)



preview_player = PreviewPlayer(preview_player_o, volume_control)


def _preview_seek(self, t):
    #time in seconds
    t *= 1000000000
    preview_player.player.seek_relative(t)

def _preview_stop(self):
    preview_player.stop()

def _preview_pause(self):
    preview_player.pause()

key_map.bind(on_seek_preview = _preview_seek)
key_map.bind(on_stop_preview = _preview_stop)
key_map.bind(on_play_pause_preview = _preview_pause)

    
def close_keyboard():
    pass

import os
from pydjay.core.playback_manager import PlaybackManager
from pydjay.core.queue import PlayQueue
from pydjay.core.session import SessionManager


HOME         = os.path.expanduser('~')
PYDJAY_CACHE = os.path.join(HOME, '.pydjay')
STATE        = os.path.join(PYDJAY_CACHE, 'state')
SESSIONS     = os.path.join(PYDJAY_CACHE, 'sessions')
PLAYLISTS    = os.path.join(PYDJAY_CACHE, 'playlists')

session_manager  = SessionManager(os.path.join(SESSIONS, "Current Session.m3u"))
play_queue       = PlayQueue()
playback_manager = PlaybackManager(main_player, play_queue, session_manager)
