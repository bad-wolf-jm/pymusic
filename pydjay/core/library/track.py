import mutagen.mp3
import mutagen.id3
import mutagen.mp4
import os

"""
__info_fields__ = [
    'length',
    'file',
    'bitrate',
    'samplerate',
    'channels',
    'file_type',
    'file_mimetype',
    'date_added',
    'file_timestamp'
]

__track_fields__ = [
    'title',
    'artist',
    'album',
    'album_artist',
    'album_cover',
    'genre',
    'grouping',
    'category',
    'description',
    'comments',
    'encoder',


    
    'source',
    
    'mood',
    'style',
    'vocal',

    'loved',
    'rating',
    'speed_feel',
    
    'bpm',
    'length',
    'file',

    'phrasing',

    'play_times',
    'waveform',
    'play_next'
]



__id3_tag_names__ =  {
    'title':        'TIT2',
    'artist':       'TPE1',
    'album':        'TALB',
    'album_artist': 'TPE2',
    'album_cover':  None,
    'genre':        'TCON',
    'grouping':     None,
    'category':     None,
    'description':  None,


    'encoder':     'TENC'
}

#class TrackInfo
"""

class TrackInfo(object):
    def __init__(self, info):
        super(TrackInfo, self).__init__()
        self._metadata = info


    def __get(self, field_name, default = None):
        return self._metadata.get(field_name, None)

    def __set(self, field_name, value):
        self._metadata[field_name] = value


    bitrate       = property(lambda self: self.__get('bitrate'))
    samplerate    = property(lambda self: self.__get('samplerate'))
    channels      = property(lambda self: self.__get('channels'))
    file_type     = property(lambda self: self.__get('file_type'))
    #date_file_modified = property(lambda self: self.__get('album_cover'))

    @property
    def length(self):
        foo = self._metadata.get('length', None)
        #return foo
        if foo is None:
            return 0
        if self.start_time is not None:
            if self.end_time is not None:
                return self.end_time - self.start_time
            else:
                return foo * 1000000 - self.start_time
        else:
            if self.end_time is not None:
                return self.end_time
            else:
                return foo * 1000000

    @property
    def stream_length(self):
        foo = self._metadata.get('length', None)
        if foo is not None:
            return foo * 1000000

    #@property
    #def location(self):
    #    return self._metadata.get('location', None)

    #@property
    #def bitrate(self):
    #    return self._metadata.get('bitrate', None)

    #@property
    #def samplerate(self):
    #    return self._metadata.get('samplerate', None)

    #@property
    #def channels(self):
    #    return self._metadata.get('channels', None)

    #@property
    #def file_type(self):
    #    return self._metadata.get('file_type', None)

    @property
    def mimetype(self):
        return self._metadata.get('mimetype', None)

    #@property
    #def date_added(self):
    #    return self._metadata.get('date_added', None)

    @property
    def timestamp(self):
        return self._metadata.get('timestamp', None)

    @property
    def encoder(self):
        return self._metadata.get('encoder', None)


    def get_start_time(self):
        
        foo = self._metadata.get('start_time', None)
        bar = self._metadata.get('end_time', None)
        if None not in [foo, bar]:
            if foo > bar or foo <= 0 or foo >= self.stream_length:
                return None
        return foo
        
    def set_start_time(self, value):
        #print value
        self._metadata['start_time'] = value
    start_time = property(get_start_time, set_start_time)

    def get_end_time(self):
        foo = self._metadata.get('start_time', None)
        bar = self._metadata.get('end_time', None)
        if None not in [foo, bar]:
            if foo > bar or bar >= self.stream_length or bar <= 0:
                return None
        return bar

#        return self._metadata.get('end_time', None)
    def set_end_time(self, value):
        #print value
        self._metadata['end_time'] = value
    end_time = property(get_end_time, set_end_time)

        
