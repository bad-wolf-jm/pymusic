import mutagen.mp3
import mutagen.id3
import mutagen.mp4
import os
import json
import sys

def load_mp3_file(filename):
    # print filename
    if not filename.endswith('.mp3'):
        return None
    try:
        bar = mutagen.mp3.MP3(filename)
        stat = os.stat(filename)
        return {
            'length':     int(bar.info.length * 1000000000),
            'bitrate':    bar.info.bitrate,
            'samplerate': bar.info.sample_rate,
            'channels':   bar.info.channels,
            'file_size':  stat.st_size
        }
    except:
        return {}


if __name__ == '__main__':
    print (json.dumps(load_mp3_file(sys.argv[1])))


#
# def load_mp4_file(filename):
#     try:
#         if not (filename.endswith('.mp4') or filename.endswith('.m4a')):
#             print "NOT THE RIGHT EXTENSION"
#             print "'" + filename + "'"
#             return None
#     except UnicodeDecodeError:
#         if not (filename.decode('utf-8').endswith('.mp4') or filename.decode('utf-8').endswith('.m4a')):
#             print "NOT THE RIGHT EXTENSION"
#             print "'" + filename + "'"
#             return None
#
#     try:
#         bar = mutagen.mp4.MP4(filename)
#         # print bar.tags.pprint()
#         # print bar.tags.keys()
#         info = {
#             'length':     int(bar.info.length * 1000),
#             #'location':   yy,
#             'bitrate':    bar.info.bitrate,
#             'samplerate': bar.info.sample_rate,
#             'channels':   bar.info.channels,
#             #'encoder':    bar.tags['TENC'] if 'TENC' in bar.tags else ""
#         }
