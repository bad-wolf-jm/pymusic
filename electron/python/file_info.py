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
