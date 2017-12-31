from pydjay.core.library import init, load_file, save
import os
import sys
import io
from PIL import Image
import urllib
import array
import cPickle as pickle
from gi.repository import GObject, GLib

from pydjay.core.audio.wavegen import WaveformGenerator
from kivy.clock import mainthread, Clock
from kivy.support import install_gobject_iteration
from kivy.base import EventLoop, runTouchApp
from kivy.uix.label import Label

# install_gobject_iteration()

_root_folder = os.path.abspath(os.path.expanduser('~/.pydjay'))
init(_root_folder)

loop = GLib.MainLoop()

scan_root = sys.argv[1]

timeout_time = 10

if not os.path.exists(scan_root):
    sys.exit(1)


db = {}


def quote(str_, *i):
    bar = str_.replace("/", "-")
    bar = bar.replace(":", "-")
    bar = bar.replace("\"", "-")
    bar = bar.replace("?", "-")
    return bar


def create_thumbnail(track, image, size, type, name):
    new_path = os.path.join(_root_folder, 'image_cache', type + '_' +
                            name  # quote(str(track), "")
                            + ".png")
    if not os.path.exists(new_path):
        image.thumbnail(size, Image.ANTIALIAS)
        image.save(new_path)
    return new_path


files = []


for f in sorted(os.listdir(scan_root)):
    files.append(os.path.join(scan_root, f))


foo = 0
# print f


def load_track(f):
    global foo
    track = load_file(f)
    if track is None:
        return None
    # account for my funny tagging

    #track.metadata._metadata['play_at'] = track.metadata._metadata.get('album_artist', None)
    #track.metadata._metadata['vocal']   = track.metadata._metadata.get('composer', None)
    #track.metadata._metadata['style']   = track.metadata._metadata.get('grouping', None)
    #track.metadata_metadata['speed_feel'] = track.metadata._metadata['']
    #track.metadata_metadata['mood'] = track.metadata._metadata['']

    if track.metadata.album_cover is not None:
        cover = track.metadata.album_cover
        im_type = cover[0]
        im_data = cover[1]
        ext = {'image/jpeg': 'jpg', 'image/png': 'png'}.get(im_type, None)
        if ext is not None:
            data = io.BytesIO(im_data)
            image = Image.open(data)
            cover_art_data = {}
            cover_art_filename = "%s - %s" % (quote(track.metadata.album), quote(track.metadata.artist))
            or_image_path = os.path.join(_root_folder, 'image_cache',
                                         'original_' + cover_art_filename  # quote(str(track), "")
                                         + ".png")
            if not os.path.exists(or_image_path):
                image.save(or_image_path)
            cover_art_data['original'] = or_image_path  # os.path.join(_root_folder, 'image_cache', 'original_'+quote(str(track), "")+".png")
            #image.thumbnail((320,320), Image.ANTIALIAS)
            #image.save(os.path.join('/Users/jihemme/.pydjay/image_cache', 'medium_'+str(track)+".jpg"))
            cover_art_data['medium'] = create_thumbnail(track, image, (320, 320), 'medium', cover_art_filename)
            cover_art_data['small'] = create_thumbnail(track, image, (160, 160), 'small', cover_art_filename)
            cover_art_data['tiny'] = create_thumbnail(track, image, (100, 100), 'tiny', cover_art_filename)

            #os.path.join('/Users/jihemme/.pydjay/image_cache', 'medium_'+str(track)+".jpg")
#            image.thumbnail((160,160), Image.ANTIALIAS)
#            image.save(os.path.join('/Users/jihemme/.pydjay/image_cache', 'small_'+str(track)+".jpg"))
#            cover_art_data['small'] = os.path.join('/Users/jihemme/.pydjay/image_cache', 'small_'+str(track)+".jpg")
#            image.thumbnail((100,100), Image.ANTIALIAS)
#            image.save(os.path.join('/Users/jihemme/.pydjay/image_cache', 'tiny_'+str(track)+".jpg"))
#            cover_art_data['tiny'] = os.path.join('/Users/jihemme/.pydjay/image_cache', 'tiny_'+str(track)+".jpg")
            track.metadata._metadata['album_art'] = cover_art_data
            #im   = CoreImage(data, ext = ext)
            #self._album_art = im
        else:
            print im_type
    else:
        foo += 1

    # print track.metadata.album_cover
    #db[f] = track
    return track


def _next_track(data_points):
    Clock.schedule_once(_do_next_track, 0)
    Clock.unschedule(force_process_next)
    #GLib.timeout_add(50, _do_next_track)


