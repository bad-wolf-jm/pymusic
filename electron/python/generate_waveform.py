#!/usr/bin/python
import os
import sys
# print os.getcwd()
# sys.path.append('.')
#from pydjay.core.library import load_file as lib_load_file
##from pydjay.core.library.track import Track, save_mp3_file
# import os.getcwd()
#import sys
#import io
#from PIL import Image
#import urllib
#import pymysql
import array

from wavegen import WaveformGenerator
#import pprint
#import subprocess
#import datetime

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


def generate(mp3_path, wave_path):
    try:
        wg = WaveformGenerator(35000)
        #
        wg.set_data_point_callback(_print_time)
        wave_points = wg.generate_waveform(mp3_path)  # = WaveformGenerator(f, 35000)
        try:
            file_ = open(wave_path, 'wb')
            flat_wave = [num for pair in wave_points for num in pair]
            file_.write(str(len(flat_wave)) + '\n')
            arr = array.array('f', flat_wave)
            arr.tofile(file_)
            file_.close()
        except Exception as details:
            print (details)
    except Exception as details:
        print (details)

        #f['waveform'] = None


if __name__ == '__main__':
    mp3_path = sys.argv[1]
    wave_path = sys.argv[2]
    generate(mp3_path, wave_path)
