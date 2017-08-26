from pydjay.core.library import init, load_file, save
import os
import sys
import io
from PIL import Image
import urllib
import array
#import cPickle as pickle
from gi.repository import GObject, GLib

from pydjay.core.audio.wavegen import WaveformGenerator
from kivy.clock import mainthread, Clock
from kivy.support import install_gobject_iteration
from kivy.base import EventLoop, runTouchApp
from kivy.uix.label import Label
import pymysql
from mp3hash import mp3hash

# install_gobject_iteration()

connection = pymysql.connect(host="localhost",
                             user='root',
                             password='root',
                             db='pymusic',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

insert_track_sql = u"""
INSERT INTO tracks (
-- id,
title, artist, album, year, genre, style, bpm, rating, favorite, comments, last_played, waveform,
cover_medium, cover_small, cover_large, cover_original, track_length, stream_start, stream_end, stream_length,
date_added, date_modified, bitrate, samplerate, file_name, file_size, hash, play_at, kind, category, description
)
VALUES (
-- {id},
{title}, {artist}, {album}, {year}, {genre}, {style}, {bpm}, {rating}, {favorite}, {comments},
{last_played}, {waveform}, {cover_medium}, {cover_small}, {cover_large}, {cover_original}, {track_length},
{stream_start}, {stream_end}, {stream_length}, {date_added}, {date_modified}, {bitrate}, {samplerate},
{file_name}, {file_size}, {hash}, {play_at}, {kind}, {category}, {description}
)
"""


_root_folder = os.path.abspath(os.path.expanduser('~/.pydjay'))
# init(_root_folder)

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


def addslashes(s):
    if s == None:
        return u'NULL'
    d = {u'"': u'\\"',
         u"'": u"\\'",
         u"\0": u"\\\0",
         u"\\": u"\\\\"}
    return u''.join([d.get(c, c) for c in s])


def none_to_null(v):
    return v if v is not None else u'NULL'

#    if s == None:
#        return ''
#    d = {'"': '\\"', "'": "\\'", "\0": "\\\0", "\\": "\\\\"}
#    return u''.join(d.get(c, c) for c in s)


foo = 0
# print f


def load_track(f):
    global foo
    track = load_file(f)
    if track is None:
        return None
    cover_art_data = {'original': None, 'tiny': None, 'small': None, 'medium': None}
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
            cover_art_data['original'] = or_image_path
            cover_art_data['medium'] = create_thumbnail(track, image, (320, 320), 'medium', cover_art_filename)
            cover_art_data['small'] = create_thumbnail(track, image, (160, 160), 'small', cover_art_filename)
            cover_art_data['tiny'] = create_thumbnail(track, image, (100, 100), 'tiny', cover_art_filename)
            track.metadata._metadata['album_art'] = cover_art_data
    else:
        foo += 1

    stat = os.stat(f)
    file_size = stat.st_size
    #access_time = stat.st_atime
    #modified_time = stat.st_mtime
    #created_time = stat.st_ctime

    print stat


#    print mp3hash(f), len(mp3hash(f))
    return {
        'id': None,
        'title': track.metadata.title,
        'artist': track.metadata.artist,
        'album': track.metadata.album,
        'year': track.metadata.year,
        'genre': track.metadata.genre,
        'style': track.metadata.style,
        'bpm': track.metadata.bpm,
        'rating': track.metadata.rating,
        'favorite': track.metadata.loved,
        'comments': track.metadata.comments,
        'last_played': None,
        'waveform': None,
        'cover_medium': cover_art_data['small'],
        'cover_small': cover_art_data['tiny'],
        'cover_large': cover_art_data['medium'],
        'cover_original': cover_art_data['original'],
        'track_length': track.info.stream_length,
        'stream_start': 0,
        'stream_end': track.info.stream_length,
        'stream_length': track.info.stream_length,
        'date_added': None,
        'date_modified': None,
        'bitrate': track.info.bitrate,
        'samplerate': track.info.samplerate,
        'file_name': f.decode('utf8'),
        'file_size': file_size,
        'hash': mp3hash(f),
        'play_at':None,
        'kind':None,
        'category': None,
        'description': None
    }


def _next_track(data_points):
    Clock.schedule_once(_do_next_track, 0)
    Clock.unschedule(force_process_next)


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


def STRING(v):
    return u"'{}'".format(v) if v is not None else 'NULL'


def DATE(v):
    return 'NULL'


def add_track(i, track):
    with connection.cursor() as cursor:
        track_info = {
            'id': i,
            'title': STRING(addslashes(track['title'])),
            'artist': STRING(addslashes(track['artist'])),
            'album': STRING(addslashes(track['album'])),
            'year': none_to_null(track['year']),
            'genre': STRING(addslashes(track['genre'])),
            'style': STRING(addslashes(track['style'])),
            'bpm': none_to_null(track['bpm']),
            'rating': none_to_null(track['rating']),  # track.metadata.rating,
            'favorite': none_to_null(track['favorite']),  # track.metadata.loved,
            'comments': STRING(addslashes(track['comments'])),  # track.metadata.comments,
            'last_played': DATE(track['last_played']),  # None,
            'waveform': STRING(track['waveform']),  # None,
            'cover_medium': STRING(addslashes(track['cover_medium'])),  # cover_art_data['small'],
            'cover_small': STRING(addslashes(track['cover_small'])),  # cover_art_data['tiny'],
            'cover_large': STRING(addslashes(track['cover_large'])),  # cover_art_data['medium'],
            'cover_original': STRING(addslashes(track['cover_original'])),  # cover_art_data['original'],
            'track_length': none_to_null(track['track_length']),  # track.info.stream_length,
            'stream_start': none_to_null(track['stream_start']),  # 0,
            'stream_end': none_to_null(track['stream_end']),  # track.info.stream_length,
            'stream_length': none_to_null(track['stream_length']),  # track.info.stream_length,
            'date_added': DATE(track['date_added']),  # None,
            'date_modified': DATE(track['date_modified']),  # None,
            'bitrate': none_to_null(track['bitrate']),  # track.info.bitrate,
            'samplerate': none_to_null(track['samplerate']),  # track.info.samplerate,
            'file_name': STRING(addslashes(track['file_name'])),  # f,
            'file_size': track['file_size'],  # file_size,
            'hash': STRING(track['hash']),
            'play_at': STRING(track['play_at']),
            'kind': STRING(track['kind']),
            'category': STRING(track['category']),
            'description': STRING(track['description']),# mp3hash(f)
        }
        print i
        sql = insert_track_sql.format(**track_info)
        print sql
        cursor.execute(sql)

        # print sql


def process_track_queue(*args):
    #global wg
    #global track
    global last_time
    global db
    last_time = None
    i = 0
    while len(files) > 0:
        f = files.pop(0)
        print (f)
        track = load_track(f)
        print track
        add_track(i, track)
        i += 1
    connection.commit()
    # try:
    #     if track is not None:
    #         #print ('file://' + urllib.quote(os.path.abspath(f)))
    #         path = os.path.join(_root_folder, 'wave_cache', quote(str(track), "")+".wf")
    #         print path
    #         if not os.path.exists(path):
    #             try:
    #                 wg = WaveformGenerator(35000)
    #                 last_time = 0
    #                 wg.set_data_point_callback(_print_time)
    #                 wave_points = wg.generate_waveform(f) #= WaveformGenerator(f, 35000)
    #                 try:
    #                     pass
    #                     #file_ = open(path, 'wb')
    #                     #flat_wave = [num for pair in wave_points for num in pair]
    #                     #file_.write(str(len(flat_wave)) + '\n')
    #                     #arr = array.array('f', flat_wave)
    #                     #arr.tofile(file_)
    #                     #file_.close()
    #                     #track.metadata._metadata['waveform'] = path
    #                 except Exception as details:
    #                     print (details)
    #                     track.metadata._metadata['waveform'] = None
    #
    #                 #Clock.schedule_interval(force_process_next, 1)
    #             except Exception as details:
    #                 print (details)
    #                 track.metadata._metadata['waveform'] = None
    #                 #Clock.schedule_once(process_track_queue, 0)
    #                 #GLib.timeout_add(1,process_track_queue)
    #             db[track.location] = track
    #
    #         else:
    #             track.metadata._metadata['waveform'] = path
    #             db[track.location] = track
    #             #Clock.schedule_once(process_track_queue, 0)
    #
    #             #GLib.timeout_add(1, process_track_queue)
    # except KeyboardInterrupt:
    #     track.metadata._metadata['waveform'] = None
    #     db[track.location] = track
    #
    #     pass
    # else:
    # process_track_queue()
    #db[track.location] = track
    #Clock.schedule_once(process_track_queue, 0)
    #GLib.timeout_add(1, process_track_queue)

    # else:
    #    loop.quit()
    print (foo)


def process_track_queue_XXX(*args):
    #global wg
    #global track
    global last_time
    global db
    last_time = None
    while len(files) > 0:
        f = files.pop(0)
        print (f)
        track = load_track(f)
        print track
        try:
            if track is not None:
                #print ('file://' + urllib.quote(os.path.abspath(f)))
                path = os.path.join(_root_folder, 'wave_cache', quote(str(track), "") + ".wf")
                print path
                if not os.path.exists(path):
                    try:
                        wg = WaveformGenerator(35000)
                        last_time = 0
                        wg.set_data_point_callback(_print_time)
                        wave_points = wg.generate_waveform(f)  # = WaveformGenerator(f, 35000)
                        try:
                            pass
                            #file_ = open(path, 'wb')
                            #flat_wave = [num for pair in wave_points for num in pair]
                            #file_.write(str(len(flat_wave)) + '\n')
                            #arr = array.array('f', flat_wave)
                            # arr.tofile(file_)
                            # file_.close()
                            #track.metadata._metadata['waveform'] = path
                        except Exception as details:
                            print (details)
                            track.metadata._metadata['waveform'] = None

                        #Clock.schedule_interval(force_process_next, 1)
                    except Exception as details:
                        print (details)
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
    print (foo)


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

# if _root_folder is not None:
#    foo = open(os.path.join(_root_folder, "library.data"), "w")
#    tracks = [(key, db[key].location, db[key].info._metadata, db[key].metadata._metadata) for key in db]
#    #print tracks
#    pickle.dump(tracks, foo)
#db = json.dumps(tracks, indent=4)
# foo.write(db)
# foo.close()
# save()
