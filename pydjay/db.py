import sys
import os
import traceback
import zmq
import json
import time

#from multiprocessing import freeze_support
#from pydjay.core.keyboard import key_map

sys.path.insert(0, os.path.dirname(__file__))

if __name__ == '__main__':
    #freeze_support()
    #import pydjay.bootstrap
    #from kivy.base import runTouchApp
    #from kivy.core.window import Window
    #from kivy.clock import Clock
    from core.library import init, save, get_track_by_name, get_tracks

    #from pydjay.ui.main_screen import MainScreen

    ##Window.clearcolor = (0.1,0.1,0.1, 1)
    #Window.size = (1728,1152)
    HOME         = os.path.expanduser('~')
    PYDJAY_CACHE = os.path.join(HOME, '.pydjay')
    STATE        = os.path.join(PYDJAY_CACHE, 'state')
    SESSIONS     = os.path.join(PYDJAY_CACHE, 'sessions')
    PLAYLISTS    = os.path.join(PYDJAY_CACHE, 'playlists')

    init(PYDJAY_CACHE)

    #bar = MainScreen(pydjay.bootstrap.main_player,
#                     pydjay.bootstrap.preview_player,
#                     pydjay.bootstrap.volume_control)

#    if not os.path.exists(pydjay.bootstrap.STATE):
#        os.makedirs(pydjay.bootstrap.STATE)


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

    queue           = read_state(STATE, 'queue.txt')
    current_session = read_state(SESSIONS, 'Current Session.m3u')
    short_list      = read_state(STATE, 'shortlist.txt')
#    bar.short_list.set_track_list(queue)

    try:

        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://127.0.0.1:%s" % 9999)

        while True:
            #  Wait for next request from client
            message = socket.recv()
            print message, type(message)
            message = json.loads(message)

            command = message['command']
            print command



            print "Received request: ", command
            #time.sleep (1)

            if command == 'get_tracks':
                ll = get_tracks()
                send = [x.metadata._metadata for x in ll]
                socket.send(json.dumps(send))


#        key_map.bind(on_cycle_focus = bar.cycle_focus)
#        runTouchApp(bar)
    except Exception, details:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print '-'*60
        traceback.print_exc(file=sys.stdout)
        print '-'*60
        print details

    finally:
#        pydjay.bootstrap.main_player.stop()
#        pydjay.bootstrap.preview_player.stop()

        foo = open(os.path.join(STATE, 'queue.txt'), 'w')
        #for track in bar.master_queue.queue_view.adapter.data:
        #    if track['item'].track.location is not None:
        #        foo.write(track['item'].track.location + '\n')
        foo.close()


        foo = open(os.path.join(STATE, 'shortlist.txt'), 'w')
        #for track in bar.short_list.short_list.adapter.data:
        #    if track['item'].track.location is not None:
        #        foo.write(track['item'].track.location + '\n')
        foo.close()
        save()
#        bar.shutdown()
#        pydjay.bootstrap.close_keyboard()
#        pydjay.bootstrap.main_player.shutdown()
#        pydjay.bootstrap.preview_player.shutdown()
#        pydjay.bootstrap.volume_control_o.close()
