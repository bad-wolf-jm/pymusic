import zmq
#import json
import threading
import time
from gi.repository import GLib


class PushServer(object):
    """docstring for RPCServer."""

    def __init__(self, name=None, port=9999, **kw):
        object.__init__(self)
        self.__name = name
        self.__port = port
        self.__running = False
        self.__context = zmq.Context()
        self.__socket = self.__context.socket(zmq.PUSH)
        self.__socket.bind("tcp://127.0.0.1:%s" % self.__port)
        self.__message_queue = []
        self._i = 0

    def __process_one_event(self, *args):
        if len(self.__message_queue) > 0:

            try:
                #print event
                event = self.__message_queue[0]
                self.__socket.send_json(event, flags=zmq.NOBLOCK)
                self.__message_queue.pop(0)
                return True
            except zmq.Again as e:
                return True
            except Exception, details:
                print "ERROR", details
                return True
        return True

    def start(self, threaded=True):
        self.__running = True
        if threaded:
            GLib.timeout_add(250, self.__process_one_event)
        else:
            self.run()

    def stop(self):
        self.__running = False

    def push(self, event, *args, **kwargs):
        #print event, args, kwargs
        self.__message_queue = [x for x in self.__message_queue if x['event'] != event]
        self.__message_queue.append({'event': event, 'args': args, 'kwargs': kwargs})


class PushClient(object):
    """docstring for RPCServer."""

    def __init__(self, name=None, port=9999, **kw):
        object.__init__(self)
        self.__name = name
        self.__port = port
        self.__running = False
        self.__context = zmq.Context()
        self.__socket = self.__context.socket(zmq.PULL)
        self.__socket.connect("tcp://127.0.0.1:%s" % self.__port)
        self.__handlers = {}

    def run(self):
        while self.__running:
            try:
                event = self.__socket.recv_json(flags=zmq.NOBLOCK)
                callback = self.__handlers.get(event['event'], None)
                if callback is not None:
                    try:
                        for c in callback:
                            c(*event['args'], **event['kwargs'])
                    except Exception, details:
                        print details
            except zmq.Again as e:
                time.sleep(0.01)
            except Exception, details:
                print details, 'err'
                pass
        print 'Closed push client'

    def __process_one_event(self, *args):
        try:
            event = self.__socket.recv_json(flags=zmq.NOBLOCK)
            callback = self.__handlers.get(event['event'], None)
            if callback is not None:
                try:
                    for c in callback:
                        c(*event['args'], **event['kwargs'])
                except Exception, details:
                    print details
            return True
        except zmq.Again as e:
            return True
        except Exception, details:
            print details, 'err'
            return True

    def stop(self):
        self.__running = False

    def register_push_event_handler(self, name, function):
        if name not in self.__handlers:
            self.__handlers[name] = []
        self.__handlers[name].append(function)

    def start(self, threaded=True):
        self.__running = True
        if threaded:
            GLib.idle_add(self.__process_one_event)
        else:
            self.run()