class TrackMetadata(object):
    def __init__(self, metadata):
        object.__init__(self)
        self._metadata = metadata
        #self._metadata['title']        = metadata.get('title', None)
        #self._metadata['artist']       = metadata.get('artist', None)
        #self._metadata['album']        = metadata.get('album', None)
        #self._metadata['album_artist'] = metadata.get('album_artist', None)
        #self._metadata['album_cover']  = metadata.get('album_cover', None)
        #self._metadata['genre']        = metadata.get('genre', None)
        #self._metadata['grouping']     = metadata.get('grouping', None)
        #self._metadata['category']     = metadata.get('category', None)
        #self._metadata['description']  = metadata.get('description', None)
        #self._metadata['comments']     = metadata.get('comments', None)
        #self._metadata['source']       = metadata.get('source', None)
        #self._metadata['mood']         = metadata.get('mood', None)
        #self._metadata['style']        = metadata.get('style', None)
        #self._metadata['vocal']        = metadata.get('vocal', None)
        #self._metadata['loved']        = metadata.get('loved', None)
        #self._metadata['rating']       = metadata.get('rating', None)
        #self._metadata['speed_feel']   = metadata.get('speed_feel', None)
        #self._metadata['bpm']          = metadata.get('bpm', None)
        ##self._length      = None
        ##self._file = None
        #self._metadata['phrasing']     = metadata.get('phrasing', [])
        #self._metadata['num_phrases']  = metadata.get('num_phrases', None)
        #self._metadata['play_times']   = metadata.get('play_times', [])
        #self._metadata['waveform']     = metadata.get('waveform', [])
        #self._metadata['play_next']    = metadata.get('play_next', [])


    def __get(self, field_name, default = None):
        return self._metadata.get(field_name, None)

    def __set(self, field_name, value):
        self._metadata[field_name] = value


    title       = property(lambda self: self.__get('title'))
    artist      = property(lambda self: self.__get('artist'))
    album       = property(lambda self: self.__get('album'))
    album_cover = property(lambda self: self.__get('album_art'))
    genre       = property(lambda self: self.__get('genre'))
    style       = property(lambda self: self.__get('style'))
    play_at     = property(lambda self: self.__get('play_at'))
    vocal       = property(lambda self: self.__get('vocal'))
    rating      = property(lambda self: self.__get('rating'))
    bpm         = property(lambda self: self.__get('bpm'))
    comments    = property(lambda self: self.__get('comments'))
    loved       = property(lambda self: self.__get('loved'),
                           lambda self, value: self.__get('loved', value))
    play_times  = property(lambda self: self.__get('play_times'))
    
    #@property
    #def title(self):
    #    return self._metadata.get('title', None)

    #@property
    #def artist(self):
    #    return self._metadata.get('artist', None)

    #@property
    #def album(self):
    #    return self._metadata.get('album', None)

    @property
    def album_artist(self):
        return self._metadata.get('album_artist', None)

    #@property
    #def album_cover(self):
    #    return self._metadata.get('album_art', None)

    #@property
    #def genre(self):
    #    return self._metadata.get('genre', None)

    @property
    def grouping(self):
        return self._metadata.get('grouping', None)

    @property
    def category(self):
        return self._metadata.get('category', None)

    @property
    def description(self):
        return self._metadata.get('description', None)

    @property
    def year(self):
        return self._metadata.get('year', None)

    
    #@property
    #def comments(self):
    #    return self._metadata.get('comments', None)

    @property
    def source(self):
        return self._metadata.get('source', None)

    @property
    def mood(self):
        return self._metadata.get('mood', None)

    #@property
    #def style(self):
    #    return self._metadata.get('style', None)

    #@property
    #def play_at(self):
    #    return self._metadata.get('play_at', None)

    #@property
    #def vocal(self):
    #    return self._metadata.get('vocal', None)

    #def get_loved(self):
    #    return self._metadata.get('loved', False)
    #def set_loved(self, value):
    #    self._metadata['loved'] = value
    #loved = property(get_loved, set_loved)
    
    ##@property
    #def rating(self):
    #    return self._metadata.get('rating', None)

    @property
    def speed_feel(self):
        return self._metadata.get('speed_feel', None)

    #@property
    #def bpm(self):
    #    return self._metadata.get('bpm', None)

    @property
    def phrasing(self):
        return self._metadata.get('phrasing', [])

    @property
    def phrase_length(self):
        return self._metadata.get('phrase_length', [])

    @property
    def num_phrases(self):
        return self._metadata.get('num_phrases', None)

    #@property
    #def play_times(self):
    #    return self._metadata.get('play_times', None)
    def add_play_time(self, time):
        if self.play_times is None:
            self._metadata['play_times'] = [time]
        else:
            self._metadata['play_times'].append(time)
            self._metadata['play_times'].sort()

    @property
    def play_count(self):
        return len(self.play_times) if self.play_times is not None else 0

    @property
    def last_played(self):
        return self.play_times[-1] if self.play_times is not None else None
    

    def get_waveform(self):
        return self._metadata.get('waveform', None)
    def set_waveform(self, value):
        self._metadata['waveform'] = value
    waveform = property(get_waveform, set_waveform)




    
    @property
    def play_next(self):
        return self._metadata.get('play_next', None)

    def add_play_next(self, track):
        if self.play_next is not None:
            self.play_next.add(track.location)
        else:
            self._metadata['play_next'] = set([track.location])


