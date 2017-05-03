import zmq
import json
import threading
import time

class PushServer(threading.Thread):
    """docstring for RPCServer."""
    def __init__(self, name = None, port = 9999, **kw):
        threading.Thread.__init__(self)
        self.__name           = name
        self.__port           = port
        self.__running        = False
        self.__context        = zmq.Context()
        self.__socket  = self.__context.socket(zmq.PUSH)
        self.__socket.bind("tcp://127.0.0.1:%s" % self.__port)
        self.__message_queue = []

    def run(self):
        while self.__running:
            while len(self.__message_queue) > 0:
                event = self.__message_queue.pop(0)
                try:
                    self.__socket.send_json(event)
                    time.sleep(.05)
                except Exception, details:
                    print "ERROR", details
        self.__socket.close()

    def start(self, threaded = True):
        self.__running = True
        if not threaded:
            self.run()
        else:
            threading.Thread.start(self)

    def stop(self):
        self.__running = False

    def push(self, event, *args, **kwargs):
        #if replace:
        self.__message_queue = [x for x in self.__message_queue if x['event'] != event]
        self.__message_queue.append({'event': event, 'args': args, 'kwargs': kwargs})


class PushClient(threading.Thread):
    """docstring for RPCServer."""
    def __init__(self, name = None, port = 9999, **kw):
        threading.Thread.__init__(self)
        self.__name           = name
        self.__port           = port
        self.__running        = False
        self.__context        = zmq.Context()
        self.__socket  = self.__context.socket(zmq.PULL)
        self.__socket.connect("tcp://127.0.0.1:%s" % self.__port)
        self.__handlers = {}

    def run(self):
        while self.__running:
            #print 'running', self, self.__running
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
                #print "No message received yet"
                time.sleep(0.01)
            except Exception, details:
                print details, 'err'
                pass
        self.__socket.close()
        print 'Closed push client'

    def stop(self):
        print 'closing'
        self.__running = False
        #self.__socket.close()

    def register_push_event_handler(self, name, function):
        if name not in self.__handlers:
            self.__handlers[name] = []
        self.__handlers[name].append(function)

    def start(self, threaded = True):
        self.__running = True
        if not threaded:
            self.run()
        else:
            threading.Thread.start(self)
