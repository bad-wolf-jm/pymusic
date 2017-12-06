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

    def _sink_chain(self, buf):s
        # this is where we do filtering
        # and then push a buffer to the next element, returning a value saying
        # it was either successful or not.
        time_per_packet = int(1.0 / self.stream_rate * 1000000000)  # in nanoseconds

        # if self._duration is not None:
        #foo = self._parent.query_duration(Gst.Format.TIME)
        # print foo
        # if foo[0]:
        # self._duration =
        #self._duration = [1]
        # self._duration / (time_per_packet * self._num_data_points * 2)
        self._packets_per_data_point = 1

        # print "FOO", self._idx, buf.get_size(), buf.get_sizes(), buf.pts, buf.duration, self._duration, self._packets_per_data_point, len(self._packet_queue)
        # if buf is None:

        pts, data = buf  # .map(Gst.MapFlags.READ)
        # try:
        #assert res
        offset = 0
        buffer_bytes = array.array('f', data)
        num_samples = len(buffer_bytes)
        packets = []
        timestamp = pts

        while offset + self.num_channels < num_samples:
            self._packet_queue.append(
                (timestamp, tuple(buffer_bytes[offset:offset + self.num_channels])))
            offset += self.num_channels
            timestamp += time_per_packet

        # finally:
        #    buf.unmap(mapinfo)

        self._process_packet_queue()

        # if self._eos:
        #    return Gst.FlowReturn.EOS
        # return self.srcpad.push(buf)

    def _process_packet_queue(self):
        def _av(x):
            # print x
            return float(x[0] + x[1]) / 2

        if self._duration is not None:
            while len(self._packet_queue) >= 1:
                # self._packets_per_data_point:#

                #min_timestamp = self._packet_queue[0][0]
                #max_timestamp = self._packet_queue[self._packets_per_data_point-1][0]
                # average_timestamp = float(max_timestamp + min_timestamp) / 2 #numpy.mean([foo[0] for foo in self._packet_queue[0:self._packets_per_data_point]])

                timestamp = self._packet_queue[0][0]
                #max_timestamp = self._packet_queue[self._packets_per_data_point-1][0]
                # average_timestamp = float(max_timestamp + min_timestamp) / 2 #numpy.mean([foo[0] for foo in self._packet_queue[0:self._packets_per_data_point]])
                sample = self._packet_queue[0][1]

                value = (sample[0] + sample[1]) / 2

                # print min_timestamp, max_timestamp, average_timestamp
                #sams = [sample[1] for sample in self._packet_queue[0:self._packets_per_data_point]]
                #vals = map(numpy.mean, [sample[1] for sample in self._packet_queue[0:self._packets_per_data_point]])

                # = [sample[1] for sample in self._packet_queue[0:self._packets_per_data_point]]
                # print sams
                #a_vals = [_av(x) for x in sams]
                # max_points = numpy.amax(a_vals)#map(numpy.mean, [sample[1] for sample in self._packet_queue[0:self._packets_per_data_point]]))
                # min_points = numpy.amin(a_vals)#map(numpy.mean, [sample[1] for sample in self._packet_queue[0:self._packets_per_data_point]]))
                self._idx += 1
                new_data_point = (self._duration, timestamp, value)  # (max_points+min_points) / 2)
                # print new_data_point
                if self._new_data_point_cb is not None:
                    self._new_data_point_cb(*new_data_point)
                self._data_points.append((timestamp, value))  # (max_points+min_points) / 2))
                del self._packet_queue[0]
