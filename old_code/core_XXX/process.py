import os
import threading
from multiprocessing import Process, Queue

try:
    import queue
except ImportError:
    import Queue as queue


class MethodDispatcher(object):
    def __init__(self, *args, **kwargs):
        super(MethodDispatcher, self).__init__(*args, **kw)
        self._methods = {}

    def register_method(self, name, func):
        self._methods[name] = func


    def call_method(self, name, args, kwargs):
        m = self._methods.get(name, None)
        if m is not None:
            try:
                m(*args, **kwargs)
            except:
                print "ERROR CALLING METHOD"

    
class BackgroundProcess(Process, MethodDispatcher):

    def __init__(self, player_name, num_channels = 2, in_queue = None, out_queue = None, *args, **kw):
        super(BackgroundProcess, self).__init__(*args, **kw)
        self._methods = {}
        
    def run_init(self):
        pass

    def stop(self):
        pass

    def remote_call(self, name, *args, **kwargs):
        self.out_queue.put((name, args, kwargs))

    
    def run(self):
        self.run_init()
        self.remote_call('_init')
        while True:
            try:
                command, args, kwargs = self.in_queue.get_nowait()
                if command == 'close':
                    self.stop()
                    break
                try:
                    self.call_method(command, args, kwargs)
                except Exception, details:
                    print 'ERROR CALLING', details
                    break
            except queue.Empty, details:
                pass


class ForegroundProcess(EventDispatcher, MethodDispatcher):
    def __init__(self, player_name, num_channels = 2, *args, **kw):
        super(ForegroundProcess, self).__init__(*args, **kw)
        self.out_queue  = Queue(maxsize = 10)
        self.in_queue   = Queue(maxsize = 1000)
        self.ready_sem = threading.Semaphore(0)
        self._output_process.start()
        self._running = True
        self._foo = threading.Thread(target = self._listen)
        self._foo.start()
        self.stream_time = 0
        self.ready_sem.acquire()

    def _init(self):
        self.ready_sem.release()
        
    def _listen(self):
        while self._running:
            try:
                command, args, kwargs = self.in_queue.get_nowait()
                try:
                    self.call_method(command args, kwargs)
                except Exception, details:
                    print 'y', details
            except queue.Empty, details:
                pass
            finally:
                pass
        
    