class Track:
    def __init__(self, filename, info, metadata):
        self.location = filename
        self.info     = TrackInfo(info)
        self.metadata = TrackMetadata(metadata)
        self._index   = []
        fields = ['artist', 'album', 'album_artist', 'genre', 'title',
                  'grouping', 'category', 'description',
                  'comments', 'mood', 'style',
                  'vocal', 'speed_feel']
        #list_of_words = [x.lower() for x in list_of_words]
        for f in fields:
            try:
                self._index.append(unicode(getattr(self.metadata, f)).lower())
            except:
                pass
            if self.metadata.rating is not None:
                self._index.append('@rat=%s'%self.metadata.rating)
            if self.metadata.loved:
                self._index.append('@loved')
            self._index.extend(['@bpm~', '@bpm<', '@bpm>'])    
            #for w in list_of_words:
            #    if w not in bar:
            #        break
            #else:
            #    return True
        #return False


    def matches(self, list_of_words):
        fields = ['artist', 'album', 'album_artist', 'genre', 'title',
                  'grouping', 'category', 'description',
                  'comments', 'mood', 'style',
                  'vocal', 'speed_feel']
        list_of_words = [x.lower() for x in list_of_words]
        ret_val = False
        for w in list_of_words:

            if w.startswith('@bpm'):
                x = w[4:]
                if len(x) >= 2:
                    comp = x[0]
                    try:
                        bpm = int(x[1:])
                    except:
                        bpm = None
                    if bpm is not None:
                        t_bpm = self.metadata.bpm
                        if t_bpm is not None:
                            if comp == '<':
                                if t_bpm < bpm:
                                    return True
                            elif comp == '>':
                                if t_bpm > bpm:
                                    return True
                            elif comp == '~':
                                if t_bpm > bpm * 0.8 and t_bpm < bpm * 1.2:
                                    return True
            for f in self._index:
                if w in f:
                    break
            else:
                return False
        return True
        
    def __lt__(self, other):
        #print 'cmp'
        if other is None:
            return False

        for key in ['title', 'artist', 'album']:
            if getattr(self.metadata, key) < getattr(other.metadata, key):
                return True
            elif getattr(self.metadata, key) > getattr(other.metadata, key):
                return False
                
        return False

    def __le__(self, other):
        #print 'cmpe'
        if other is None:
            return False

        for key in ['title', 'artist', 'album']:
            if getattr(self.metadata, key) <= getattr(other.metadata, key):
                return True
            elif getattr(self.metadata, key) > getattr(other.metadata, key):
                return False
                
        return False

    def __gt__(self, other):
        #print 'cmp'
        if other is None:
            return True

        for key in ['title', 'artist', 'album']:
            if getattr(self.metadata, key) > getattr(other.metadata, key):
                return True
            elif getattr(self.metadata, key) < getattr(other.metadata, key):
                return False
        return False

    def __ge__(self, other):
        #pint 'cmpe'
        if other is None:
            return True
        for key in ['title', 'artist', 'album']:
            if getattr(self.metadata, key) >= getattr(other.metadata, key):
                return True
            elif getattr(self.metadata, key) < getattr(other.metadata, key):
                return False
        return False

    def __eq__(self, other):
        #print 'cmpe'
        if other is None:
            return False
        for key in ['title', 'artist', 'album']:
            if getattr(self.metadata, key) == getattr(other.metadata, key):
                return True
        return False


    def __repr__(self):
        return unicode(self.metadata.title).encode('ascii', 'xmlcharrefreplace') + ' - ' + unicode(self.metadata.artist).encode('ascii', 'xmlcharrefreplace')



