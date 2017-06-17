import zmq
import json
import threading
#import time


class RPCServer(threading.Thread):
    """docstring for RPCServer."""

    def __init__(self, name=None, port=9999, **kw):
        threading.Thread.__init__(self)
        self.__name = name
        self.__port = port
        self.__running = False
        self.__context = zmq.Context()
        self.__socket = self.__context.socket(zmq.REP)
        self.__socket.bind("tcp://127.0.0.1:%s" % self.__port)

    def __run(self):
        while self.__running:
            try:
                command = self.__socket.recv(flags=zmq.NOBLOCK)
                command = json.loads(command)
            except zmq.Again as e:
                continue
                pass  # time.sleep(0.01)
            except Exception, details:
                print details
                break
            command_name = command['name']
            command_args = command.get('args', None) or tuple()
            command_kw = command.get('kwargs', None) or {}
            method = getattr(self, command_name, None)
            try:
                if method is not None:
                    value = method(*command_args, **command_kw)
                    value = json.dumps(value)
                    self.__socket.send(value)
            except Exception, details:
                print 'ERROR CALLING', details, value
                continue
                # time.sleep(.05)
        self.__socket.close()

    run = __run

    def start(self, threaded=True):
        self.__running = True
        if threaded:
            threading.Thread.start(self)
        else:
            self.__run()

    def stop(self):
        self.__running = False


class RPCClient(object):
    """docstring for RPCClient."""

    def __init__(self, name=None, port=9999, **kw):
        object.__init__(self)
        self.__name = name
        self.__port = port
        self.__context = zmq.Context()
        self.__socket = self.__context.socket(zmq.REQ)
        self.__socket.connect("tcp://127.0.0.1:%s" % self.__port)

    def remote_call(self, f_name, *args, **kwargs):
        comm = {'name': f_name, 'args': args, 'kwargs': kwargs}
        try:
            self.__socket.send(json.dumps(comm))
            return json.loads(self.__socket.recv())
        except:
            print comm

    def stop(self):
        self.__socket.close()
