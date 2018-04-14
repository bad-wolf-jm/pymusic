import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst, GObject as gobject

Gst.init(None)
gobject.threads_init()

import array
import numpy
import decoder


class WaveformGenerator:

    def __init__(self, num_data_points, new_data_point_cb=None, process_done_cb=None, *args, **kwargs):
        self._num_data_points = num_data_points
        self._duration = None
        self._idx = 0
        self._eos = False
        self._force_stop = False
        self._packet_queue = []
        self._data_points = []
        self._generator_thread = None
        self._generator_thread_running = False
        self._new_data_point_cb = new_data_point_cb
        self._process_done_cb = process_done_cb

    def set_data_point_callback(self, cb):
        self._new_data_point_cb = cb

    def set_process_done_callback(self, cb):
        self._process_done_cb = cb

    def get_data_points(self):
        return self._data_points

    def force_stop(self):
        self._force_stop = True

    def generate_waveform(self, filename):
        self.sample_generator = decoder.GstAudioFile(
            filename, format='S16LE', timeout=2, samplerate=250)
        self._duration = None
        self._force_stop = False
        self._data_points = []
        with self.sample_generator as generator:
            self.stream_rate = generator.samplerate
            self.num_channels = generator.channels
            for buf in generator:
                if self._duration is None:
                    self._duration = generator.duration
                if self._force_stop:
                    break
                self._sink_chain(buf)
        return self._data_points

    def _sink_chain(self, buf):
        # this is where we do filtering
        # and then push a buffer to the next element, returning a value saying
        # it was either successful or not.
        time_per_packet = int(1.0 / self.stream_rate * 1000000000)  # in nanoseconds
        self._packets_per_data_point = 1

        pts, data = buf
        offset = 0
        buffer_bytes = array.array('f', data)
        num_samples = len(buffer_bytes)
        timestamp = pts

        while offset + self.num_channels < num_samples:
            self._packet_queue.append(
                (timestamp, tuple(buffer_bytes[offset:offset + self.num_channels])))
            offset += self.num_channels
            timestamp += time_per_packet
        self._process_packet_queue()

    def _process_packet_queue(self):
        def _av(x):
            return float(x[0] + x[1]) / 2

        if self._duration is not None:
            while len(self._packet_queue) >= 1:
                timestamp = self._packet_queue[0][0]
                sample = self._packet_queue[0][1]
                value = (sample[0] + sample[1]) / 2
                self._idx += 1
                new_data_point = (self._duration, timestamp, value)
                if self._new_data_point_cb is not None:
                    self._new_data_point_cb(*new_data_point)
                self._data_points.append((timestamp, value))
                del self._packet_queue[0]
