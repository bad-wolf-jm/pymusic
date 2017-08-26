from pydjay.core.library import init, load_file as lib_load_file, save
from pydjay.core.library.track import Track, save_mp3_file
import os, sys, io
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
import pprint
import subprocess
import datetime

from pydjay.utils.xml import Parser
import plistlib

foo = plistlib.readPlist("Music.xml")
#print foo

#Parser.parse(open('Music.xml').read())


def _get_string(list):
    return ''.join([x.text for x in list])

def node_to_dict(node):
    result = {"__tag__":node.tag}
    for attribute in node.children:
        if attribute.tag != 'CharData':
            result[attribute.tag] = _get_string(attribute.children)
                #print attribute.tag, result[attribute.tag]
    return result




#install_gobject_iteration()

_root_folder = os.path.abspath(os.path.expanduser('~/.pydjay'))
init(_root_folder)

loop = GLib.MainLoop()

#scan_root = sys.argv[1]

timeout_time = 10

#if not os.path.exists(scan_root):
#    sys.exit(1)


db = {}

def quote(str_, i = None):
    bar = str_.replace("/", "-")
    bar = bar.replace(":", "-")
    bar = bar.replace("\"", "-")
    bar = bar.replace("?", "-")
    return bar

def create_thumbnail(track, image, size, type):
    new_path = os.path.join(_root_folder, 'image_cache', type+'_' + quote(str(track), "") + ".png")
    image.thumbnail(size, Image.ANTIALIAS)
    image.save(new_path)
    return new_path


files = []


tracks = foo.get("Tracks", {})
track_list = []

