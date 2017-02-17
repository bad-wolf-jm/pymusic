import os
import re
import mimetypes
import socket
import threading
import errno
import time
import urllib
import tempfile
import json


from functools import partial
from threading import Thread
from os.path import getsize
from datetime import datetime

from kivy.clock import mainthread, Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty, BooleanProperty, StringProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.bubble import Bubble

from kivy.properties import ObjectProperty
from kivy.factory import Factory

#from pydjay.audio.wavegen import WaveformGenerator
#from pydjay.audio.gst import AudioDecoder

#from pydjay.library import save_to_current_session, get_track_by_name

#from pydjay.uix import waveform_seekbar#screen, paged_grid, paged_display
#from pydjay.gui.turntable import turntable
#from pydjay.gui.utils import seconds_to_human_readable
from kivy.event import EventDispatcher
from kivy.logger import Logger

MAGIC='PYDJAY00MAGIC'

try:
    _default_host_name = socket.gethostname().split('.')[0]
except:
    _default_host_name = 'localhost'

try:
    _default_ip = socket.gethostbyname(socket.gethostname())
except:
    _default_ip = '127.0.0.1'

from kivy.utils import platform

class ConnectionError(Exception):
    pass

class Protocol:
    def __init__(self, socket, command_listener, controller = None):
        self._sock = socket
        self._sock.settimeout(.25)
        self._command_listener = command_listener
        self._command_thread = threading.Thread(target = self._listen_for_commands)
        self._command_thread.start()
        self._controller = controller
        self._data_buffer = ""
        self._lines = []
        self._shutdown = False
        
    def send_command(self, name, *args):
        #print 'SENDING COMMAND'
        if len(args) > 0:
            command = name +'+' + '+'.join(args)#[urllib.quote(x, "") for x in args])
        else:
            command = name
        if self._sock is not None:
            command += '\n'
            try:
                while not self._shutdown and command != '':
                    try:
                        sent = self._sock.send(command)
                        command = command[sent:]
                    except socket.timeout:
                        continue
                    except socket.error as e:
                        #self._handle_lost_connection("BB")
                        #print e
                        #break
                        raise ConnectionError()
                    except Exception, details:
                        raise ConnectionError()
                        #print details
                        #break
            except ConnectionError:
                self._handle_lost_connection("BB")
                
    def _handle_lost_connection(self, reason = ""):
        if self._sock is not None:
            self._sock.close()
            self._sock = None
        if self._command_listener is not None:
            try:
                self._command_listener.handle_lost_connection()
            except:
                pass
        self._controller.handle_lost_connection()

    def _read_lines(self):
        self._data_buffer += self._sock.recv(4096)
        if self._data_buffer != '':
            lines = self._data_buffer.split('\n')
            if len(lines) == 1:
                return []
            self._data_buffer = lines[-1]
            lines = lines[:1]
            return lines
        return None
                
    def _listen_for_commands(self):
        self._data_buffer = ""
        self._shutdown = False
        while not self._shutdown:
            #print self._shutdown
            try:
                lines = self._read_lines()
                if lines is None:
                    self._handle_lost_connection("AA")
                    break
                for l in lines:
                    if l != '':
                        bar = l.split('+')
                        command_name = bar[0]
                        if len(bar) > 0:
                            command_args = bar[1:] #[urllib.unquote(x) for x in bar[1:]]
                        else:
                            command_args = []
                        self._handle_command(command_name, command_args)
            except socket.timeout:
                continue
            except socket.error as e:
                self._handle_lost_connection("BB")
                print e
                break
            except Exception, details:
                print details
                break

    @mainthread
    def _handle_command(self, command, arg):
        method = "handle_"+command
        #print command, arg, method
        if self._command_listener is not None and hasattr(self._command_listener, method):
            method = getattr(self._command_listener, method)
            try:
                method(*arg)#[urllib.unquote(x) for x in arg])
            except Exception, details:
                print "COMMAND ERROR", details
                
    def shutdown(self):
        self._shutdown = True
        if self._command_thread is not None:
            self._shutdown = True
            self._command_thread.join()
        if self._sock is not None:
            self._sock.close()



