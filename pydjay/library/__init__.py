#init
import os
import cPickle as pickle
import time
from track import load_file, Track
from playlist import MainPlaylist, FilteredPlaylist


_folders  = [os.path.expanduser('~'), #'/Volumes/Media/Blues MP3',
             #'/Volumes/Media/Blues Music',
             #'/Volumes/Media/iTunes/Music'
             ]
_root_folder = None
_sessions = []
_library  = {}
_playlists = []


def init(root_folder):
    global _root_folder
    #print "INIT"
    _root_folder = root_folder



    structure = ['sessions', 'image_cache', 'wave_cache', 'playlists']

    for x in structure:
        path = os.path.join(root_folder, x)
        if not os.path.exists(path):
            os.makedirs(path)
    
    #if not os.path.exists(os.path.join(root_folder, "sessions")):
    #    os.makedirs(os.path.join(root_folder, "sessions"))
    #if not os.path.exists(os.path.join(root_folder, "image_cache")):
    #    os.makedirs(os.path.join(root_folder, "image_cache"))
    #if not os.path.exists(os.path.join(root_folder, "wave_cache")):
    #    os.makedirs(os.path.join(root_folder, "wave_cache"))
    #if not os.path.exists(os.path.join(root_folder, "playlists")):
    #    os.makedirs(os.path.join(root_folder, "playlists"))
        
    if os.path.exists(os.path.join(root_folder, "library.data")):
        foo = open(os.path.join(root_folder, "library.data"))
        _tracks = pickle.load(foo)
        for key, location, info, metadata in _tracks:
            _library[key] = Track(location, info, metadata)
    #if os.path.exists(os.path.join(root_folder, "playlists.data")):
    #    foo = open(os.path.join(root_folder, "playlists.data"))
    #    _library = pickle.load(foo)




def save():
    if _root_folder is not None:
        foo = open(os.path.join(_root_folder, "library.data"), "w")
        tracks = [(key, _library[key].location, _library[key].info._metadata, _library[key].metadata._metadata) for key in _library]
        #print tracks
        pickle.dump(tracks, foo)
        foo.close()
        #foo = open(os.path.join(_root_folder, "playlists.data"))
        #pickle.dump(__playlists, foo)

def add_file(filename):
    if os.path.exists(filename):
        if filename not in _library and filename.endswith('.mp3'):
            ii = load_file(filename)
            _library[filename] = ii
            
    
def get_folders():
    return _folders

def get_sessions():
    sess_folder = os.path.join(_root_folder, "sessions")
    sessions = []
    for sess in os.listdir(sess_folder):
        if sess.endswith('.m3u'):
            name, ext = os.path.splitext(sess)
            sessions.append((name, os.path.join(sess_folder, sess)))
    return sessions

def get_playlists():
    sess_folder = os.path.join(_root_folder, "playlists")
    sessions = []
    for sess in os.listdir(sess_folder):
        if sess.endswith('.m3u'):
            name, ext = os.path.splitext(sess)
            sessions.append((name, os.path.join(sess_folder, sess)))
    return sessions

def get_session_by_name(path):
    tracks = []
    if os.path.exists(path):
        foo = open(path, 'rU')
        #print foo.readlines()
        for bar in foo.readlines():
            #print bar
            tracks.append(get_track_by_name(bar.strip('\n'), True))
    return tracks

def save_to_current_session(track):
    sess_folder = os.path.join(_root_folder, "sessions")
    current_session = os.path.join(sess_folder, 'Current Session.m3u')
    if not os.path.exists(current_session):
        #if track.location is not None:
        foo = open(current_session, 'w')
    else:
        foo = open(current_session, 'a')

    if track.location is not None:
        foo.write(track.location+'\n')
    foo.close()

