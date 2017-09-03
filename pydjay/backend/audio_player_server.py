# import zmq
# import threading


from pydjay.backend.command_server import RPCServer
from pydjay.backend.push_server import PushServer
from pydjay.core.audio.audio_player_base import AudioPlayer


class AudioServer(AudioPlayer, RPCServer):
    """An RPC server for the audio player class"""

    def __init__(self, player_name=None, num_channels=2, port=9999, event_port=5557):
        RPCServer.__init__(self, player_name, port)
        AudioPlayer.__init__(self, player_name, num_channels)
        self.event = PushServer(player_name, event_port)
        self.event.start()

    def on_end_of_stream(self):
        AudioPlayer.on_end_of_stream(self, value)
        self.event.push('end_of_stream')

    def on_track_position(self, value):
        AudioPlayer.on_track_position(self, value)
        self.event.push('track_position_notice', value)

    def on_track_duration(self, value):
        AudioPlayer.on_track_duration(self, value)
        self.event.push('track_duration_notice', value)

    def on_track_length(self, value):
        AudioPlayer.on_track_length(self, value)
        self.event.push('track_length_notice', value)