class FileDownloadJob:
    def __init__(self):
        self._done_callbacks = []
        self._track_data = None

    def add_done_listener(self, callback, *args):
        self._done_callbacks.append((callback, args))

    def remove_done_listener(self, callback):
        cands = [x for x in self._done_callbacks if x[0] == callback]
        for foo in cands:
            self._done_callbacks.remove(foo)
        
    def done(self):
        for x, args in self._done_callbacks:
            try:
                x(self._track_data, *args)
            except:
                pass
            #self._done_callbacks.remove(callback)



            
class FileProtocol:
    def __init__(self, socket, from_address, local_root, controller = None):
        self._sock = socket
        self._sock.settimeout(.25)
        self._from_address = from_address
        self._local_root = local_root
        self._download_thread = threading.Thread(target = self._download_file)
        self._download_thread.start()
        self._controller = controller
        self._data_buffer = ""
        self._lines = []
        
    def _download_file(self):
        t = time.time()
        _data_buffer = ""
        while '\n' not in _data_buffer:
            _data_buffer += self._sock.recv(4096)

        line, rest = _data_buffer.split('\n', 1)
        remote_filename = urllib.unquote(line).decode('utf-8') #json.loads(line) #urllib.unquote(line))
        n, extension = os.path.splitext(remote_filename)
        f_handle, local_filename = tempfile.mkstemp(prefix = "data_", suffix = extension, dir = self._local_root)
        os.close(f_handle)
        Logger.info("FileProtocol: downloading '%s' from %s ---> %s", remote_filename, self._from_address[0], local_filename)
        download_job = FileDownloadJob()
        self._controller.add_file(remote_filename, download_job)

        f_handle = open(local_filename, 'wb')
        f_handle.write(rest)
        while True:
            try:
                bytes_read = self._sock.recv(4096)
                num = len(bytes_read)
                break
            except socket.timeout:
                continue
        while bytes_read != '':
            f_handle.write(bytes_read)
            while True:
                try:
                    bytes_read = self._sock.recv(4096)
                    break
                except socket.timeout:
                    continue
            #print len(bytes_read)
        f_handle.flush()
        f_handle.close()
        self._controller.done_downloading('%s:%s'%self._from_address)
        #with self._controller.file_lock:
        self._controller.add_file(remote_filename, local_filename)
        download_job.done()
        t1 = time.time()
        #self._controller.send_command("UPLOAD_COMPLETED", remote_filename.encode('utf-8'), str(t1-t))
        Logger.info("FileProtocol: Done downloading '%s' ", remote_filename)
                
    def shutdown(self):
        self._shutdown = True
        if self._download_thread is not None:
            #self._shutdown = True
            self._download_thread.join()
        if self._sock is not None:
            self._sock.close()


class DownloadCancelled(Exception):
    pass


