#import runpy
import sys
import os
import traceback
import threading
from multiprocessing import freeze_support
#from jmc.gui import config
from pydjay.utils import tmpfile
from pydjay.core.keyboard import key_map
#import kivy

sys.path.insert(0, os.path.dirname(__file__))

if __name__ == '__main__':
    freeze_support()
    import pydjay.bootstrap

    """
    from pydjay.audio.player.player import AudioPlayer
    from pydjay.audio.player.volume import VolumeController
    main_player    = AudioPlayer("MainPlayer", 2)
    preview_player = AudioPlayer("PreviewPlayer", 2)
    volume_control_o = VolumeController("VolumeControl", num_channels = 6)
    #preview_volume_control = VolumeController("PrecuePlayerVolume")

    preview_player.connect_outputs(output_1 = "VolumeControl:input_5",
                                   output_2 = "VolumeControl:input_6")

    #preview_volume_control.connect_outputs(output_1 = "system:playback_5",
    #                                       output_2 = "system:playback_6")
    main_player.connect_outputs(output_1 = "VolumeControl:input_1",
                                output_2 = "VolumeControl:input_2")
    main_player.connect_outputs(output_1 = "VolumeControl:input_3",
                                output_2 = "VolumeControl:input_4")
    volume_control_o.connect_outputs(output_1 = "system:playback_1",
                                   output_2 = "system:playback_2",
                                   output_3 = "system:playback_5",
                                   output_4 = "system:playback_6",
                                   output_5 = "system:playback_5",
                                   output_6 = "system:playback_6")


    class VolumeControl:
        def __init__(self):
            self.channel_layout =  {'main_player':         [1,2],
                                    'main_player_monitor': [3,4],
                                    'preview_player':      [5,6]}
            self.volumes =  {'main_player':         1.0,
                             'main_player_monitor': 1.0,
                             'preview_player':      1.0,
                             'main_player_monitor_mute': 0.07}
            self.controller = volume_control_o


        def set_volume(self, channel, value):
            self.volumes[channel] = value
            if channel in self.channel_layout:
                self.controller.set_volumes(channels = self.channel_layout[channel], value = value)

        def get_volume(self, channel):
            return self.volumes[channel]

    volume_control = VolumeControl()
    volume_control.set_volume('main_player', 1.0)
    volume_control.set_volume('main_player_monitor', 1.0)
    volume_control.set_volume('preview_player', 1.0)
    volume_control.set_volume('main_player_monitor_mute', .07)
    """        
    from kivy.base import runTouchApp
    from kivy.core.window import Window
    from kivy.clock import Clock
    from kivy.uix.button import Button
    from kivy.config import Config
    from pydjay.library import load_file
    from pydjay.library import init, save, get_track_by_name, save_current_session

    from pydjay.gui.modules.main_screen import MainScreen
    #import multiprocessing as mp

    #def key(*args):
    #    print args

    
    #mp.set_start_method('spawn')
    Config.set('graphics', 'width', '1200')
    Config.set('graphics', 'height', '720')
    Window.clearcolor = (0.1,0.1,0.1, 1)
    Window.size = (1728,1152)
    #Window.bind(on_keyboard = key)
    


    HOME         = os.path.expanduser('~')
    PYDJAY_CACHE = os.path.join(HOME, '.pydjay')

    init(PYDJAY_CACHE)

    bar = MainScreen(pydjay.bootstrap.main_player,
                     pydjay.bootstrap.preview_player,
                     pydjay.bootstrap.volume_control)
    #bar.main_player.queue = bar.master_queue
    #bar.master_list.queue = bar.master_queue
    #bar.master_list.main_player = bar.main_player
    #bar.master_list.short_list.window = bar


    STATE    = os.path.join(PYDJAY_CACHE, 'state')
    SESSIONS = os.path.join(PYDJAY_CACHE, 'sessions')
    
    if not os.path.exists(STATE):
        os.makedirs(STATE)
    if os.path.exists(os.path.join(STATE, 'queue.txt')):
        foo = open(os.path.join(STATE, 'queue.txt'), 'rU')
        queue = []
        for location in foo.readlines():
            track = get_track_by_name(location.rstrip('\n'), True)
            if track is not None:
                queue.append(track)
        print queue
        bar.master_queue.set_track_list(queue)

    if os.path.exists(os.path.join(STATE, 'main_list.txt')):
        foo = open(os.path.join(STATE, 'main_list.txt'), 'rU')
        queue = []
        title = foo.readline().rstrip('\n')
        for location in foo.readlines():
            track = get_track_by_name(location.rstrip('\n'), True)
            if track is not None:
                queue.append(track)
        #print queue
        bar.master_list.set_playlist_title(title)
        bar.master_list.set_track_list(queue)

        
    if os.path.exists(os.path.join(STATE, 'shortlist.txt')):
        foo = open(os.path.join(STATE, 'shortlist.txt'), 'rU')
        queue = []
        for location in foo.readlines():
            track = get_track_by_name(location.rstrip('\n'), True)
            if track is not None:
                queue.append(track)
        #print queue
        bar.short_list.set_track_list(queue)
        #bar.master_list.update_labels()
    
    if os.path.exists(os.path.join(SESSIONS, 'Current Session.m3u')):
        foo = open(os.path.join(SESSIONS, 'Current Session.m3u'), 'rU')
        queue = []
        for location in foo.readlines():
            queue.append(location.rstrip('\n'))
            #track = get_track_by_name(location.rstrip('\n'), True)
            #if track is not None:
            #    queue.append(track)
        #print queue
        bar.master_queue.deck.set_current_session(queue)
        #bar.master_list.update_labels()

    #print "XXX"
    try:
        #bar.master_list._show_library()
        key_map.bind(on_cycle_focus = bar.cycle_focus)
        #bar.master_queue.set_player(bar.master_queue.deck)
        runTouchApp(bar)
        #print Window.size
    except Exception, details:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print '-'*60
        traceback.print_exc(file=sys.stdout)
        print '-'*60
        print details
        
    finally:
        pydjay.bootstrap.main_player.stop()
        pydjay.bootstrap.preview_player.stop()
        
        foo = open(os.path.join(STATE, 'queue.txt'), 'w')
        for track in bar.master_queue.queue_view.adapter.data:
            if track['item'].track.location is not None:
                foo.write(track['item'].track.location + '\n')
        foo.close()


        foo = open(os.path.join(STATE, 'shortlist.txt'), 'w')
        for track in bar.short_list.short_list.adapter.data:
            if track['item'].track.location is not None:
                foo.write(track['item'].track.location + '\n')
        foo.close()
        
        foo = open(os.path.join(STATE, 'main_list.txt'), 'w')
        foo.write(bar.master_list.playlist_title + '\n')
        for track in bar.master_list.master_list.get_full_track_list():
            if track.location is not None:
                foo.write(track.location + '\n')
        foo.close()
        
        save_current_session()
        save()
        #os._exit(0)
        
        bar.shutdown()
        pydjay.bootstrap.close_keyboard()
        pydjay.bootstrap.main_player.shutdown()
        pydjay.bootstrap.preview_player.shutdown()
        pydjay.bootstrap.volume_control_o.close()
        #preview_volume_control.close()
        #os._exit(0)

        print threading.enumerate()

#runpy.run_module(sys.argv[1], run_name = "__main__")

#tmpfile.cleanup()
#runpy.run_module('pydjay.gui.main_screen', run_name = "__main__")

#runpy.run_module('pydjay.gui.main_player_deck', run_name = "__main__")
#runpy.run_module('pydjay.gui.master_list', run_name = "__main__")
#runpy.run_module('pydjay.gui.master_queue', run_name = "__main__")


#runpy.run_module('jmc.gui.media_player.player', run_name = "__main__")
