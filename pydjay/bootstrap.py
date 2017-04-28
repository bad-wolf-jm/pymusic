#Core of audio part
#from pydjay.core.audio.player import AudioPlayer
from pydjay.core.audio.volume import VolumeController
from pydjay.core.precue import PreviewPlayer
from pydjay.core.keyboard import key_map

import zmq
import os
import threading
from decoder import GstAudioFile
from output_jack import JackOutput

from kivy.properties import StringProperty, NumericProperty, AliasProperty
from kivy.event import EventDispatcher
from kivy.clock import mainthread, Clock
#from kivy.properties import AliasProperty
from kivy.event import EventDispatcher

class AudioPlayer(EventDispatcher):
    state                = StringProperty(None, allownone = True)
    track_duration       = NumericProperty(None, allownone = True)
    track_position       = NumericProperty(None, allownone = True)
    track_length         = NumericProperty(None, allownone = True)

    def __init__(self, port = 9999, event_port = 5757):
        super(AudioPlayer, self).__init__(*args, **kw)
        self._port = port
        self._event_port = event_port

        self._context        = zmq.Context()
        self._server_socket  = self._context.socket(zmq.REQ)
        self._server_socket.connect("tcp://127.0.0.1:%s" % self._port)

        self._event_handlers = {'end_of_stream':         self.signal_end_of_stream,
                                'track_position_notice': self._set_track_position,
                                'track_duration_notice': self._set_track_duration,
                                'track_length_notice':   self._set_track_length}


        #self._context                = zmq.Context()
        self._event_port             = event_port
        self._event_notifier_running = True
        self._event_socket           = self._context.socket(zmq.PULL)
        self._event_socket.bind("tcp://127.0.0.1:%s" % self._event_port)
        #self._message_queue          = []
        self._event_notifier_thread  = threading.Thread(target = self._event_notifier)
        self._event_notifier_thread.start()
        self.register_event_type("on_end_of_stream")


    def _event_notifier(self):
        while self._event_notifier_running:
            try:
                event = self._event_socket.recv_json()
                callback = self._event_handlers.get(event['type'], None)
                if callback is not None:
                    try:
                        del event['type']
                        callback(**event)
                    except Exception, details:
                        print details
                time.sleep(.05)
            except Exception, details:
                print details
                pass

    def on_end_of_stream(self, *args):
       pass

    @mainthread
    def set_time(self, type_, value):
       setattr(self, type_, value)

    def _set_track_duration(self, value = None):
        self.set_time('track_duration', value)

    def _set_track_position(self, value = None):
        self.set_time('track_duration', value)

    def _set_track_length(self, value = None):
        self.set_time('track_duration', value)

    @mainthread
    def signal_end_of_stream(self, after_time = 0):
        #        def _do(*a):
        #            Clock.unschedule(_keep_setting_time)
        self.dispatch('on_end_of_stream')
        #def _keep_setting_time(*a):
        #    self.track_position = self._output.stream_time
        #Clock.schedule_interval(_keep_setting_time, .1)
        #Clock.schedule_once(_do, float(self._output.buffer_time) / 1000000000)

    def _get_remaining_time(self, *a):
        if self.track_duration is not None and self.track_position is not None:
            return self.track_duration - self.track_position
        return 0

    remaining_time  = AliasProperty(_get_remaining_time, bind = ['track_duration', 'track_position'])

    #def connect_outputs(self, **kwargs):
    #    self._output.connect_outputs(**kwargs)

    #def disconnect_outputs(self, **kwargs):
    #    self._output.disconnect_outputs(**kwargs)

    #def _player_loop(self):
    #    eos = False
    #    has_duration = False
    #    iteration = 0
    #    while self._is_playing:
    #        try:
    #            timestamp, samples = self._decoder.next()
    #            if self._decoder.duration is not None and not has_duration:
    #                has_duration = True
    #                self.set_time('track_duration', self._decoder.duration)
    #                self.set_time('track_length', self._decoder.track_length)
    #            if iteration == 5:
    #                self.set_time('track_position', self._output.stream_time)
    #                iteration = 0
    #            else:
    #                iteration += 1
    #            self._output.send(samples)
    #        except StopIteration:
    #            eos = True
    #            break
    #    self._decoder.close()
    #    self._is_playing = False
    #    self._player_thread = None
    #    if eos:
    #        self.signal_end_of_stream()

    def play(self, filename, start_time = None, end_time = None):
        self._server_socket.send(json.dumps({'name': 'play',
                                                'args': (filename,),
                                                'kwargs':{'start_time': start_time,
                                                          'end_time': end_time}}))
        #self.stop(flush = True)
        #self._file          = filename
        #try:
        #    self._decoder       = GstAudioFile(self._file, self._output.num_channels, self._output.samplerate, 'F32LE', None, start_time, end_time)
        #    if start_time is not None:
        #        self._decoder.set_start_time(start_time)
        #        self._output.reset_timer(start_time)
        #    else:
        #        self._output.reset_timer(0)
        #    self._player_thread = threading.Thread(target = self._player_loop)
        #    self._is_playing    = True
        #    self._player_thread.start()
        #    self.state = "playing"
        #except IOError:
        #    self.state = 'stopped'
        #except Exception, details:
        #    print details
        #    self.state = 'stopped'
        ##    raise

    def stop(self, flush = False):
        self._server_socket.send(json.dumps({'name': 'stop',
                                                'args': (,),
                                                'kwargs':{'flush': flush}}))
        #self._is_playing = False
        #if flush:
        #    self._output.flush_buffer()
        #self._output.reset_timer()
        #if self._player_thread is not None:
        #    self._player_thread.join()
        #self._player_thread = None
        #self._decoder       = None
        #self.track_duration = None
        #self.track_length   = None
        ##self.track_position = None
        #self.state          = "stopped"

    def pause(self):
        self.state = "paused"

    def seek(self, timestamp):
        self._server_socket.send(json.dumps({'name': 'seek',
                                                'args': (timestamp,),
                                                'kwargs':{}}))
        #if self._decoder is not None:
        #    self._decoder.seek(timestamp)
        #    self._output.reset_timer(timestamp)
        #    self._output.flush_buffer()

    def seek_relative(self, time):
        self._server_socket.send(json.dumps({'name': 'seek_relative',
                                                        'args': (time,),
                                                        'kwargs':{}}))
        #if self._is_playing:
        #    p = self.track_position
        #    if p is not None:
        #        d = self.track_duration
        #        if d is not None:
        ##            p = max(min(p, d), 0)