def load_mp4_file(filename):
    #print 'LOADING MO$ FILE:',  filename
    try:
        if not (filename.endswith('.mp4') or filename.endswith('.m4a')):
            print "NOT THE RIGHT EXTENSION"
            print "'"+filename+"'"
            return None
    except UnicodeDecodeError:
        if not (filename.decode('utf-8').endswith('.mp4') or filename.decode('utf-8').endswith('.m4a')):
            print "NOT THE RIGHT EXTENSION"
            print "'"+filename+"'"
            return None
        
    try:
        bar = mutagen.mp4.MP4(filename)
        #print bar.tags.pprint()
        #print bar.tags.keys()
        info = {
            'length':     int(bar.info.length*1000),
            #'location':   yy,
            'bitrate':    bar.info.bitrate,
            'samplerate': bar.info.sample_rate,
            'channels':   bar.info.channels,
            #'encoder':    bar.tags['TENC'] if 'TENC' in bar.tags else ""
        }
        
        #get metadata
        
        metadata = {}


        text_fields = [
            ('\xa9grp', 'grouping'),
            ('\xa9nam', 'title'),
            ('\xa9ART', 'artist'),
            ('aArt',    'album_artist'),
            ('\xa9alb', 'album'),
            #('TMOO', 'mood'),
            #('TLAN', 'language'),
            ('catg',    'category'),
            ('desc',    'description'),
            ('\xa9gen', 'genre')
        ]

        for id3, field in text_fields:
            foo = bar.tags.get(id3)
            #print foo
            metadata[field] = None
            if foo is not None and len(foo) > 0:
                metadata[field] = unicode(foo[0])
            
        foo = bar.tags.get('tmpo')
        metadata['bpm'] = None
        if foo is not None and len(foo) > 0:
            metadata['bpm'] = foo[0]

        foo = bar.tags.get('\xa9day')
        metadata['year'] = None
        if foo is not None and len(foo) > 0:
            metadata['year'] = foo[0]


        foo = bar.tags.get('\xa9cmt')
        metadata['comments'] = None
        if foo is not None and len(foo) > 0:
            com = ''
            for comment in foo:
                #if comment.desc == '':
                com += unicode(comment)
            metadata['comments'] = com


        #pydjay specific tags stored as comments:
        #
        #special_string_tags = [#('COMM:MOOD',      'mood'),
        #                       ('COMM:STYLE',     'style'),
        #                       ('COMM:PLAY_AT',   'play_at'),
        #                       ('COMM:VOCAL',     'vocal'),
        #                       ('COMM:SPEED-FEEL','speed_feel')]
        #for t, field in special_string_tags:
        #    foo = bar.tags.getall(t)
        #    if len(foo) > 0:
        #        value = foo.text[0]
        #        metadata[field] = value

        #foo = bar.tags.getall('COMM:LOVED')
        #if len(foo) > 0:
        #    metadata['loved'] = True
        #else:
        #    metadata['loved'] = False#

        #special_int_tags = [('COMM:NUM-PHRASES',   'num_phrases'),
        #                    ('COMM:RATING',        'rating'),
        #                    ('COMM:PHRASE-LENGTH', 'phrase_length')]
        #for t, field in special_int_tags:
        #    foo = bar.tags.getall(t)
        #    if len(foo) > 0:
        #        value = foo.text[0]
        #        metadata[field] = int(value)
        
        #special_list_tags = ['COMM:PLAY-TIMES', 'COMM:PHRASING']

        #foo = bar.tags.getall('COMM:PLAY-TIMES')
        #if len(foo) > 0:
        #    data = foo[0].split(";")
        #    metadata['play_times'] = data
        #else:
        #    metadata['loved'] = []

        #foo = bar.tags.getall('COMM:PHRASING')
        #if len(foo) > 0:
        #    data = foo[0].split(";")
        #    metadata['play_times'] = [float(x) for x in data]
        #else:
        #    metadata['loved'] = []
        #
        
        foo = bar.tags.get('covr')
        metadata['album_art'] = None
        #print 'cover'
        if foo is not None and len(foo) > 0:
            #com = ''
            #print foo
            for image in foo:
                formats = {mutagen.mp4.AtomDataType.JPEG : "image/jpeg",
                           mutagen.mp4.AtomDataType.PNG  : "image/png"}
                #if image.imageformat in [0, 3]:
                metadata['album_art'] = (formats[image.imageformat], str(image))
                #print image.imageformat, formats[image.imageformat]
                    #break
        return Track(filename, info, metadata)
    except Exception, details:
        print details
        return Track(filename, {}, {})
