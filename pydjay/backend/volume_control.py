import zmq
import threading

from pydjay.core.audio.volume import VolumeController
from pydjay.backend.command_server import RPCServer#, PushServer

class VolumeControlServer(VolumeController, RPCServer):
    def __init__(self, name = 'VolumeControl', num_channels = 2, port = 9997, event_port = 5555):
        RPCServer.__init__(self, name, port)
        VolumeController.__init__(self, name, num_channels)
        self._context                = zmq.Context()
        self._event_port             = event_port
        self._event_notifier_running = True
        self._event_socket           = self._context.socket(zmq.PUSH)
        self._event_socket.bind("tcp://127.0.0.1:%s" % self._event_port)
        self._message_queue          = []
        self._event_notifier_thread  = threading.Thread(target = self._event_notifier)
        self._event_notifier_thread.start()

    def _event_notifier(self):
        while self._event_notifier_running:
            while len(self._message_queue) > 0:
                try:
                    event = self._message_queue.pop(0)
                    self._event_socket.send_json(event)
                    time.sleep(.05)
                except:
                    pass

    def set_volumes(self, channels, volume):
        VolumeController.set_volumes(self, channels = channels, value = volume)
        self._message_queue = [x for x in self._message_queue if x['type'] != 'volume_set_notice']
        self._message_queue.append({'type': 'volume_set',
                                    'channels': channels,
                                    'value': value})


if __name__ == '__main__':
    c = VolumeControlServer('VolumeControl', num_channels = 6)
    c.connect_outputs(output_1 = "system:playback_1",
                    output_2 = "system:playback_2",
                    output_3 = "system:playback_5",
                    output_4 = "system:playback_6",
                    output_5 = "system:playback_5",
                    output_6 = "system:playback_6")
    c.start(threaded = False)
