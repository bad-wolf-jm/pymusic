import zmq
import json
import threading
import time

class RPCServer(object):
    """docstring for RPCServer."""
    def __init__(self, name = None, port = 9999, **kw):
        super(RPCServer, self).__init__()
        self._name           = name
        self._port           = port
        self._command_thread = None
        self._running        = False
        self._context        = zmq.Context()
        self._server_socket  = self._context.socket(zmq.REP)
        self._server_socket.bind("tcp://127.0.0.1:%s" % self._port)


    def _command_loop(self):
        print "Listening...", self._port
        while self._running:
            command = self._server_socket.recv()
            try:
                print command
                command = json.loads(command)
            except Exception, details:
                print details
                continue
            command_name = command['name']
            command_args = command.get('args', None) or tuple()
            command_kw   = command.get('kwargs', None) or {}
            method       = getattr(self, command_name, None) or self._default_method
            try:
                value = method(*command_args, **command_kw)
                value = json.dumps(value)
                self._server_socket.send(value)
            except Exception, details:
                print 'ERROR CALLING', details
                continue
                time.sleep(.05)

    def start(self, threaded = True):
        if threaded:
            if self._command_thread is not None:
                self._command_thread = threading.Thread(target = self._command_loop)
                self._running = True
                self._command_thread.start()
        else:
            #self.shutdown()
            if self._command_thread is None:
                self._running = True
                self._command_loop()

    def shutdown(self):
        if self._command_thread is not None:
            self._running = False
            self._command_thread.join()


class PushServer(object):
    """docstring for RPCServer."""
    def __init__(self, name = None, port = 9999, **kw):
        super(PushServer, self).__init__()
        self._name           = name
        self._port           = port
        self._command_thread = None
        self._running        = False
        self._context        = zmq.Context()
        self._server_socket  = self._context.socket(zmq.PUSH)
        self._server_socket.bind("tcp://127.0.0.1:%s" % self._port)
        self._message_queue = []
        print 'FOOBAR', self._port

    def _command_loop(self):
        print "PUSH ON...", self._port, self._running
        while self._running:
            while len(self._message_queue) > 0:
                event = self._message_queue.pop(0)
                print event
                self._server_socket.send_json(event)
                time.sleep(.05)

    def start(self, threaded = True):
        print 'starting push server',
        if threaded:
            if self._command_thread is None:
                self._command_thread = threading.Thread(target = self._command_loop)
                self._running = True
                self._command_thread.start()
        else:
            if self._command_thread is None:
                self._running = True
                self._command_loop()

    def shutdown(self):
        if self._command_thread is not None:
            self._running = False
            self._command_thread.join()

    def push(self, event):
        self._message_queue.append(event)


class RPCClient(object):
    """docstring for RPCServer."""
    def __init__(self, name = None, port = 9999, **kw):
        super(RPCServer, self).__init__()
        self._name           = name
        self._port           = port
        self._command_thread = None
        self._running        = False
        self._context        = zmq.Context()
        self._server_socket  = self._context.socket(zmq.REQ)
        self._server_socket.connect("tcp://127.0.0.1:%s" % self._port)

    def _command_loop(self):
        while self._running:
            command = self._socket.recv()
            try:
                command = json.loads(command)
            except:
                continue
            command_name = command['name']
            command_args = command.get('args', None) or tuple()
            command_kw   = command.get('kwargs', None) or {}
            method       = getattr(self, command_name, None) or self._default_method
            try:
                value = method(*command_args, **command_kw)
                value = json.dumps(value)
                self._socket.send(value)
            except Exception, details:
                print 'ERROR CALLING', details
                continue

    def start(self, threaded = True):
        if threaded:
            if self._command_thread is not None:
                self._command_thread = threading.Thread(target = self._command_loop)
                self._running = True
                self._command_thread.start()
        else:
            self.shutdown()
            self._command_loop()

    def shutdown(self):
        if self._command_thread is not None:
            self._running = False
            self._command_thread.join()
