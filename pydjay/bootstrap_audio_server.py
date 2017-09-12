# Core of audio part
from pydjay.backend.audio_player_server import AudioServer
from pydjay.backend.volume_control import VolumeControlServer
import os

main_player = AudioServer("MainPlayer", 2, port=9999, event_port=5557)
preview_player = AudioServer("PreviewPlayer", 2, port=9998, event_port=5556)
volume_control = VolumeControlServer("VolumeControl", num_channels=6, event_port=5555)

preview_player.connect_outputs(output_1="VolumeControl:input_5",
                               output_2="VolumeControl:input_6")

main_player.connect_outputs(output_1="VolumeControl:input_1",
                            output_2="VolumeControl:input_2")

main_player.connect_outputs(output_1="VolumeControl:input_3",
                            output_2="VolumeControl:input_4")

volume_control.connect_outputs(output_1="system:playback_1",
                               output_2="system:playback_2",
                               output_3="system:playback_5",
                               output_4="system:playback_6",
                               output_5="system:playback_5",
                               output_6="system:playback_6")


# def set_volume(channel, volume):
#     volume_control.set_volume(channel, volume)
#
#
# def get_volume(channel):
#     return volume_control.get_volume(channel)
#
#
# def _increase_main_volume(*a):
#     v = volume_control.main_player
#     v += .1
#     v = min(v, 8)
#     volume_control.main_player = v
#
#
# def _decrease_main_volume(*a):
#     v = volume_control.main_player
#     v -= .1
#     v = max(v, 0)
#     volume_control.main_player = v
#
#
# def _increase_monitor_volume(*a):
#     v = volume_control.main_player_monitor
#     v += .1
#     v = min(v, 8)
#     volume_control.main_player_monitor = v
#
#
# def _decrease_monitor_volume(*a):
#     v = volume_control.main_player_monitor
#     v -= .1
#     v = max(v, 0)
#     volume_control.main_player_monitor = v
#
#
# def _increase_preview_volume(*a):
#     v = volume_control.preview_player
#     v += .1
#     v = min(v, 8)
#     volume_control.preview_player = v
#
#
# def _decrease_preview_volume(*a):
#     v = volume_control.preview_player
#     v -= .1
#     v = max(v, 0)
#     volume_control.preview_player = v
#
#
# def _preview_seek(self, t):
#     #time in seconds
#     t *= 1000000000
#     preview_player.player.seek_relative(t)
#
#
# def _preview_stop(self):
#     preview_player.stop()
#
#
# def _preview_pause(self):
#     preview_player.pause()