"""

"""
def save_mp4_file(track):
    #print filename
    if not track.location.endswith('.mp3'):
        return None
    try:
        bar = mutagen.mp4.MP4(track.location)
        info = {
            'length':     int(bar.info.length*1000),
            #'location':   yy,
            'bitrate':    bar.info.bitrate,
            'samplerate': bar.info.sample_rate,
            'channels':   bar.info.channels,
            #'encoder':    bar.tags['TENC'] if 'TENC' in bar.tags else ""
        }
        
        #get metadata
        
        metadata = {}


        text_fields = [
            ('grouping',     '\xa9grp'), #mutagen.id3.TIT1),
            ('title',        '\xa9nam'), #mutagen.id3.TIT2),
            ('artist',       '\xa9ART'), #mutagen.id3.TPE1),
            ('album_artist', 'aArt'), #mutagen.id3.TPE2),
            ('album',        '\xa9alb'), #mutagen.id3.TALB),
            #('mood',         ''), #mutagen.id3.TMOO),
            #('language',     ''), #mutagen.id3.TLAN),
            ('category',     'catg'), #mutagen.id3.TCAT),
            ('description',  'desc'), #mutagen.id3.TDES),
            ('genre',        '\xa9gen'), #mutagen.id3.TCON)
            ('bpm',          'tmpo'),
            ('comments',     '\xa9cmy'),
            ('year',         '\xa9day')
        ]
        #print bar
        for id3, field in text_fields:
            foo = track.metadata._metadata.get(id3, None)
            if foo is not None:
                bar.tags[field] = [unicode(foo)]
            #metadata[field] = None
            ##print foo
            #if len(foo) > 0:
            #    metadata[field] = unicode(foo[0])
            
        #foo = bar.tags.getall('TBPM')
        #if track.metadata.bpm is not None:
        #    bar.tags.add(mutagen.id3.TBPM(encoding = 3, text = str(track.metadata.bpm)))
        #metadata['bpm'] = None
        #if len(foo) > 0:
        #    metadata['bpm'] = +foo[0]

        #foo = bar.tags.getall('TDRC')
        #metadata['year'] = None
        #if len(foo) > 0:
        #    metadata['year'] = unicode(foo[0].text[0])
        
        #if track.metadata.year is not None:
        #    bar.tags.add(mutagen.id3.TDRC(encoding = 3, text = str(track.metadata.year)))


        ##$foo = bar.tags.getall('COMM')
        #$metadata['comments'] = None
        ##print foo
        #if len(foo) > 0:
        #    com = ''
        #    for comment in foo:
        #        #print 'COMMENT::', comment
        #        if comment.desc == '':
        #            com += unicode(comment)
        #        #print com
        #    metadata['comments'] = com
        #if track.metadata.comments is not None:
        #    bar.tags.add(mutagen.id3.COMM(encoding = 3, text = track.metadata.comments))


        #pydjay specific tags stored as comments:
        #special_string_tags = [#('COMM:MOOD',      'mood'),
        #                       ('COMM:STYLE',     'style'),
        #                       ('COMM:PLAY_AT',   'play_at'),
        #                       ('COMM:VOCAL',     'vocal'),
        #                       ('COMM:SPEED-FEEL','speed_feel')]
        #if track.metadata.style is not None:
        #    bar.tags.add(mutagen.id3.COMM(encoding = 3, desc = "STYLE", text = track.metadata.style))

        #if track.metadata.play_at is not None:
        #    bar.tags.add(mutagen.id3.COMM(encoding = 3, desc = "PLAY_AT", text = track.metadata.play_at))

        #if track.metadata.vocal is not None:
        #    bar.tags.add(mutagen.id3.COMM(encoding = 3, desc = "VOCAL", text =track.metadata.vocal))
        #if track.metadata.speed_feel is not None:
        #    bar.tags.add(mutagen.id3.COMM(encoding = 3, desc = "SPEED_FEEL", text = track.metadata.speed_feel))


        #for t, field in special_string_tags:
        #    foo = bar.tags.getall(t)
        #    if len(foo) > 0:
        #        value = foo.text[0]
        #        metadata[field] = value

        #foo = bar.tags.getall('COMM:LOVED')
        #if len(foo) > 0:
        #    metadata['loved'] = True
        #else:
        #    metadata['loved'] = False

        #special_int_tags = [('COMM:NUM-PHRASES',   'num_phrases'),
        #                    ('COMM:RATING',        'rating'),
        #                    ('COMM:PHRASE-LENGTH', 'phrase_length')]
        #for t, field in special_int_tags:
        #    foo = bar.tags.getall(t)
        #    if len(foo) > 0:
        #        value = foo.text[0]
        #        metadata[field] = int(value)
        
        #special_list_tags = ['COMM:PLAY-TIMES', 'COMM:PHRASING']
        #if track.metadata.loved:
        #    bar.tags.add(mutagen.id3.COMM(encoding = 3, desc = "LOVED", text = "TRUE"))
        #else:
        #    bar.tags.add(mutagen.id3.COMM(encoding = 3, desc = "LOVED", text = "FALSE"))

        #foo = bar.tags.getall('COMM:PLAY-TIMES')
        #if track.metadata.play_times is not None:
        #    bar.tags.add(mutagen.id3.COMM(encoding = 3, desc = "PLAY_TIMES", text = ";".join(track.metadata.play_times)))
        #if len(foo) > 0:
        #    data = foo[0].split(";")
        #    metadata['play_times'] = data
        #else:
        #    metadata['loved'] = []

        #foo = bar.tags.getall('COMM:PHRASING')
        #if len(foo) > 0:
        #    data = foo[0].split(";")
        #    metadata['play_times'] = [float(x) for x in data]
        #else:
        #    metadata['loved'] = []

        
        #foo = bar.tags.getall('APIC')
        #metadata['album_art'] = None
        #if len(foo) > 0:
        #    #com = ''
        #    for image in foo:
        #        if image.type in [0, 3]:
        #            metadata['album_art'] = (image.mime, image.data)
        #            break
        #try:
        #    del bar.tags['APIC:']
        #except:
        #    pass
        #print bar
        #return Track(filename, info, metadata)
        bar.tags.save(track.location)
    except Exception, details:
        print details
        #return Track(filename, {}, {})


    

    