class TrackProtocol(EventDispatcher):
    progress = NumericProperty(0)
    track    = ObjectProperty(None)
    done     = BooleanProperty(None)
    
    def __init__(self, socket, from_address, local_root, controller = None):
        super(TrackProtocol, self).__init__()
        self._sock = socket
        self._sock.settimeout(.5)
        self._from_address = from_address
        self._local_root = local_root
        self._controller = controller
        self._data_buffer = ""
        self._lines = []
        self._bytes_read = 0
        self._total_size = 0
        self._progress_callbacks = []
        self._done_callbacks = []
        self._cancelled_callbacks = []
        self._download_thread = threading.Thread(target = self._download_data)
        self._download_thread.start()
 
    def _download_file(self, filename, size):
        n, extension = os.path.splitext(filename)
        f_handle, local_filename = tempfile.mkstemp(prefix = "data_", suffix = extension, dir = self._local_root)
        os.close(f_handle)
        Logger.info("FileProtocol: downloading '%s' from %s ---> %s", filename, self._from_address[0], local_filename)
        f_handle = open(local_filename, 'wb')

        total_length_read = len(self._data_buffer)
        length_to_read    = size - len(self._data_buffer)
        #print "TOTAL_LENGTH_READ", total_length_read
        #print "LENGTH_READ", length_to_read
        if length_to_read >= 0:
            while length_to_read >= 0:
                f_handle.write(self._data_buffer)
                while True:
                    try:
                        bytes_read = self._sock.recv(4096)
                        if platform != 'android':
                            time.sleep(.0015)
                        self._bytes_read += len(bytes_read)
                        self._progress(self._bytes_read)
                        break
                    except socket.timeout:
                        continue
                if bytes_read == "":
                    if length_to_read == 0:
                        break
                    else:
                        Logger.error('TrackProtocol: Error downloading file <%s>, the connection was closed too soon.', filename)
                        # raise "Cownload Cancelled" exception
                        raise DownloadCancelled()
                        break
                    pass
                self._data_buffer = bytes_read
                length_to_read -= len(self._data_buffer)
                #print "LENGTH_READ", length_to_read
            f_handle.write(self._data_buffer[:length_to_read])
            self._data_buffer = self._data_buffer[length_to_read:]
            

        else:
            f_handle.write(self._data_buffer[0:size])
            self._data_buffer = self._data_buffer[size:]

        f_handle.flush()
        f_handle.close()
        self._controller.add_file(filename, local_filename)


    @mainthread
    def _progress(self, bytes_read):
        #print bytes_read
        self.progress = float(bytes_read) / self._total_size

    @mainthread
    def _track(self, data):
        self.track = data

    @mainthread
    def _done(self):
        self.done = True

    #@mainthread
    #def cancelled(self):

    @mainthread
    def cancelled(self):
        for x in self._cancelled_callbacks:
            try:
                x(self.track)
            except Exception, details:
                print details
        #self._done()

    #def add_completion_callback(self, callback):
    #    if callback is not None:
    #        if not callback in self._completed_callbacks:
    #            self._completed_callbacks.append(callback)

    #def remove_completion_callback(self, callback):
    #    #if callback is not None:
    #    if callback in self._completed_callbacks:
    #        self._completed_callbacks.remove(callback)


    def add_cancelled_callback(self, callback):
        if callback is not None:
            if not callback in self._cancelled_callbacks:
                self._cancelled_callbacks.append(callback)

    def remove_cancelled_callback(self, callback):
        #if callback is not None:
        if callback in self._cancelled_callbacks:
            self._cancelled_callbacks.remove(callback)
        
    def _download_data(self):
        download_job = FileDownloadJob()
        t = time.time()
        _data_buffer = ""
        while '\n' not in _data_buffer:
            _data_buffer += self._sock.recv(4096)

        line, rest = _data_buffer.split('\n', 1)

        sizes = line.split(":")

        data_size     = int(sizes[0])
        cover_size    = int(sizes[1])
        waveform_size = int(sizes[2])
        track_size    = int(sizes[3])
        self._total_size = data_size  + cover_size + track_size
        #print _data_buffer.encode('utf-8')
        self._data_buffer = rest
        #print "DATA_BUFFER:", self._data_buffer
        while len(self._data_buffer) <= data_size:
            try:
                self._data_buffer += self._sock.recv(4096)
            except socket.timeout:
                continue

        #print self._data_buffer[0:data_size]
        track_data = json.loads(self._data_buffer[0:data_size])
        self._data_buffer = self._data_buffer[data_size:]
        #print self._data_buffer
        track_index = track_data['location']
        art_index   = track_data['cover']
        wave_index  = track_data['waveform']
        download_job._track_data = track_data
        self._track(track_data)
        self._controller.add_track_data(track_index, download_job)
        try:
            if art_index is not None:
                self._download_file(art_index, cover_size)
            if wave_index is not None:
                self._download_file(wave_index, waveform_size)
            self._download_file(track_index, track_size)
            self._controller.done_downloading('%s:%s'%self._from_address)
            self._controller.add_track_data(track_index, track_data)
            self._progress(1)
            download_job.done()
            self._done()
            Logger.info("FileProtocol: Done downloading '%s' ", track_data)
        except DownloadCancelled:
            self.cancelled()
            pass
            
    def shutdown(self):
        self._shutdown = True
        if self._download_thread is not None:
            #self._shutdown = True
            self._download_thread.join()
        if self._sock is not None:
            self._sock.close()


        
