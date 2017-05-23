#Core of audio part
from pydjay.core.audio.volume import VolumeController
from pydjay.core.precue import PreviewPlayer
from pydjay.core.keyboard import key_map

import zmq
import os
import threading
import json
import time
from pydjay.backend.push_server import PushClient
from pydjay.backend.command_server import RPCClient
from kivy.properties import StringProperty, NumericProperty, AliasProperty
from kivy.event import EventDispatcher
from kivy.clock import mainthread, Clock


from pydjay.backend.main_player import main_player as main_player_server
from pydjay.backend.preview_player import main_player as preview_player_server
from pydjay.backend.volume_controller import c as volume_controller_server



volume_controller_server.start()
time.sleep(2)
preview_player_server.start()
time.sleep(2)
main_player_server.start()
time.sleep(2)

#preview_player = AudioServer("PreviewPlayer", 2, port = 9998, event_port = 5556)
#preview_player.connect_outputs(output_1 = "VolumeControl:input_5",
#                               output_2 = "VolumeControl:input_6")
#preview_player.start(threaded = False)
#
#
#main_player = AudioServer("MainPlayer", 2, port = 9999, event_port = 5557)
#main_player.connect_outputs(output_1 = "VolumeControl:input_1",
#                            output_2 = "VolumeControl:input_2")
#main_player.connect_outputs(output_1 = "VolumeControl:input_3",#
#                            output_2 = "VolumeControl:input_4")
#main_player.start(threaded = True)



class AudioPlayer(EventDispatcher): #, RPCClient, PushClient):
    state                = StringProperty(None, allownone = True)
    track_duration       = NumericProperty(None, allownone = True)
    track_position       = NumericProperty(None, allownone = True)
    track_length         = NumericProperty(None, allownone = True)

    def __init__(self, port = 9999, event_port = 5757, *args, **kw):
        EventDispatcher.__init__(self)
        self.event = PushClient("", event_port)
        self.rpc   = RPCClient("", port)
        self.event.register_push_event_handler('end_of_stream',         self.signal_end_of_stream)
        self.event.register_push_event_handler('track_position_notice', self._set_track_position)
        self.event.register_push_event_handler('track_duration_notice', self._set_track_duration)
        self.event.register_push_event_handler('track_length_notice',   self._set_track_length)
        self.register_event_type("on_end_of_stream")
        self.event.start()

    def on_end_of_stream(self, *args):
       pass

    @mainthread
    def set_time(self, type_, value):
        setattr(self, type_, value)

    def _set_track_duration(self, value = None):
        self.set_time('track_duration', value)

    def _set_track_position(self, value = None):
        self.set_time('track_position', value)

    def _set_track_length(self, value = None):
        self.set_time('track_length', value)

    @mainthread
    def signal_end_of_stream(self, after_time = 0):
        self.dispatch('on_end_of_stream')

    def _get_remaining_time(self, *a):
        if self.track_duration is not None and self.track_position is not None:
            return self.track_duration - self.track_position
        return 0

    remaining_time  = AliasProperty(_get_remaining_time, bind = ['track_duration', 'track_position'])

    def play(self, filename, start_time = None, end_time = None):
        self.rpc.remote_call('play', filename, start_time = start_time, end_time = end_time)

    def stop(self, flush = False):
        self.rpc.remote_call('stop', flush = flush)

    def pause(self):
        self.state = "paused"

    def seek(self, timestamp):
        self.rpc.remote_call('seek', timestamp)

    def seek_relative(self, time):
        self.rpc.remote_call('seek_relative', time)

    def shutdown(self):
        self.event.stop()
        self.event.join()

main_player      = AudioPlayer(port = 9999, event_port = 5557)
preview_player_o = AudioPlayer(port = 9998, event_port = 5556)

class VolumeControl(EventDispatcher):
    def __init__(self, port = 9997, event_port = 5555):
        EventDispatcher.__init__(self)
        self.rpc = RPCClient("", port)
        self.event = PushClient("", event_port)
        self.channel_layout =  {'main_player':         [1,2],
                                'main_player_monitor': [3,4],
                                'preview_player':      [5,6]}
        self.volumes =  {'main_player':         1.0,
                         'main_player_monitor': 1.0,
                         'preview_player':      1.0,
                         'main_player_monitor_mute': 0.07}
        self.event.start()

    def propagate_volume(self, *a, **kw):
        pass

    def set_volume(self, channel, value):
        self.volumes[channel] = value
        if channel in self.channel_layout:
            self.rpc.remote_call('set_volumes', channels = self.channel_layout[channel], volume = value)
        return True

    def get_volume(self, channel):
        return self.volumes[channel]

    def shutdown(self):
        self.event.stop()
        self.event.join()


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