def load_mp3_file(filename):
    #print filename
    if not filename.endswith('.mp3'):
        return None
    try:
        bar = mutagen.mp3.MP3(filename)
        #try:
        #    del bar['APIC']
        #except:
        #    pass
        #print bar.pprint()
        #print bar
        info = {
            'length':     int(bar.info.length*1000),
            #'location':   yy,
            'bitrate':    bar.info.bitrate,
            'samplerate': bar.info.sample_rate,
            'channels':   bar.info.channels,
            #'encoder':    bar.tags['TENC'] if 'TENC' in bar.tags else ""
        }
        
        #get metadata
        
        metadata = {}


        text_fields = [
            ('TIT1', 'grouping'),
            ('TIT2', 'title'),
            ('TPE1', 'artist'),
            ('TPE2', 'album_artist'),
            ('TALB', 'album'),
            ('TMOO', 'mood'),
            ('TLAN', 'language'),
            ('TCAT', 'category'),
            ('TDES', 'description'),
            ('TCON', 'genre')
        ]
        #print bar
        for id3, field in text_fields:
            foo = bar.tags.getall(id3)
            metadata[field] = None
            #print foo
            if len(foo) > 0:
                metadata[field] = unicode(foo[0])
            
        foo = bar.tags.getall('TBPM')
        metadata['bpm'] = None
        if len(foo) > 0:
            metadata['bpm'] = +foo[0]

        foo = bar.tags.getall('TDRC')
        metadata['year'] = None
        if len(foo) > 0:
            metadata['year'] = unicode(foo[0].text[0])


        foo = bar.tags.getall('COMM')
        metadata['comments'] = None
        #print foo
        if len(foo) > 0:
            com = ''
            for comment in foo:
                #print 'COMMENT::', comment
                if comment.desc == '':
                    com += unicode(comment)
                #print com
            metadata['comments'] = com


        #pydjay specific tags stored as comments:
        special_string_tags = [#('COMM:MOOD',      'mood'),
                               ('COMM:STYLE',     'style'),
                               ('COMM:PLAY_AT',   'play_at'),
                               ('COMM:VOCAL',     'vocal'),
                               ('COMM:SPEED-FEEL','speed_feel')]
        for t, field in special_string_tags:
            foo = bar.tags.getall(t)
            if len(foo) > 0:
                value = foo[0].text[0]
                metadata[field] = value

        foo = bar.tags.getall('COMM:LOVED')
        if len(foo) > 0 and foo[0].text[0] == 'TRUE':
            metadata['loved'] = True
        else:
            metadata['loved'] = False

        special_int_tags = [('COMM:NUM-PHRASES',   'num_phrases'),
                            ('COMM:RATING',        'rating'),
                            ('COMM:PHRASE-LENGTH', 'phrase_length')]
        for t, field in special_int_tags:
            foo = bar.tags.getall(t)
            if len(foo) > 0:
                value = foo[0].text[0]
                metadata[field] = int(value)
        
        #special_list_tags = ['COMM:PLAY-TIMES', 'COMM:PHRASING']

        foo = bar.tags.getall('COMM:PLAY-TIMES')
        if len(foo) > 0:
            data = foo[0].split(";")
            metadata['play_times'] = data
        else:
            metadata['play_times'] = []

        foo = bar.tags.getall('COMM:PHRASING')
        if len(foo) > 0:
            data = foo[0].split(";")
            metadata['phrasing'] = [float(x) for x in data]
        else:
            metadata['phrasing'] = []

        
        foo = bar.tags.getall('APIC')
        metadata['album_art'] = None
        if len(foo) > 0:
            #com = ''
            for image in foo:
                if image.type in [0, 3]:
                    metadata['album_art'] = (image.mime, image.data)
                    break
                else:
                    print image.type
        #try:
        #    del bar.tags['APIC:']
        #except:
        #    pass
        #print bar
        return Track(filename, info, metadata)
    except Exception, details:
        print "FOOBAR", details
        return Track(filename, {}, {})



