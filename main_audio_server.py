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

    main_player_channels = [1, 2]
    precue_player_channels = [5, 6]
    monitor_channels = [3, 4]

    main_volume = 1.0
    monitor_volume = 1.0
    precue_volume = 1.0

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

        def main_stop(self):
            pydjay.bootstrap_audio_server.main_player.stop()

        def set_main_player_volume(self, value):
            pydjay.bootstrap_audio_server.volume_control.set_volumes(channels=main_player_channels, volume=value)

        def set_precue_player_volume(self, value):
            pydjay.bootstrap_audio_server.volume_control.set_volumes(channels=precue_player_channels, volume=value)

        def set_monitor_volume(self, value):
            pydjay.bootstrap_audio_server.volume_control.set_volumes(channels=monitor_channels, volume=value)

        def increase_main_player_volume(self, *a):
            global main_volume
            main_volume += .01
            main_volume = min(main_volume, 4)
            self.set_main_player_volume(main_volume)

        def decrease_main_player_volume(self, *a):
            global main_volume
            main_volume -= .01
            main_volume = max(main_volume, 0)
            self.set_main_player_volume(main_volume)

        def increase_monitor_volume(self, *a):
            global monitor_volume
            monitor_volume += .01
            monitor_volume = min(monitor_volume, 4)
            self.set_monitor_volume(monitor_volume)

        def decrease_monitor_volume(self, *a):
            global monitor_volume
            monitor_volume -= .01
            monitor_volume = max(monitor_volume, 0)
            self.set_monitor_volume(monitor_volume)

        def increase_precue_player_volume(self, *a):
            global precue_volume
            precue_volume += .01
            precue_volume = min(precue_volume, 4)
            self.set_precue_player_volume(precue_volume)

        def decrease_precue_player_volume(self, *a):
            global precue_volume
            precue_volume -= .01
            precue_volume = max(precue_volume, 0)
            self.set_precue_player_volume(precue_volume)

        def preview_seek(self, t):
            t *= 1000000000
            pydjay.bootstrap_audio_server.preview_player.seek_relative(t)

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
