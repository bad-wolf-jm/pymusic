#import os
import threading
from decoder_no_thread import GstAudioFile
from output_jack_lb import JackOutput
from gi.repository import GLib

class AudioPlayer(object):
    def __init__(self, player_name=None, num_channels=2, **kw):
        object.__init__(self)
        self._current_time = None
        self.player_name = player_name
        self.num_channels = num_channels
        self._is_playing = False
        self._player_thread = None
        self._decoder = None
        self._output = JackOutput(self.player_name, self.num_channels)
        self.state = None
        self._track_duration = None
        self._track_position = None
        self._track_length = None
        self._pause_track = None
        self._file = None

    def connect_outputs(self, **kwargs):
        self._output.connect_outputs(**kwargs)

    def disconnect_outputs(self, **kwargs):
        self._output.disconnect_outputs(**kwargs)

    def on_track_length(self, length):
        self._track_length = length

    def on_track_duration(self, duration):
        self._track_duration = duration

    def on_track_position(self, position):
        self._track_position = position

    def on_track_remaining_time(self, position):
        pass

    def on_end_of_stream(self):
        self.on_track_length(None)
        self.on_track_duration(None)
        self.on_track_position(None)

    def _player_loop(self):
        eos = False
        has_duration = False
        while self._is_playing:
            try:
                timestamp, samples = self._decoder.next()
                if self._decoder.duration is not None and not has_duration:
                    has_duration = True
                    self.on_track_duration(self._decoder.duration)
                    self.on_track_length(self._decoder.track_length)
                self.on_track_position(self._output.stream_time)
                self._output.send(samples)
            except StopIteration:
                eos = True
                break
        self._decoder.close()
        self._is_playing = False
        self._player_thread = None
        if eos:
            self.on_end_of_stream()


    # def _player_loop_glib_idle(self):
    #     eos = False
    #     try:
    #         if self._decoder is not None:
    #             timestamp, samples = self._decoder.next()
    #             if self._decoder.duration is not None and not self._has_duration:
    #                 self._has_duration = True
    #                 self.on_track_duration(self._decoder.duration)
    #                 self.on_track_length(self._decoder.track_length)
    #             #print self._output.stream_time
    #             self._output.send(samples)
    #             self.on_track_position(self._output.stream_time)
    #         else:
    #             return True
    #     except StopIteration:
    #         eos = True
    #         #break
    #     #self._decoder.close()
    #     #self._is_playing = False
    #     #self._player_thread = None
    #     if eos:
    #         self.on_end_of_stream()
    #         return False
    #     else:
    #         if not self._is_playing:
    #             self._decoder.close()
    #             return False
    #         return True

    def stop_decoder_loop(self):
        #self._decoder.close()
        self._is_playing = False
        #self._player_thread = None

    def report_stream_position(self):
        self.on_track_position(self._output.stream_time)
        return self._is_playing


    def play(self, filename, start_time=None, end_time=None):
        self.stop(flush=True)
        self._file = filename
        self._start_time = start_time
        self._end_time = end_time
        try:
            self._decoder = GstAudioFile(
                self._file, self._output.num_channels, self._output.samplerate, 'F32LE', None, start_time, end_time, use_threaded_gloop=False)
            if start_time is not None:
                self._output.reset_timer(start_time)
            else:
                self._output.reset_timer(0)
            self._is_playing = True
            self._has_duration = False
            self._player_thread = threading.Thread(target=self._player_loop)
            self._player_thread.start()
            self.state = "playing"
        except IOError, e:
            self.state = 'stopped'
            print('error', e)
        except Exception, details:
            print details
            self.state = 'stopped'

    def stop(self, flush=False, pause=False):
        self._is_playing = False
        if flush:
            self._output.flush_buffer()
        self._output.reset_timer()
        if self._player_thread is not None:
            self._player_thread.join()
        self._player_thread = None
        self._decoder = None
        if not pause:
            self._pause_track = None
            self._pause_track_timestamp = None
        self.on_track_length(None)
        self.on_track_duration(None)
        self.on_track_position(None)
        self.state = "stopped"

    def pause(self):
        self.state = "paused"
        if self._is_playing:
            if self._file is not None:
                self._pause_track_timestamp = self._track_position
                self._pause_track = self._file
                # print self._pause_track_timestamp
                self.stop(flush=True, pause=True)
            self._is_playing = False
        else:
            if self._pause_track is not None:
                if self._pause_track == self._file:
                    s_t = self._pause_track_timestamp if self._pause_track_timestamp is not None else self._start_time
                    # print s_t
                    self.play(self._file, s_t, self._end_time)
                    self._is_playing = True
                    return
            if self._file is not None:
                self.play(self._file, self._start_time, self._end_time)

    def seek(self, timestamp):
        if self._decoder is not None:
            self._decoder.seek(timestamp)
            self._output.reset_timer(timestamp)
            self._output.flush_buffer()

    def seek_relative(self, time):
        if self._is_playing:
            p = self._track_position
            if p is not None:
                d = self._track_duration
                if d is not None:
                    p += time
                    p = max(min(p, d), 0)
                    self.seek(p)

    @property
    def is_playing(self):
        return self.state == 'playing'

    def shutdown(self):
        self.stop()
        self._output.close()