def save_mp3_file(track):
    #print filename
    if not track.location.endswith('.mp3'):
        return None
    try:
        bar = mutagen.mp3.MP3(track.location)
        info = {
            'length':     int(bar.info.length*1000),
            #'location':   yy,
            'bitrate':    bar.info.bitrate,
            'samplerate': bar.info.sample_rate,
            'channels':   bar.info.channels,
            #'encoder':    bar.tags['TENC'] if 'TENC' in bar.tags else ""
        }
        
        #get metadata
        
        metadata = {}


        text_fields = [
            ('grouping',     mutagen.id3.TIT1),
            ('title',        mutagen.id3.TIT2),
            ('artist',       mutagen.id3.TPE1),
            ('album_artist', mutagen.id3.TPE2),
            ('album',        mutagen.id3.TALB),
            ('mood',         mutagen.id3.TMOO),
            ('language',     mutagen.id3.TLAN),
            ('category',     mutagen.id3.TCAT),
            ('description',  mutagen.id3.TDES),
            ('genre',        mutagen.id3.TCON)
        ]
        #print bar
        for id3, field in text_fields:
            foo = track.metadata._metadata.get(id3, None)
            if foo is not None:
                bar.tags.add(field(encoding = 3, text = foo))
            #metadata[field] = None
            ##print foo
            #if len(foo) > 0:
            #    metadata[field] = unicode(foo[0])
            
        #foo = bar.tags.getall('TBPM')
        if track.metadata.bpm is not None:
            bar.tags.add(mutagen.id3.TBPM(encoding = 3, text = str(track.metadata.bpm)))
        #metadata['bpm'] = None
        #if len(foo) > 0:
        #    metadata['bpm'] = +foo[0]

        #foo = bar.tags.getall('TDRC')
        #metadata['year'] = None
        #if len(foo) > 0:
        #    metadata['year'] = unicode(foo[0].text[0])
        
        if track.metadata.year is not None:
            bar.tags.add(mutagen.id3.TDRC(encoding = 3, text = str(track.metadata.year)))


        ##$foo = bar.tags.getall('COMM')
        #$metadata['comments'] = None
        ##print foo
        #if len(foo) > 0:
        #    com = ''
        #    for comment in foo:
        #        #print 'COMMENT::', comment
        #        if comment.desc == '':
        #            com += unicode(comment)
        #        #print com
        #    metadata['comments'] = com
        if track.metadata.comments is not None:
            bar.tags.add(mutagen.id3.COMM(encoding = 3, text = track.metadata.comments))


        #pydjay specific tags stored as comments:
        #special_string_tags = [#('COMM:MOOD',      'mood'),
        #                       ('COMM:STYLE',     'style'),
        #                       ('COMM:PLAY_AT',   'play_at'),
        #                       ('COMM:VOCAL',     'vocal'),
        #                       ('COMM:SPEED-FEEL','speed_feel')]
        if track.metadata.style is not None:
            bar.tags.add(mutagen.id3.COMM(encoding = 3, desc = "STYLE", text = track.metadata.style))

        if track.metadata.play_at is not None:
            bar.tags.add(mutagen.id3.COMM(encoding = 3, desc = "PLAY_AT", text = track.metadata.play_at))

        if track.metadata.vocal is not None:
            bar.tags.add(mutagen.id3.COMM(encoding = 3, desc = "VOCAL", text =track.metadata.vocal))
        if track.metadata.speed_feel is not None:
            bar.tags.add(mutagen.id3.COMM(encoding = 3, desc = "SPEED_FEEL", text = track.metadata.speed_feel))


        #for t, field in special_string_tags:
        #    foo = bar.tags.getall(t)
        #    if len(foo) > 0:
        #        value = foo.text[0]
        #        metadata[field] = value

        #foo = bar.tags.getall('COMM:LOVED')
        #if len(foo) > 0:
        #    metadata['loved'] = True
        #else:
        #    metadata['loved'] = False

        #special_int_tags = [('COMM:NUM-PHRASES',   'num_phrases'),
        #                    ('COMM:RATING',        'rating'),
        #                    ('COMM:PHRASE-LENGTH', 'phrase_length')]
        #for t, field in special_int_tags:
        #    foo = bar.tags.getall(t)
        #    if len(foo) > 0:
        #        value = foo.text[0]
        #        metadata[field] = int(value)
        
        #special_list_tags = ['COMM:PLAY-TIMES', 'COMM:PHRASING']
        if track.metadata.loved:
            bar.tags.add(mutagen.id3.COMM(encoding = 3, desc = "LOVED", text = "TRUE"))
        else:
            bar.tags.add(mutagen.id3.COMM(encoding = 3, desc = "LOVED", text = "FALSE"))

        if track.metadata.rating is not None:
            bar.tags.add(mutagen.id3.COMM(encoding = 3, desc = "RATING", text = str(track.metadata.rating)))
        else:
            bar.tags.add(mutagen.id3.COMM(encoding = 3, desc = "RATING", text = "0"))

        #foo = bar.tags.getall('COMM:PLAY-TIMES')
        if track.metadata.play_times is not None:
            bar.tags.add(mutagen.id3.COMM(encoding = 3, desc = "PLAY_TIMES", text = ";".join(track.metadata.play_times)))
        #if len(foo) > 0:
        #    data = foo[0].split(";")
        #    metadata['play_times'] = data
        #else:
        #    metadata['loved'] = []

        #foo = bar.tags.getall('COMM:PHRASING')
        #if len(foo) > 0:
        #    data = foo[0].split(";")
        #    metadata['play_times'] = [float(x) for x in data]
        #else:
        #    metadata['loved'] = []

        
        #foo = bar.tags.getall('APIC')
        #metadata['album_art'] = None
        if track.metadata.album_cover is not None:
            type_ = track.metadata.album_cover[0]
            data  = track.metadata.album_cover[1]
            bar.tags.add(mutagen.id3.APIC(mime = type_, data = data))
        #else:
        #    print "NO COVER"
        #if len(foo) > 0:
        #    #com = ''
        #    for image in foo:
        #        if image.type in [0, 3]:
        #            metadata['album_art'] = (image.mime, image.data)
        #            break
        #try:
        #    del bar.tags['APIC:']
        #except:
        #    pass
        #print bar
        #return Track(filename, info, metadata)
        #print track.location
        bar.tags.save(track.location)
        #bar = mutagen.mp3.MP3(track.location)
        #print bar.pprint()
        #print track.location
        #print bar.pprint()
        #print 
    except Exception, details:
        print 'FOOFOO', details
        #return Track(filename, {}, {})

