#!/usr/bin/python
import os
import sys
print os.getcwd()
sys.path.append('.')
from pydjay.core.library import load_file as lib_load_file
#from pydjay.core.library.track import Track, save_mp3_file
#import os.getcwd()
import sys
import io
from PIL import Image
import urllib
import array

from pydjay.core.audio.wavegen import WaveformGenerator
import pprint
import subprocess
import datetime

import plistlib

foo = plistlib.readPlist("Music.xml")


def _get_string(list):
    return ''.join([x.text for x in list])


def node_to_dict(node):
    result = {"__tag__": node.tag}
    for attribute in node.children:
        if attribute.tag != 'CharData':
            result[attribute.tag] = _get_string(attribute.children)
            # print attribute.tag, result[attribute.tag]
    return result


_root_folder = os.path.abspath(os.path.expanduser('~/.pydjay'))


def quote(str_, i=None):
    bar = str_.replace("/", "-")
    bar = bar.replace(":", "-")
    bar = bar.replace("\"", "-")
    bar = bar.replace("?", "-")
    return bar


files = []


tracks = foo.get("Tracks", {})
track_list = []

import pymysql
from mp3hash import mp3hash

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
date_added, date_modified, bitrate, samplerate, file_name, file_size, hash, play_at, kind, category, description, disabled, original_file_name, vocals
)
VALUES (
-- {id},
{title}, {artist}, {album}, {year}, {genre}, {style}, {bpm}, {rating}, {favorite}, {comments},
{last_played}, {waveform}, {cover_medium}, {cover_small}, {cover_large}, {cover_original}, {track_length},
{stream_start}, {stream_end}, {stream_length}, {date_added}, {date_modified}, {bitrate}, {samplerate},
{file_name}, {file_size}, {hash}, {play_at}, {kind}, {category}, {description}, {disabled}, {original_file_name}, {vocals}
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


def STRING(v):
    return u"'{}'".format(v) if v is not None else 'NULL'


def DATE(v):
    fo = "'{}'".format(v.strftime("%Y-%m-%d %H:%M:%S")) if v is not None else 'NULL'
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
        'vocals': tracks[n].get('Composer', None),
        'last_played': None,
        'waveform': None,
        'cover_medium': None,  # cover_art_data['small'],
        'cover_small': None,  # cover_art_data['tiny'],
        'cover_large': None,  # cover_art_data['medium'],
        'cover_original': None,  # cover_art_data['original'],
        'track_length': tracks[n].get('Total Time', None) * 1000000,
        'stream_start': 0,
        'stream_end': tracks[n].get('Total Time', None) * 1000000,
        'stream_length': tracks[n].get('Total Time', None) * 1000000,
        'date_added': tracks[n].get('Date Added', None),
        'date_modified': tracks[n].get('Date Modified', None),
        'bitrate': tracks[n].get('Bit Rate', None),
        'samplerate': tracks[n].get('Sample Rate', None),
        'file_name': urllib.unquote(tracks[n].get('Location', 'file://')[7:]).decode('utf8'),
        'file_size': tracks[n].get('Size', None),
        'hash': None,
        'play_at': tracks[n].get('Album Artist', None),
        'kind': tracks[n].get('Kind', None),
        'category': tracks[n].get('Category', None),
        'description': tracks[n].get('Description', None)
    }
    track_list.append(new_track_metadata)

files = sorted(track_list, key=lambda x: x['file_name'])


def load_track(f):
    track = Track(f['location'], {}, {})
    if track is None:
        return None
    del f['location']
    track.metadata._metadata = f
    return track


#def _next_track(data_points):
#    Clock.schedule_once(_do_next_track, 0)
#    Clock.unschedule(force_process_next)


last_time = None


def _print_time(total, time, point):
    global last_time
    global timeout_time
    cur_time = time / 1000000000
    timeout_time = 10
    if last_time is None or cur_time - last_time > 2:
        printProgress(time, total, "Generating Waveform", "completed")
        last_time = cur_time


def printProgress(iteration, total, prefix='', suffix='', decimals=0, barLength=30):
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
            'vocals': STRING(addslashes(track['vocals'])),
            'bpm': none_to_null(track['bpm']),
            'rating': none_to_null(track['rating']),
            'disabled': bool_to_int(track['disabled']),
            'favorite': none_to_zero(track['favorite']),
            'comments': STRING(addslashes(track['comments'])),
            'last_played': DATE(track['last_played']),
            'waveform': STRING(addslashes(track['waveform'])),
            'cover_medium': STRING(addslashes(track['cover_medium'])),
            'cover_small': STRING(addslashes(track['cover_small'])),
            'cover_large': STRING(addslashes(track['cover_large'])),
            'cover_original': STRING(addslashes(track['cover_original'])),
            'track_length': none_to_null(track['track_length']),
            'stream_start': none_to_null(track['stream_start']),
            'stream_end': none_to_null(track['stream_end']),
            'stream_length': none_to_null(track['stream_length']),
            'date_added': DATE(track['date_added']),
            'date_modified': DATE(track['date_modified']),
            'bitrate': none_to_null(track['bitrate']),
            'samplerate': none_to_null(track['samplerate']),
            'file_name': STRING(addslashes(track['file_name'])),
            'original_file_name': STRING(addslashes(track['original_file_name'])),
            'file_size': track['file_size'],
            'hash': STRING(track['hash']),
            'play_at': STRING(track['play_at']),
            'kind': STRING(track['kind']),
            'category': STRING(track['category']),
            'description': STRING(track['description']),
        }
        sql = insert_track_sql.format(**track_info)
        cursor.execute(sql)