#{#'Album': 'Coney Island Washboard Melody',
# #'Skip Date': datetime.datetime(2016, 12, 14, 1, 0, 14),
# #'Persistent ID': 'D1BB2F3EC5163058',
# #'BPM': 71,
# #'Album Artist': 'Any time',
# #'Track Type': 'File',
# #'Composer': 'Instrumental',
# 'File Folder Count': 2,
# 'Total Time': 255829,
# 'Sort Album Artist': 'Any time',
# #'Genre': 'Slow Jazz',
# 'Bit Rate': 712,
# #'Loved': True,
# #'Kind': 'MPEG-4 video file',
# #'Name': 'Creole Love Call',
# #'Artist': u'La Planche \xe0 Dixie, Christin Giovanardi',
# #'File Type': 1297101856,
# #'Date Added': datetime.datetime(2016, 12, 10, 7, 3, 2),
# #'Comments': '8/8, straight rhythm',
# 'Sort Composer': 'Instrumental',
# 'Artwork Count': 1,
# #'Grouping': 'Slow Drag',
# 'Location': 'file:///Volumes/Media/Blues%20Music/Creole%20Love%20Call%20-%20La%20Planche%20a%CC%80%20Dixie,%20Christin%20Giovanardi%20(Coney%20Island%20Washboard%20Melody)%20.mp4',
# 'Date Modified': datetime.datetime(2016, 12, 14, 1, 0, 13),
# 'Library Folder Count': 1,
# 'Skip Count': 1,
# 'Track ID': 18731,
# 'Size': 23408299}

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
date_added, date_modified, bitrate, samplerate, file_name, file_size, hash, play_at, kind, category, description, disabled, original_file_name
)
VALUES (
-- {id},
{title}, {artist}, {album}, {year}, {genre}, {style}, {bpm}, {rating}, {favorite}, {comments},
{last_played}, {waveform}, {cover_medium}, {cover_small}, {cover_large}, {cover_original}, {track_length},
{stream_start}, {stream_end}, {stream_length}, {date_added}, {date_modified}, {bitrate}, {samplerate},
{file_name}, {file_size}, {hash}, {play_at}, {kind}, {category}, {description}, {disabled}, {original_file_name}
)
"""

def addslashes(s):
    if s == None:
        return None
    d = {u'"': u'\\"',
         u"'": u"\\'",
         u"\0": u"\\\0",
         u"\\": u"\\\\"}
    return u''.join([d.get(c, c) for c in s])


def none_to_null(v):
    return v if v is not None else u'NULL'

def none_to_zero(v):
    return v if v is not None else 0

def bool_to_int(b):
    return 1 if b else 0
#    if s == None:
#        return ''
#    d = {'"': '\\"', "'": "\\'", "\0": "\\\0", "\\": "\\\\"}
#    return u''.join(d.get(c, c) for c in s)


def STRING(v):
    return u"'{}'".format(v) if v is not None else 'NULL'


def DATE(v):
    fo = "date('{}')".format(v.strftime("%Y-%m-%d %H:%M:%S")) if v is not None else 'NULL'
    return fo


for n in tracks:
    new_track_metadata = {
        'id': None,
        'title': tracks[n].get('Name', None),
        'artist': tracks[n].get('Artist', None),
        'album': tracks[n].get('Album', None),
        'year': tracks[n].get('Year', None),
        'genre': tracks[n].get('Genre', None),
        'style': tracks[n].get('Grouping', None),
        'bpm': tracks[n].get('BPM', None),
        'rating': tracks[n].get('Rating', None) // 20,
        'favorite': tracks[n].get('Loved', None),
        'comments': tracks[n].get('Comments', None),
        'disabled': tracks[n].get('Disabled', False),
        'last_played': None,
        'waveform': None,
        'cover_medium': None, #cover_art_data['small'],
        'cover_small': None, #cover_art_data['tiny'],
        'cover_large': None, #cover_art_data['medium'],
        'cover_original': None, #cover_art_data['original'],
        'track_length': tracks[n].get('Total Time', None)*1000000,
        'stream_start': 0,
        'stream_end': tracks[n].get('Total Time', None)*1000000,
        'stream_length': tracks[n].get('Total Time', None)*1000000,
        'date_added': tracks[n].get('Date Added', None),
        'date_modified': tracks[n].get('Date Modified', None),
        'bitrate': tracks[n].get('Bit Rate', None),
        'samplerate': tracks[n].get('Sample Rate', None),
        'file_name': urllib.unquote(tracks[n].get('Location','file://')[7:]).decode('utf8'),
        'file_size': tracks[n].get('Size', None),
        'hash': None,
        'play_at':tracks[n].get('Album Artist', None),
        'kind': tracks[n].get('Kind', None),
        'category': tracks[n].get('Category', None),
        'description': tracks[n].get('Description', None)
    }
    track_list.append(new_track_metadata)

files = sorted(track_list, key= lambda x: x['file_name'])

def load_track(f):
    track = Track(f['location'], {}, {})
    if track is None:
        return None
    #account for my funny tagging
    del f['location']
    track.metadata._metadata = f


    #track.metadata._metadata['play_at'] = track.metadata._metadata.get('album_artist', None)
    #track.metadata._metadata['vocal']   = track.metadata._metadata.get('composer', None)
    #track.metadata._metadata['style']   = track.metadata._metadata.get('grouping', None)
    #track.metadata_metadata['speed_feel'] = track.metadata._metadata['']
    #track.metadata_metadata['mood'] = track.metadata._metadata['']

    #if track.metadata.album_cover is not None:
    ##    cover = track.metadata.album_cover
    #    im_type = cover[0]
    #    im_data = cover[1]
    #    ext = {'image/jpeg': 'jpg','image/png': 'png'}.get(im_type, None)
    #    if ext is not None:
    #        data = io.BytesIO(im_data)
    #        image = Image.open(data)
    #        cover_art_data = {}
    #        image.save(os.path.join(_root_folder, 'image_cache', 'original_' + quote(str(track), "")+".png"))
    #        cover_art_data['original'] = os.path.join(_root_folder, 'image_cache', 'original_'+quote(str(track), "")+".png")
    #        #image.thumbnail((320,320), Image.ANTIALIAS)
    #        #image.save(os.path.join('/Users/jihemme/.pydjay/image_cache', 'medium_'+str(track)+".jpg"))
    #        cover_art_data['medium'] = create_thumbnail(track, image, (320,320), 'medium')
    #        cover_art_data['small']  = create_thumbnail(track, image, (160,160), 'small')
    #        cover_art_data['tiny']   = create_thumbnail(track, image, (100,100), 'tiny')

            #os.path.join('/Users/jihemme/.pydjay/image_cache', 'medium_'+str(track)+".jpg")
#            image.thumbnail((160,160), Image.ANTIALIAS)
#            image.save(os.path.join('/Users/jihemme/.pydjay/image_cache', 'small_'+str(track)+".jpg"))
#            cover_art_data['small'] = os.path.join('/Users/jihemme/.pydjay/image_cache', 'small_'+str(track)+".jpg")
#            image.thumbnail((100,100), Image.ANTIALIAS)
#            image.save(os.path.join('/Users/jihemme/.pydjay/image_cache', 'tiny_'+str(track)+".jpg"))
#            cover_art_data['tiny'] = os.path.join('/Users/jihemme/.pydjay/image_cache', 'tiny_'+str(track)+".jpg")
    #        track.metadata._metadata['album_art'] = cover_art_data
            #im   = CoreImage(data, ext = ext)
            #self._album_art = im

    #print track.metadata.album_cover
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
    #print time, total
    #if time > total:
    #    Glib.timeout_add
    if last_time is None or cur_time - last_time > 2:
        printProgress(time, total, "Generating Waveform", "completed")
        last_time = cur_time

#loop.run()


def printProgress (iteration, total, prefix = '', suffix = '', decimals = 0, barLength = 30):
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
            'disabled': bool_to_int(track['disabled']),  # track.metadata.loved,
            'favorite': none_to_zero(track['favorite']),  # track.metadata.loved,
            'comments': STRING(addslashes(track['comments'])),  # track.metadata.comments,
            'last_played': DATE(track['last_played']),  # None,
            'waveform': STRING(addslashes(track['waveform'])),  # None,
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
            'original_file_name': STRING(addslashes(track['original_file_name'])),  # f,
            'file_size': track['file_size'],  # file_size,
            'hash': STRING(track['hash']),
            'play_at': STRING(track['play_at']),
            'kind': STRING(track['kind']),
            'category': STRING(track['category']),
            'description': STRING(track['description']),# mp3hash(f)
        }
        #print i
        sql = insert_track_sql.format(**track_info)
        #print sql
        cursor.execute(sql)

def create_thumbnail(track, image, size, type, name):
    new_name = type + '_' + name + ".png"
    new_path = os.path.join('sql_image_cache', new_name) #type + '_' +
                            #name  # quote(str(track), "")
                            #+ ".png")
    if not os.path.exists(new_path):
        image.thumbnail(size, Image.ANTIALIAS)
        image.save(os.path.join(_root_folder, new_path))
    return new_name

def quote(str_, *i):
    bar = str_.replace(u"/", u"-")
    bar = bar.replace(u":", u"-")
    bar = bar.replace(u"\"", u"-")
    bar = bar.replace(u"?", u"-")
    return bar

def process_track_queue(*args):
    global wg
    global track
    global last_time
    global db
    last_time = None
    total = len(files)
    index = 0
    while len(files) > 0:
        f = files.pop(0)
        orig = f['file_name']
        print f['file_name']
        #track = load_track(f)
        file_meta = lib_load_file(orig)
        if file_meta is not None:
            album_art = file_meta.metadata.album_cover
            #print album_art
        else:
            print track.location
            #sys.exit(0)
            #print album_art

        mp3_file = quote("%s - %s (%s).mp3"% (f['title'],  f['artist'], f['album']))
        mp3_path = os.path.join(os.path.expanduser('~/.pydjay/sql_music_cache'), mp3_file)
        _f = lambda x: x if ord(x)<128 else '__'
        x = [_f(x) for x in mp3_file]
        cover_art_filename = quote("".join(x))

        if not os.path.exists(mp3_path):
            subprocess.call(['avconv', '-y',
                             '-i',
                             f['file_name'],
                             '-acodec', 'libmp3lame',
                             '-ab',  '320k',
                             '-vn',
                             '-r', '48000',
                             mp3_path])
            pass

        f['original_file_name'] = f['file_name']
        f['file_name'] = mp3_file
        stat = os.stat(mp3_path)
        f['file_size'] = stat.st_size
        tr = lib_load_file(mp3_path)
        #update file size, bitdate and samplerate from the mo3 file
        foo = {
            'track_length': tr.info.stream_length,
            'stream_start': 0,
            'stream_end': tr.info.stream_length,
            'stream_length': tr.info.stream_length,
            'bitrate': tr.info.bitrate,
            'samplerate': tr.info.samplerate,
            }
        f.update(foo)

        #waveform
        #wave_file =
        wave_file = quote("%s - %s (%s).wv"% (f['title'],  f['artist'], f['album']))
        wave_path = os.path.join(os.path.expanduser('~/.pydjay/sql_wave_cache'), wave_file)
        #wave_path = os.path.join(_root_folder, 'sql_wave_cache', quote(str(track), "") + ".wf")
        #print path
        if not os.path.exists(wave_path):
            try:
                wg = WaveformGenerator(35000)
                last_time = 0
                wg.set_data_point_callback(_print_time)
                wave_points = wg.generate_waveform(mp3_path)  # = WaveformGenerator(f, 35000)
                try:
                    #pass
                    file_ = open(wave_path, 'wb')
                    flat_wave = [num for pair in wave_points for num in pair]
                    file_.write(str(len(flat_wave)) + '\n')
                    arr = array.array('f', flat_wave)
                    arr.tofile(file_)
                    file_.close()
                    f['waveform'] = wave_file
                except Exception as details:
                    print (details)
                    f['waveform'] = None

                #Clock.schedule_interval(force_process_next, 1)
            except Exception as details:
                print (details)
                f['waveform'] = None
                #Clock.schedule_once(process_track_queue, 0)
                # GLib.timeout_add(1,process_track_queue)
            #db[track.location] = track

        else:
            f['waveform'] = wave_file
            #db[track.location] = track



        if album_art is not None:
            cover = album_art
            im_type = cover[0]
            im_data = cover[1]
            ext = {'image/jpeg': 'jpg', 'image/png': 'png'}.get(im_type, None)
            if ext is not None:
                data = io.BytesIO(im_data)
                image = Image.open(data)
                cover_art_data = {}
                cover_art_filename = quote(u'cover_im_{}-{}'.format(f['album'], f['artist']))
                _f = lambda x: x if ord(x)<128 else '__'
                x = [_f(x) for x in cover_art_filename]
                cover_art_filename = "".join(x)
                or_image_filename = 'original_' + cover_art_filename + ".png"
                or_image_path = os.path.join('sql_image_cache', or_image_filename)
                #                             'original_' + cover_art_filename  # quote(str(track), "")
                #                             + ".png")
                PPPP = os.path.join(_root_folder, 'sql_image_cache', or_image_filename)
                if not os.path.exists(PPPP):
                    image.save(PPPP)
                f['cover_original'] = or_image_filename
                f['cover_large'] = create_thumbnail(track, image, (320, 320), 'large', cover_art_filename)
                f['cover_medium'] = create_thumbnail(track, image, (160, 160), 'medium', cover_art_filename)
                f['cover_small'] = create_thumbnail(track, image, (100, 100), 'small', cover_art_filename)
                index += 1
                connection.commit()
                #track.metadata._metadata['album_art'] = cover_art_data


        add_track(0, f)

    connection.commit()
    #else:
    #    loop.quit()



def REST():
        mp3_file = quote("%s - %s (%s).mp3"% (track.metadata.title, track.metadata.artist, track.metadata.album))


        mp3_path = os.path.join('/Users/jihemme/Music/Blues MP3', mp3_file)

        if not os.path.exists(mp3_path):
            #subprocess.call(['avconv', '-y',
            #                 '-i',
            #                 track.location,
            #                 '-acodec', 'libmp3lame',
            #                 '-ab',  '320k',
            #                 '-vn',
            #                 '-r', '48000',
            #                 mp3_path])
            pass
        #print 'Converting'
        #print 'XXXXXXXXXXXXXX', track.location
        file_meta = lib_load_file(track.location)
        if file_meta is not None:
            album_art = file_meta.metadata.album_cover
        else:
            print track.location
            #sys.exit(0)
            print album_art
        #sys.exit(0)
        track.metadata._metadata['album_art'] = album_art
        track.location = mp3_path
        #if album_art is not None:
        ##
        #    sys.exit()
        save_mp3_file(track)

        #if track is not None:
        #    #print 'file://' + urllib.quote(os.path.abspath(f))
        #    path = os.path.join(_root_folder, 'wave_cache', quote(str(track), "")+".wf")
        #    #if not os.path.exists(path):
        #    #    try:
        #    #        wg.generate_waveform(track.location) #= WaveformGenerator(f, 35000)
        #    #        #Clock.schedule_interval(force_process_next, 1)
        #    #    except Exception, details:
        #    #        print "BRABRA", details
        #    #        track.metadata._metadata['waveform'] = None
        #    #        db[track.location] = track
        #    #        Clock.schedule_once(process_track_queue, 0)
        #    #        #GLib.timeout_add(1,process_track_queue)
        #    #
        #    #        else:
        #    #            print 'WAVEFORM EXISTS'
        #    #            track.metadata._metadata['waveform'] = path
        #    #            db[track.location] = track
        #    Clock.schedule_once(process_track_queue, 0)#
##
#                #GLib.timeout_add(1, process_track_queue)

#        else:
#            #process_track_queue()
#            #db[track.location] = track
#            Clock.schedule_once(process_track_queue, 0)
#            #GLib.timeout_add(1, process_track_queue)








#def _do_next_track(*data_points):
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
#wg.set_process_done_callback(_next_track)
#wg.set_data_point_callback(_print_time)
track = None
Clock.schedule_once(process_track_queue, 0)

#GLib.timeout_add(0, process_track_queue)
xxx = Label()

#try:
runTouchApp(xxx)
#EventLoop.run()
print 'running main loop'
#loop.run()
print 'stopped main loop'

#if _root_folder is not None:
#    foo = open(os.path.join(_root_folder, "library__2.data"), "w")
#    tracks = [(key, db[key].location, db[key].info._metadata, db[key].metadata._metadata) for key in db]
#    #print tracks
#    pickle.dump(tracks, foo)
##    #db = json.dumps(tracks, indent=4)
#    #foo.write(db)
#    #foo.close()
##save()