def load_file(filename):
    if filename.endswith('.mp3'):
        return load_mp3_file(filename)
    elif (filename.endswith('.mp4') or filename.endswith('.m4a')):
        return load_mp4_file(filename)
    return None #Track(filename, {}, {})
    
        
if __name__ == '__main__':
    tr = load_mp4_file('test_mp4_tag.mp4')
    try:
        del tr.metadata._metadata['album_art']
    except:
        pass
    tr.metadata._metadata['grouping']     = 'NEW GROUPING 2'
    tr.metadata._metadata['title']        = 'NEW TITLE 2'
    tr.metadata._metadata['artist']       = 'NEW ARTIST 2'
    tr.metadata._metadata['album_artist'] = 'NEW ALBUM_ARTIST 2'
    tr.metadata._metadata['album']        = 'NEW ALBUM 2'
    tr.metadata._metadata['mood']         = 'NEW MOOD 2'
    tr.metadata._metadata['language']     = 'NEW LANGUAGE 2'
    tr.metadata._metadata['category']     = 'NEW CATEGORY 2'
    tr.metadata._metadata['description']  = 'NEW DESCRIPTION 2'
    tr.metadata._metadata['genre']        = 'NEW GENRE 2'

    tr.metadata._metadata['bpm']          = '000'
    tr.metadata._metadata['year']         = '9999'
    tr.metadata._metadata['comments']     = 'NEW comments'
    tr.metadata._metadata['syle']         = 'NEW style'
    tr.metadata._metadata['play_at']      = 'NEW PLAY_AT'
    tr.metadata._metadata['vocal']        = 'NEW VOCAL'
    tr.metadata._metadata['speed_feel']   = 'slow'
    tr.metadata._metadata['loved']        = False
    tr.metadata._metadata['play_times']   = ['12:30', '11:23']

    
    save_mp4_file(tr)
    tr = load_mp4_file('test_mp4_tag.mp4')   
    try:
        del tr.metadata._metadata['album_art']
    except:
        pass
     
    print tr.metadata._metadata
    
    #for xx in os.listdir('/Volumes/Media/Blues MP3'):
    #    zz = load_file(os.path.join('/Volumes/Media/Blues MP3', xx))
    #    if zz is not None:
    #        del zz.metadata._metadata['album_art']
    #        print zz.metadata._metadata
