import sys
import os
import traceback
from multiprocessing import freeze_support
#from pydjay.core.keyboard import key_map
import gi
import time
#gi.require_version('Gst', '1.0')

#import warnings
# warnings.simplefilter("ignore")
from gi.repository import GLib
#
#from gi.repository import Gst
#from gi.repository import GObject

# sys.path.insert(0, os.path.dirname(__file__))
#
# if __name__ == '__main__':
#     freeze_support()
#     import pydjay.bootstrap_audio_server
from pydjay.backend.command_server import RPCClient

foo = RPCClient(port=9898)
foo.remote_call('preview_play', 'test_file.mp3')
time.sleep(35)

#     #from kivy.base import runTouchApp
#from kivy.core.window import Window
#from kivy.clock import Clock
#from pydjay.core.library import init, save, get_track_by_name, get_tracks
#from kivy.config import Config
#Config.set('kivy', 'exit_on_escape', '0')
#from pydjay.ui.main_screen import MainScreen

#    Window.clearcolor = (0.1, 0.1, 0.1, 1)
#    Window.size = (1728, 1152)

#    init(pydjay.bootstrap.PYDJAY_CACHE)

#    bar = MainScreen(pydjay.bootstrap.main_player,
#                     pydjay.bootstrap.preview_player,
#                     pydjay.bootstrap.volume_control)

#    if not os.path.exists(pydjay.bootstrap.STATE):
#        os.makedirs(pydjay.bootstrap.STATE)
# class RemoteController(RPCClient):
#     def __init__(self, name='PLAYER', port = 9898):
#         RPCClient.__init__(self, name, port)
#
#     def preview_play(self, filename, start_time = None, end_time = None):
#         pydjay.bootstrap_audio_server.preview_player.play(filename, start_time, end_time)
#
#
#     def main_play(self, filename, start_time = None, end_time = None):
#         pydjay.bootstrap_audio_server.main_player.play(filename, start_time, end_time)
#
#
#
# def poll_zmq(*a):
#     print 'idle'
#     return True
# #
# def read_state(dirname, file_name):
#     path = os.path.join(dirname, file_name)
#     queue = []
#     if os.path.exists(path):
#         foo = open(path, 'rU')
#         for location in foo.readlines():
#             track = get_track_by_name(location.rstrip('\n'), True)
#             if track is not None:
#                 queue.append(track)
#     return queue
#
# bar.master_list.set_playlist_title('All songs')
# bar.master_list.display_list(list_=pydjay.bootstrap.get_all_tracks())
#
#     try:
#         event_loop = GLib.MainLoop()
#         GLib.idle_add(poll_zmq)
#         pydjay.bootstrap_audio_server.main_player.start(threaded=True)
#         event_loop.run()
#     except Exception, details:
#         exc_type, exc_value, exc_traceback = sys.exc_info()
#         print '-' * 60
#         traceback.print_exc(file=sys.stdout)
#         print '-' * 60
#         print details
#
#     finally:
#         pass
#         #pydjay.bootstrap.main_player.stop()
#         #pydjay.bootstrap.preview_player.stop()
#
# #        save()
# #        bar.shutdown()
# #        pydjay.bootstrap.close_keyboard()
# #        pydjay.bootstrap.main_player.shutdown()
# #        pydjay.bootstrap.preview_player.shutdown()
# #        pydjay.bootstrap.volume_control.shutdown()