def create_thumbnail(track, image, size, folder, name):
    image.thumbnail(size, Image.ANTIALIAS)
    image.save(os.path.join(os.path.expanduser('~/.pydjay/sql_image_cache'), name))
    return name


def quote(str_, *i):
    bar = str_.replace(u"/", u"-")
    bar = bar.replace(u":", u"-")
    bar = bar.replace(u"\"", u"-")
    bar = bar.replace(u"?", u"-")
    return bar


def make_unique_filename(folder, prefix, extension):
    template_name = prefix+"_{index}.{ext}"
    index = 1
    name = template_name.format(index = index, ext=extension)
    p = os.path.join(folder, name)
    while os.path.exists(p):
        index += 1
        name = template_name.format(index = index, ext=extension)
        p = os.path.join(folder, name)
    return name

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
        file_meta = lib_load_file(orig)
        if file_meta is not None:
            album_art = file_meta.metadata.album_cover
        else:
            print track.location

        #mp3_file = quote("%s - %s (%s).mp3" % (f['title'],  f['artist'], f['album']))
        #mp3_path = os.path.join(os.path.expanduser('~/.pydjay/sql_music_cache'), mp3_file)
        mp3_file= make_unique_filename(os.path.expanduser('~/.pydjay/sql_music_cache'), 'track', 'mp3')
        mp3_path = os.path.join(os.path.expanduser('~/.pydjay/sql_music_cache'), mp3_file)

        #def _f(x): return x if ord(x) < 128 else '__'
        #x = [_f(x) for x in mp3_file]
        #cover_art_filename = quote("".join(x))

        if not os.path.exists(mp3_path):
            subprocess.call(['avconv', '-y', '-i', f['file_name'], '-acodec', 'libmp3lame', '-ab',  '320k', '-vn', '-r', '48000', mp3_path])

        f['original_file_name'] = f['file_name']
        f['file_name'] = mp3_file
        stat = os.stat(mp3_path)
        f['file_size'] = stat.st_size
        tr = lib_load_file(mp3_path)
        foo = {
            'track_length': tr.info.stream_length,
            'stream_start': 0,
            'stream_end': tr.info.stream_length,
            'stream_length': tr.info.stream_length,
            'bitrate': tr.info.bitrate,
            'samplerate': tr.info.samplerate,
        }
        f.update(foo)

        wave_file = make_unique_filename(os.path.expanduser('~/.pydjay/sql_wave_cache'), 'waveform', 'wv')  #quote("%s - %s (%s).wv" % (f['title'],  f['artist'], f['album']))
        wave_path = os.path.join(os.path.expanduser('~/.pydjay/sql_wave_cache'), wave_file)
        if not os.path.exists(wave_path):
            try:
                wg = WaveformGenerator(35000)
                last_time = 0
                wg.set_data_point_callback(_print_time)
                wave_points = wg.generate_waveform(mp3_path)  # = WaveformGenerator(f, 35000)
                try:
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

            except Exception as details:
                print (details)
                f['waveform'] = None

        else:
            f['waveform'] = wave_file

        if album_art is not None:
            cover = album_art
            im_type = cover[0]
            im_data = cover[1]
            print im_type
            ext = {'image/jpeg': 'jpg', 'image/png': 'png'}.get(im_type, None)
            if ext is not None:
                data = io.BytesIO(im_data)
                image = Image.open(data)
                cover_art_data = {}
                cover_art_filename_original = make_unique_filename(os.path.expanduser('~/.pydjay/sql_image_cache'), 'cover_original', 'png')
                cover_art_filename_small = make_unique_filename(os.path.expanduser('~/.pydjay/sql_image_cache'), 'cover_small', 'png')
                cover_art_filename_medium = make_unique_filename(os.path.expanduser('~/.pydjay/sql_image_cache'), 'cover_medium', 'png')
                cover_art_filename_large = make_unique_filename(os.path.expanduser('~/.pydjay/sql_image_cache'), 'cover_large', 'png')
                #quote(u'cover_im_{}-{}'.format(f['album'], f['artist']))

                def P(name):
                    return os.path.join(os.path.expanduser('~/.pydjay/sql_image_cache'), name)
                #def _f(x): return x if ord(x) < 128 else '__'
                #x = [_f(x) for x in cover_art_filename]
                #cover_art_filename = "".join(x)
                #or_image_filename = 'original_' + cover_art_filename + ".png"
                #or_image_path = os.path.join('sql_image_cache', or_image_filename)
                #PPPP = os.path.join(_root_folder, 'sql_image_cache', or_image_filename)
                #if not os.path.exists(PPPP):
                image.save(P(cover_art_filename_original))
                folder = os.path.expanduser('~/.pydjay/sql_image_cache')
                track = None
                f['cover_original'] = cover_art_filename_original
                f['cover_large'] = create_thumbnail(track, image, (320, 320), folder, cover_art_filename_large)
                f['cover_medium'] = create_thumbnail(track, image, (160, 160), folder, cover_art_filename_medium)
                f['cover_small'] = create_thumbnail(track, image, (100, 100), folder, cover_art_filename_small)
                index += 1
            else:
                print ("")

        add_track(0, f)
        connection.commit()

process_track_queue()