def save_current_session():
    sess_folder = os.path.join(_root_folder, "sessions")
    current_session = os.path.join(sess_folder, 'Current Session.m3u')
    if os.path.exists(current_session):
        foo = open(current_session, 'rU').readlines()
        bar = [x for x in foo if x != '\n']
        new_session_filename = "DJ Set - " + time.strftime("%a, %d %b %Y %H-%M")
        new_session_full_path = os.path.join(sess_folder, new_session_filename)

        if os.path.exists(new_session_full_path + '.m3u'):
            index = 1
            path = new_session_full_path
        
            while os.path.exists(path+" - "+ str(index)+ '.m3u'):
                index += 1
            new_session_full_path = path+" - "+str(index)
        session = open(new_session_full_path + '.m3u', 'w')
        for x in bar:
            session.write(x)
        session.close()
        os.unlink(current_session)

def get_filters():
    return {

        "RHYTHM: Straight": FilteredPlaylist(_library,
                                            'comments',
                                            'contains',
                                            'straight rhythm'),
        "RHYTHM: Shuffle": FilteredPlaylist(_library,
                                            'comments',
                                            'contains',
                                            'shuffle rhythm'),
        "RHYTHM: Swing": FilteredPlaylist(_library,
                                            'comments',
                                            'contains',
                                            'swing rhythm'),

        "12 bar blues": FilteredPlaylist(_library,
                                            'comments',
                                            'contains',
                                            '12 bar blues'),

        
        "GENRE: Blues": FilteredPlaylist(_library,
                                      'genre',
                                      'contains',
                                      'Blues'),



        
        "GENRE: Chicago Blues": FilteredPlaylist(_library,
                                          'genre',
                                          'contains',
                                          'Chicago Blues'),
        
        "GENRE: Delta Blues": FilteredPlaylist(_library,
                                          'genre',
                                          'contains',
                                          'Delta Blues'),
        "GENRE: Slow Jazz": FilteredPlaylist(_library,
                                          'genre',
                                          'contains',
                                          'Slow Jazz'),
        "GENRE: Jazz": FilteredPlaylist(_library,
                                 'genre',
                                 'contains',
                                 'Jazz'),
        "GENRE: Soul": FilteredPlaylist(_library,
                                 'genre',
                                 'contains',
                                 'Soul'),
        "GENRE: Funk": FilteredPlaylist(_library,
                                 'genre',
                                 'contains',
                                 'Funk'),
        #"STYLE: Slow Drag": FilteredPlaylist(_library,
        #                              'style',
        #                              'contains',
        #                              'Slow Drag'),
        #"STYLE: Ballroom": FilteredPlaylist(_library,
        #                             'style',
        #                             'contains',
        #                             'Ballroom'),
        #"STYLE: Jookin'": FilteredPlaylist(_library,
        #                            'style',
        #                            'contains',
        #                            'Jookin\''),
        #"STYLE: Struttin'": FilteredPlaylist(_library,
        #                              'style',
        #                              'contains',
        #                              'Struttin\''),
        "PLAY AT: Early in the night": FilteredPlaylist(_library,
                                  'play_at',
                                  'contains',
                                  'Early in the night'),
        "PLAY AT: Early to middle of the night": FilteredPlaylist(_library,
                                                         'play_at',
                                                         'contains',
                                                         'Early to middle of the night'),
        "PLAY AT: Middle of the night": FilteredPlaylist(_library,
                                                'play_at',
                                                'contains',
                                                'Middle of the night'),
        "PLAY AT: Middle to late night": FilteredPlaylist(_library,
                                                 'play_at',
                                                 'contains',
                                                 'Middle to late night'),
        "PLAY AT: Late night": FilteredPlaylist(_library,
                                       'play_at',
                                       'contains',
                                       'Late night'),



    }

def get_track_by_name(path, load = False):
    if path in _library:
        return _library[path]
    if load:
        return load_file(path)
    return None


def get_tracks():
    return _library.values()

def get_master_playlist():
    return MainPlaylist(_library)



if __name__ == '__main__':
    init('/Users/jihemme/.pydjay')
    #for xx in os.listdir('/Volumes/Media/Blues MP3'):
    #    yy = os.path.join('/Volumes/Media/Blues MP3', xx)
    #    print yy
    #    add_file(yy)
    #save()
    print _library