class ControlServer(EventDispatcher):
    connected_to          = StringProperty("")
    connected             = BooleanProperty(False)
    broadcasting          = NumericProperty(0, allownone = True)

    def __init__(self,
                 host_name        = _default_host_name,
                 ip_address       = _default_ip,
                 port             = 1729,
                 broadcast_port   = 8989,
                 file_server_port = 9009,
                 local_file_root  = None,
                 command_handler  = None,
                 *args, **kw):
        super(ControlServer, self).__init__(*args, **kw)
        self._host_name          = host_name
        self._ip_address         = ip_address
        self._port               = port
        self._file_port          = file_server_port
        self._broadcast_port     = broadcast_port
        self._file_server_port   = file_server_port
        self._command_handler    = command_handler
        self._local_file_root    = local_file_root
        self._server_socket      = None
        self._file_server_socket = None
        self._server_thread      = None
        self._command_thread     = None
        self._broadcast_timeout  = 30
        self._master             = None
        self._discovery_thread   = None
        self._connected_ip       = None
        self._files_database     = {}
        self._file_downloads     = {}
        self._track_protocol_watch = []
        self.file_lock           = threading.Lock()
        self.file_download_lock  = threading.Lock()
        #self._track_database     = {}


    def add_file(self, remote, local):
        with self.file_lock:
            self._files_database[remote] = local

    def add_track_data(self, index, track_data):
        self._command_handler.handle_ADD_TRACK(index, track_data)

    def add_track_protocol_watch(self, cb):
        self._track_protocol_watch.append(cb)

    def new_track_download(self, track_protocol):
        for x in self._track_protocol_watch:
            try:
                x(track_protocol)
            except Exception, details:
                Logger.error("TrackDownload: error %s", details)
                pass
        
    def get_file(self, name):
        #with self.file_lock:
        return self._files_database.get(name, None)

    def done_downloading(self, from_):
        with self.file_download_lock:
            if from_ in self._file_downloads:
                #foo = self._file_downloads[from_]
                #foo.done()
                del self._file_downloads[from_]
    
    def _do_broadcast_loop(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #create UDP socket
        s.bind(('', 0))
        s.settimeout(.2)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) #this is a broadcast socket
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        my_ip = socket.gethostbyname(socket.gethostname()) #get our IP. Be careful if you have multiple network interfaces or IPs
        t = time.time()
        self._broadcast = True
        Clock.schedule_once(self._stop_broadcast, self._broadcast_timeout)
        while self._broadcast:
            #print 'BROADCASTING'
            try:
                data = MAGIC+self._host_name
                s.sendto(data, ('255.255.255.255', 8989))
                time.sleep(.5)
                elapsed_time = time.time() - t
                self._set_broadcast_time(int(self._broadcast_timeout-elapsed_time))
            except socket.timeout:
                pass
        Clock.unschedule(self._stop_broadcast)
        self._stop_broadcast()

    @mainthread
    def _set_broadcast_time(self, value):
        self.broadcasting = value

    @mainthread
    def set_connected(self, val):
        self.connected = val

    @mainthread
    def set_connected_to(self, val):
        self.connected_to = val

        
    def start_broadcast(self):
        self._discovery_thread = threading.Thread(target = self._do_broadcast_loop)
        self._discovery_thread.start()
        Logger.info('ControlServer: Broadcasting control server on %s', self._ip_address)

    def stop_broadcast(self):
        self._do_stop_broadcast()
        #@= False
        #@if self._discovery_thread is not None:
        #@    self._discovery_thread.join()
        #@    self._discovery_thread = None

    def _do_stop_broadcast(self, *args):
        #print 'STOPPING', self._discovery_thread
        self._set_broadcast_time(-1) 
        if self._discovery_thread is not None:
            self._broadcast = False
            self._discovery_thread.join()
            self._discovery_thread = None
            Logger.info('ControlServer: Stop broadcasting control server on %s', self._ip_address)

    _stop_broadcast = mainthread(_do_stop_broadcast)
    

    def start_server(self):
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind((self._ip_address, self._port))
        self._server_socket.listen(5)
        self._server_thread = threading.Thread(target = self._serve_until_connected)
        self._server_thread.start()
        Logger.info('ControlServer: Server started on %s:%s', self._ip_address, self._port)

    
    def start_file_server(self):
        self._file_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._file_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._file_server_socket.bind((self._ip_address, self._file_port))
        self._file_server_socket.listen(5)
        self._file_server_socket.settimeout(.25)
        self._file_server_thread = threading.Thread(target = self._serve_files)
        self._file_server_thread.start()
        Logger.info('ControlServer: File server started on %s:%s', self._ip_address, self._file_port)

    def _serve_files(self):
        while not self._server_shutdown:
            try:
                (clientsocket, address) = self._file_server_socket.accept()
                foo = TrackProtocol(clientsocket, address, self._local_file_root, self)
                self._file_downloads['%s:%s'%address] = foo
                self.new_track_download(foo)
                #foo.start()
                Logger.info('ControlServer: Downloading file from to %s', address[0])
                #break
            except socket.timeout:
                continue

    def _serve_until_connected(self):
        self._server_shutdown = False
        self._server_socket.settimeout(0.25)
        while not self._server_shutdown:
            try:
                (clientsocket, address) = self._server_socket.accept()
                self._master = Protocol(clientsocket, self._command_handler, self)
                self._connected_ip = address[0]
                self._stop_broadcast()
                self.set_connected(True)
                self._master.send_command("HOST", self._host_name, self._ip_address, str(self._file_server_port))
                Logger.info('ControlServer: Connected to %s', address[0])
                break
            except socket.timeout:
                continue
        self._server_socket.close()
        self._server_socket  = None
        self._server_thread  = None

    def send_command(self, *args):
        self._master.send_command(*args)

    def handle_lost_connection(self):
        self.start_server()
        self.set_connected(False)
        self.set_connected_to("")
        Logger.error('ControlServer: Connection to %s has been broken', self._connected_ip)
        self._connected_ip = None

                    
    def shutdown(self):
        Logger.info('ControlServer: Shutting down %s', self._ip_address)
        if self._master is not None:
            self._master.shutdown()
        self._server_shutdown = True#socket.shutdown()
        print 'stopping briadcast', self._discovery_thread
        self.stop_broadcast()
        if self._server_thread is not None:
            self._server_thread.join()
        if self._file_server_thread is not None:
            self._file_server_thread.join()
        with self.file_download_lock:
            for key in self._file_downloads:
                self._file_downloads[key].shutdown()    


