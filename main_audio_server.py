import sys
import os
import traceback
from multiprocessing import freeze_support
import gi
from gi.repository import GLib

sys.path.insert(0, os.path.dirname(__file__))

if __name__ == '__main__':
    freeze_support()
    import pydjay.bootstrap_audio_server
    from pydjay.backend.command_server import RPCServer

    class RemoteController(RPCServer):
        def __init__(self, name='PLAYER', port=9898):
            RPCServer.__init__(self, name, port)

        def preview_play(self, filename, start_time=None, end_time=None):
            pydjay.bootstrap_audio_server.preview_player.play(filename, start_time, end_time)

        def preview_stop(self):
            pydjay.bootstrap_audio_server.preview_player.stop()

        def preview_pause(self):
            pydjay.bootstrap_audio_server.preview_player.pause()

        def main_play(self, filename, start_time=None, end_time=None):
            pydjay.bootstrap_audio_server.main_player.play(filename, start_time, end_time)

    poll_zmq = RemoteController()

    try:
        event_loop = GLib.MainLoop()
        poll_zmq.start(threaded=True)
        pydjay.bootstrap_audio_server.main_player.start(threaded=True)
        event_loop.run()
    except Exception, details:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print '-' * 60
        traceback.print_exc(file=sys.stdout)
        print '-' * 60
        print details

    finally:
        pass
