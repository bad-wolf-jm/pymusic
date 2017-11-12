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
