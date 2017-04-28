import zmq
import threading


from pydjay.backend.command_server import RPCServer, PushServer
from pydjay.core.audio.audio_player_base import AudioPlayer
#from pydjay.core.audio.volume import VolumeController
#from pydjay.core.precue import PreviewPlayer

class AudioServer(AudioPlayer, RPCServer):
    """An RPC server for the audio player class"""
    def __init__(self, player_name = None, num_channels = 2, port = 9999, event_port = 5557):
        #print 'CCC3'
        RPCServer.__init__(self, player_name, port)
        #print 'CCC'
        AudioPlayer.__init__(self, player_name, num_channels)
        #super(AudioServer, self).__init__(player_name = player_name, num_channels = num_channels, port = port)
        #print 'CCC'

        self._event_port             = event_port
        self._context        = zmq.Context()
        self._event_socket   = self._context.socket(zmq.PUSH)
        self._event_socket.bind("tcp://127.0.0.1:%s" % self._event_port)
        self._event_notifier_running = True
        self._message_queue          = []
        self._event_notifier_thread  = threading.Thread(target = self._event_notifier)
        self._event_notifier_thread.start()

    def on_eos(self):
        self._last_position = None
        self._message_queue.append({'type': 'eof_of_stream'})

    def on_track_position(self, value):
        self._message_queue = [x for x in self._message_queue if x['type'] != 'track_position_notice']
        self._message_queue.append({'type': 'track_position_notice',
                                    'value': value})
        self._last_position = value

    def on_track_duration(self, value):
        self._message_queue = [x for x in self._message_queue if x['type'] != 'track_duration_notice']
        self._message_queue.append({'type': 'track_duration_notice',
                                    'value': value})

    def on_track_length(self, value):
        self._message_queue = [x for x in self._message_queue if x['type'] != 'track_length_notice']
        self._message_queue.append({'type': 'track_length_notice',
                                    'value': value})

    def _event_notifier(self):
        while self._event_notifier_running:
            while len(self._message_queue) > 0:
                try:
                    event = self._message_queue.pop(0)
                    self._event_socket.send_json(event)
                    time.sleep(.05)
                except:
                    pass


#if __name__ == '__main__':
#    main_player = AudioServer("MainPlayer", 2)
#    main_player.connect_outputs(output_1 = "system:playback_1",
#                                output_2 = "system:playback_2")
#    main_player.start(threaded = False)