class ControlClient(EventDispatcher):
    is_connected    = BooleanProperty(False)
    is_connected_to = StringProperty(None, allownone = True)
    
    def __init__(self, host = _default_host_name, ip_address = _default_ip, port = 1729, command_listener = None, *args, **kw):
        super(ControlClient, self).__init__(*args, **kw)
        self._host = host
        self._port = port
        self._ip   = ip_address
        self._sock = None
        self._shutdown = False
        #self._sock.settimeout(1)
        self._current_path = None
        self._current_uri = None
        self._is_playing = False
        self._is_paused = False
        self._command_listener = command_listener
        self._connect_thread = None

    def connect(self, abort = None):
        def _do_connect(abort = None):
            try:
                self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._sock.settimeout(1)
                self._shutdown = False
                while not self._shutdown:
                    try:
                        self._sock.connect((self._ip, self._port))
                        self._protocol = Protocol(self._sock, self._command_listener, self)
                        #self._protocol.send_command("HOST", self._host, self._ip)
                        break
                    except socket.timeout:
                        continue
                while not self._shutdown:
                    try:
                        #self._sock.connect((self._ip, self._port))
                        #self._protocol = Protocol(self._sock, self._command_listener, self)
                        self._protocol.send_command("HOST", self._host, self._ip)
                        break
                    except socket.timeout:
                        continue


                    #self._data_thread = threading.Thread(target = self._listen_for_command)
                #self._data_thread.start()
                self.set_connected(True)
                #self.set_connected_to(True)
            except Exception, details:
                print 'ERROR', details, abort
                self._sock = None
                if abort is not None:
                    abort()
            self._connect_thread = None
            
        self._connect_thread = threading.Thread(target = _do_connect, args = (abort,))
        self._connect_thread.start()


    def disconnect(self):
        self._sock.close()
        self._sock = None
        self._protocol = None
        
    def send_command(self, *args):
        self._protocol.send_command(*args)

    #def send_command_sync(self, *args):
    #    self._protocol.send_command_sync(*args)

    @mainthread
    def set_connected(self, value):
        self.is_connected = value

    @mainthread
    def set_connected_to(self, value):
        self.is_connected_to = value

    def handle_lost_connection(self):
        Logger.error("Protocol: Lost connection")
        self.set_connected(False)
        self.set_connected_to("")
    
    def shutdown(self):
        if self._protocol is not None:
            self._protocol.shutdown()
        self._shutdown = True
        
        if self._connect_thread is not None:
            self._connect_thread.join()
            self._connect_thread = None
        
        #if self._discovery_thread is not None:
        #    self._discovery_thread.join()
        #    self._discovery_thread = None
