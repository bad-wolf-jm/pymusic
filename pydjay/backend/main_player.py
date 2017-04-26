import zmq

from pydjay.backend.command_server import RPCServer, PushServer
from pydjay.core.audio.audio_player_base import AudioPlayer
from pydjay.core.audio.volume import VolumeController
from pydjay.core.precue import PreviewPlayer

class AudioServer(AudioPlayer, RPCServer):
    """An RPC server for the audio player class"""
    def __init__(self, player_name = None, num_channels = 2, port = 9999):
        super(AudioServer, self).__init__(player_name = player_name, num_channels = num_channels, port = port)
        self._push = PushServer(port = 5557)
        self.register_callback('on_end_of_stream', self._eos)
        self.register_callback("track_position", self._position_notice)
        self.register_callback("track_duration", self._duration_notice)
        self.register_callback("track_length", self._length_notice)
        self._push.start()
        self._last_position = None

    def _eos(self):
        self._last_position = None
        self._event_stream_socket.send_json({'type': 'eof_of_stream'})

    def _position_notice(self, value):
        if self._last_position is None or (value - self._last_position) > 100000000:
            self._push.push({'type': 'track_position_notice',
                            'value': value})
            self._last_position = value

    def _duration_notice(self, value):
        self._push.push({'type': 'track_duration_notice',
                        'value': value})

    def _length_notice(self, value):
        self._push.push({'type': 'track_length_notice',
                        'value': value})



if __name__ == '__main__':
    main_player = AudioServer("MainPlayer", 2)
    main_player.connect_outputs(output_1 = "system:playback_1",
                                output_2 = "system:playback_2")
    main_player.start(threaded = False)
