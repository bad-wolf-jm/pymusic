import sys
import os
import traceback
from multiprocessing import freeze_support
from pydjay.core.keyboard import key_map

sys.path.insert(0, os.path.dirname(__file__))

if __name__ == '__main__':
    freeze_support()
    import pydjay.bootstrap
    from kivy.base import runTouchApp
    from kivy.core.window import Window
    from kivy.clock import Clock
    from pydjay.core.library import init, save, get_track_by_name, get_tracks

    from pydjay.ui.main_screen import MainScreen

    Window.clearcolor = (0.1,0.1,0.1, 1)
    Window.size = (1728,1152)

    init(pydjay.bootstrap.PYDJAY_CACHE)

    bar = MainScreen(pydjay.bootstrap.main_player,
                     pydjay.bootstrap.preview_player,
                     pydjay.bootstrap.volume_control)

    if not os.path.exists(pydjay.bootstrap.STATE):
        os.makedirs(pydjay.bootstrap.STATE)


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

    queue = read_state(pydjay.bootstrap.STATE, 'queue.txt')
    pydjay.bootstrap.play_queue.set_track_list(queue)
    #bar.master_queue.set_track_list(queue)

    queue = read_state(pydjay.bootstrap.SESSIONS, 'Current Session.m3u')
    pydjay.bootstrap.session_manager.set_current_session(queue)
    #bar.master_queue.deck.set_current_session(queue)
    #bar.master_queue.deck.current_session_list.set_track_list(queue)

    bar.master_list.set_playlist_title('TRACKS')
    bar.master_list.set_track_list(get_tracks())

    queue = read_state(pydjay.bootstrap.STATE, 'shortlist.txt')
    bar.short_list.set_track_list(queue)

    try:
        key_map.bind(on_cycle_focus = bar.cycle_focus)
        runTouchApp(bar)
    except Exception, details:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print '-'*60
        traceback.print_exc(file=sys.stdout)
        print '-'*60
        print details

    finally:
        pydjay.bootstrap.main_player.stop()
        pydjay.bootstrap.preview_player.stop()

        foo = open(os.path.join(pydjay.bootstrap.STATE, 'queue.txt'), 'w')
        for track in bar.master_queue.queue_view.adapter.data:
            if track['item'].track.location is not None:
                foo.write(track['item'].track.location + '\n')
        foo.close()


        foo = open(os.path.join(pydjay.bootstrap.STATE, 'shortlist.txt'), 'w')
        for track in bar.short_list.short_list.adapter.data:
            if track['item'].track.location is not None:
                foo.write(track['item'].track.location + '\n')
        foo.close()
        save()
        bar.shutdown()
        #print 'FOOBAR 1'
        pydjay.bootstrap.close_keyboard()
        #print 'FOOBAR 2'
        pydjay.bootstrap.main_player.shutdown()
        #print 'FOOBAR 3'
        pydjay.bootstrap.preview_player.shutdown()
        #print 'FOOBAR 4'
        pydjay.bootstrap.volume_control.shutdown()
