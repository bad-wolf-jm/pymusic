from pydjay.core.library import init, load_file as lib_load_file, save
from pydjay.core.library.track import Track, save_mp3_file
import os, sys, io
from PIL import Image
import urllib
import array
import cPickle as pickle
from gi.repository import GObject, GLib

#from pydjay.audio.wavegen import WaveformGenerator
from kivy.clock import mainthread, Clock
from kivy.support import install_gobject_iteration
from kivy.base import EventLoop, runTouchApp
from kivy.uix.label import Label
import pprint
import subprocess


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

for n in tracks:
    new_track_metadata = {
        'title':         tracks[n].get('Name', None),
        'artist':        tracks[n].get('Artist', None),
        'album':         tracks[n].get('Album', None),
        'album_artist':  None, 
        'category':      None,
        'description':   None, 
        'genre':         tracks[n].get('Genre', None),
        'grouping':      None, 
        'rating':        int(tracks[n].get('Rating', None) / 20),
        'bpm':           tracks[n].get('BPM', None),
        'year':          tracks[n].get('Year', None),
        'comments':      tracks[n].get('Comments', None),
        'style':         tracks[n].get('Grouping', None),
        'play_at':       tracks[n].get('Album Artist', None),
        'vocal':         tracks[n].get('Composer', None),
        'loved':         tracks[n].get('Loved', None),
        'location':      urllib.unquote(tracks[n].get('Location','file://')[7:])
        }
    #pprint.pprint(new_track_metadata)
    track_list.append(new_track_metadata)

#sys.exit()



files = sorted(track_list, key= lambda x: x['location'])





#for f in sorted(os.listdir(scan_root)):
#    files.append(os.path.join(scan_root, f))



                               
    #print f
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


def printProgress (iteration, total, prefix = '', suffix = '', decimals = 0, barLength = 1):
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
    global wg
    global track
    global last_time
    global db
    last_time = None
    total = len(files)
    while len(files) > 0:
        f = files.pop(0)
        orig = f['location']
        print f['location']
        track = load_track(f)

        
        mp3_file = quote("%s - %s (%s).mp3"% (track.metadata.title, track.metadata.artist, track.metadata.album))
        mp3_path = os.path.join('/Users/jihemme/Music/Blues MP3', mp3_file)

        if not os.path.exists(mp3_path):
            subprocess.call(['avconv', '-y',
                             '-i',
                             track.location,
                             '-acodec', 'libmp3lame',
                             '-ab',  '320k',
                             '-vn',
                             '-r', '48000',
                             mp3_path])
        #print 'Converting'
        #print 'XXXXXXXXXXXXXX', track.location
        file_meta = lib_load_file(track.location)
        if file_meta is not None:
            album_art = file_meta.metadata.album_cover
        else:
            print track.location
            sys.exit(0)
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

    else:
        loop.quit()






    
def _do_next_track(*data_points):
    wave_points = wg.get_data_points()
    path = os.path.join(_root_folder, 'wave_cache', quote(str(track), "")+".wf")
    #file_ = open(path, 'w')
    print path
    flat_wave = [num for pair in wave_points for num in pair]
    arr = array.array('f', flat_wave)
    #print flat_wave[0:10]
    #print wave[0:5]
    #file_.close()
    try:
        file_ = open(path, 'wb')
        arr.tofile(file_)
        file_.close()
        track.metadata._metadata['waveform'] = path
    except Exception, details:
        print details
        track.metadata._metadata['waveform'] = None
    db[track.location] = track
    #GLib.timeout_add(1, process_track_queue)

    Clock.schedule_once(process_track_queue, 0)


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
