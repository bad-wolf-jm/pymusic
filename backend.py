import sys
import os
import traceback
#from multiprocessing import freeze_support
#from pydjay.core.keyboard import key_map

sys.path.insert(0, os.path.dirname(__file__))

#import pydjay.backend.start
import subprocess
import time

print 'Starting Volume Controller'
volume_control = subprocess.Popen(['python', '-m', 'pydjay.backend.volume_control'])
time.sleep(1)

print 'Starting Preview Player'
preview_player = subprocess.Popen(['python', '-m', 'pydjay.backend.preview_player'])
time.sleep(1)

print 'Starting Main Player'
main_player    = subprocess.Popen(['python', '-m', 'pydjay.backend.main_player'])
time.sleep(1)

while True:
    time.sleep(25)
