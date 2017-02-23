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
    from kivy.base import runTouchApp
    from kivy.core.window import Window
    from kivy.clock import Clock
    #from kivy.uix.button import Button
    #from kivy.config import Config
    #from pydjay.library import load_file
    from pydjay.library import init, save, get_track_by_name, get_tracks

    from pydjay.gui.modules.main_screen import MainScreen
    #import multiprocessing as mp

    #def key(*args):
    #    print args

    
    #mp.set_start_method('spawn')
    #Config.set('graphics', 'width', '1200')
    #Config.set('graphics', 'height', '720')
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


    def read_state(dirname, file_name):
        path = os.path.join(dirname, file_name)
        queue = []
        if os.path.exists(path):
            foo = open(path, 'rU')
            for location in foo.readlines():
                track = get_track_by_name(location.rstrip('\n'), True)
                if track is not None:
                    queue.append(track)
        return queue
                #else:
           # return []
        #print queue


    queue = read_state(STATE, 'queue.txt')
    bar.master_queue.set_track_list(queue)

    queue = read_state(SESSIONS, 'Current Session.m3u')
    bar.master_queue.deck.set_current_session(queue)
    bar.master_queue.deck.current_session_list.set_track_list(queue)
    
    #if os.path.exists(os.path.join(STATE, 'queue.txt')):
    #    foo = open(os.path.join(STATE, 'queue.txt'), 'rU')
    #    queue = []
    #    for location in foo.readlines():
    #        track = get_track_by_name(location.rstrip('\n'), True)
    #        if track is not None:
    #            queue.append(track)
    #    #print queue
    #    bar.master_queue.set_track_list(queue)

    #if os.path.exists(os.path.join(STATE, 'main_list.txt')):
    #    foo = open(os.path.join(STATE, 'main_list.txt'), 'rU')
    #    queue = []
    #    title = foo.readline().rstrip('\n')
    #    for location in foo.readlines():
    #        track = get_track_by_name(location.rstrip('\n'), True)
    #        if track is not None:
    #            queue.append(track)
    #    #print queue
    bar.master_list.set_playlist_title('TRACKS')
    bar.master_list.set_track_list(get_tracks())

    queue = read_state(STATE, 'shortlist.txt')
    bar.short_list.set_track_list(queue)
    
    #if os.path.exists(os.path.join(STATE, 'shortlist.txt')):
    #    foo = open(os.path.join(STATE, 'shortlist.txt'), 'rU')
    #    queue = []
    #    for location in foo.readlines():
    #        track = get_track_by_name(location.rstrip('\n'), True)
    #        if track is not None:
    #            queue.append(track)
    #    #print queue
    #    bar.short_list.set_track_list(queue)
    #    #bar.master_list.update_labels()


    #bar.master_queue.deck.dispatch("on_unavailable_added")
    
    
    #if os.path.exists(os.path.join(SESSIONS, 'Current Session.m3u')):
    #    foo = open(os.path.join(SESSIONS, 'Current Session.m3u'), 'rU')
    #    queue = []
    #    for location in foo.readlines():
    #        queue.append(location.rstrip('\n'))
    #        #track = get_track_by_name(location.rstrip('\n'), True)
    #        #if track is not None:
    #        #    queue.append(track)
    #    #print queue
    #    bar.master_queue.deck.set_current_session(queue)
    #    #bar.master_list.update_labels()

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
        
        #foo = open(os.path.join(STATE, 'main_list.txt'), 'w')
        #foo.write(bar.master_list.playlist_title + '\n')
        #for track in bar.master_list.master_list.get_full_track_list():
        #    if track.location is not None:
        #        foo.write(track.location + '\n')
        #foo.close()
        
        #save_current_session()
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