last_time = None


def _print_time(total, time, point):
    global last_time
    global timeout_time
    cur_time = time / 1000000000
    timeout_time = 10
    # print time, total
    # if time > total:
    #    Glib.timeout_add
    if last_time is None or cur_time - last_time > 2:
        printProgress(time, total, "Generating Waveform", "completed")
        last_time = cur_time

# loop.run()


def printProgress(iteration, total, prefix='', suffix='', decimals=0, barLength=20):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        barLength   - Optional  : character length of bar (Int)
    """
    formatStr = "{0:." + str(decimals) + "f}"
    percent = formatStr.format(100 * (iteration / float(total)))
    filledLength = int(round(barLength * iteration / float(total)))
    bar = '+' * filledLength + '-' * (barLength - filledLength)
    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percent, '%', suffix)),
    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()


def force_process_next(*args):
    global timeout_time
    timeout_time -= 1
    if timeout_time <= 0:
        wg.force_stop()


def process_track_queue(*args):
    #global wg
    #global track
    global last_time
    global db
    last_time = None
    while len(files) > 0:
        f = files.pop(0)
        print f
        track = load_track(f)
        try:
            if track is not None:
                # print 'file://' + urllib.quote(os.path.abspath(f))
                path = os.path.join(_root_folder, 'wave_cache', quote(str(track), "") + ".wf")
                if not os.path.exists(path):
                    try:
                        wg = WaveformGenerator(35000)
                        last_time = 0
                        wg.set_data_point_callback(_print_time)
                        wave_points = wg.generate_waveform(f)  # = WaveformGenerator(f, 35000)
                        try:
                            file_ = open(path, 'wb')
                            flat_wave = [num for pair in wave_points for num in pair]
                            file_.write(str(len(flat_wave)) + '\n')
                            arr = array.array('f', flat_wave)
                            arr.tofile(file_)
                            file_.close()
                            track.metadata._metadata['waveform'] = path
                        except Exception, details:
                            print details
                            track.metadata._metadata['waveform'] = None

                        #Clock.schedule_interval(force_process_next, 1)
                    except Exception, details:
                        print details
                        track.metadata._metadata['waveform'] = None
                        #Clock.schedule_once(process_track_queue, 0)
                        # GLib.timeout_add(1,process_track_queue)
                    db[track.location] = track

                else:
                    track.metadata._metadata['waveform'] = path
                    db[track.location] = track
                    #Clock.schedule_once(process_track_queue, 0)

                    #GLib.timeout_add(1, process_track_queue)
        except KeyboardInterrupt:
            track.metadata._metadata['waveform'] = None
            db[track.location] = track

            pass
        # else:
        # process_track_queue()
        #db[track.location] = track
        #Clock.schedule_once(process_track_queue, 0)
        #GLib.timeout_add(1, process_track_queue)

    # else:
    #    loop.quit()
    print foo


# def _do_next_track(*data_points):
#    wave_points = wg.get_data_points()
#    path = os.path.join(_root_folder, 'wave_cache', quote(str(track), "")+".wf")
#    #file_ = open(path, 'w')
#    print path
#    flat_wave = [num for pair in wave_points for num in pair]
#    arr = array.array('f', flat_wave)
#    #print flat_wave[0:10]
#    #print wave[0:5]
#    #file_.close()
#    try:
#        file_ = open(path, 'wb')
#        arr.tofile(file_)
#        file_.close()
#        track.metadata._metadata['waveform'] = path
#    except Exception, details:
#        print details
#        track.metadata._metadata['waveform'] = None
#    db[track.location] = track
#    #GLib.timeout_add(1, process_track_queue)
#
#    Clock.schedule_once(process_track_queue, 0)



#wg = WaveformGenerator(35000)
# wg.set_process_done_callback(_next_track)
# wg.set_data_point_callback(_print_time)
#track = None
#Clock.schedule_once(process_track_queue, 0)
process_track_queue()
#GLib.timeout_add(0, process_track_queue)
#xxx = Label()
# while len(files) > 0:
#    pass
# try:
# runTouchApp(xxx)
# EventLoop.run()
# print 'running main loop'
# loop.run()
# print 'stopped main loop'

if _root_folder is not None:
    foo = open(os.path.join(_root_folder, "library.data"), "w")
    tracks = [(key, db[key].location, db[key].info._metadata, db[key].metadata._metadata) for key in db]
    # print tracks
    pickle.dump(tracks, foo)
    #db = json.dumps(tracks, indent=4)
    # foo.write(db)
    # foo.close()
# save()