#                    self.seek(p)
#
    #@property
    #def is_playing(self):
    #    return self.state == 'playing'

    #def shutdown(self):
    #    self.stop()
    #    self._output.close()





main_player      = AudioPlayer(port = 9999, event_port = 5557) #AudioPlayer("MainPlayer", 2)
preview_player_o = AudioPlayer(port = 9998, event_port = 5556) #AudioPlayer("PreviewPlayer", 2)
#volume_control_o = VolumeController("VolumeControl", num_channels = 6)
#preview_volume_control = VolumeController("PrecuePlayerVolume")

#preview_player_o.connect_outputs(output_1 = "VolumeControl:input_5",
#                                 output_2 = "VolumeControl:input_6")

#preview_volume_control.connect_outputs(output_1 = "system:playback_5",
#                                       output_2 = "system:playback_6")
#main_player.connect_outputs(output_1 = "VolumeControl:input_1",
#                            output_2 = "VolumeControl:input_2")

#main_player.connect_outputs(output_1 = "VolumeControl:input_3",
#                            output_2 = "VolumeControl:input_4")

#volume_control_o.connect_outputs(output_1 = "system:playback_1",
#                                 output_2 = "system:playback_2",
#                                 output_3 = "system:playback_5",
#                                 output_4 = "system:playback_6",
#                                 output_5 = "system:playback_5",
#                                 output_6 = "system:playback_6")


class VolumeControl(EventDispatcher):
    def __init__(self, port = 9997, event_port = 5555):
        super(VolumeControl, self).__init__()
        self._port = port
        self._event_port = event_port

        self.channel_layout =  {'main_player':         [1,2],
                                'main_player_monitor': [3,4],
                                'preview_player':      [5,6]}
        self.volumes =  {'main_player':         1.0,
                         'main_player_monitor': 1.0,
                         'preview_player':      1.0,
                         'main_player_monitor_mute': 0.07}
        self.controller = volume_control_o
        self._context        = zmq.Context()
        self._server_socket  = self._context.socket(zmq.REQ)
        self._server_socket.connect("tcp://127.0.0.1:%s" % self._port)
        self._event_handlers = {'volume_set':         self.propagate_volume}
        self._event_notifier_running = True
        self._event_socket           = self._context.socket(zmq.PULL)
        self._event_socket.bind("tcp://127.0.0.1:%s" % self._event_port)
        self._event_notifier_thread  = threading.Thread(target = self._event_notifier)
        self._event_notifier_thread.start()

    def _event_notifier(self):
        while self._event_notifier_running:
            try:
                event = self._event_socket.recv_json()
                callback = self._event_handlers.get(event['type'], None)
                if callback is not None:
                    try:
                        del event['type']
                        callback(**event)
                    except Exception, details:
                        print details
                time.sleep(.05)
            except Exception, details:
                print details
                pass

    def propagate_volume(self, *a):
        pass

    def set_volume(self, channel, value):
        self.volumes[channel] = value
        if channel in self.channel_layout:
            self._server_socket.send(json.dumps({'name': 'set_volumes',
                                                 'args' (,),
                                                 'kwargs': dict(channels = self.channel_layout[channel], value = value)}))
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
