# import zmq
# import threading

from pydjay.core.audio.volume import VolumeController
from pydjay.backend.command_server import RPCServer  # , PushServer
from pydjay.backend.push_server import PushServer


class VolumeControlServer(VolumeController, RPCServer):
    def __init__(self, name='VolumeControl', num_channels=2, port=9997, event_port=5555):
        RPCServer.__init__(self, name, port)
        VolumeController.__init__(self, name, num_channels)
        self.event = PushServer(name, event_port)
        self.event.start()

    def set_volumes(self, channels, volume):
        VolumeController.set_volumes(self, channels=channels, value=volume)
        self.event.push('volume_set_notice', channels=channels, value=volume)


if __name__ == '__main__':

    c = VolumeControlServer('VolumeControl', num_channels=6)
    c.connect_outputs(output_1="system:playback_1",
                      output_2="system:playback_2",
                      output_3="system:playback_5",
                      output_4="system:playback_6",
                      output_5="system:playback_5",
                      output_6="system:playback_6")

    c.start(threaded=False)
