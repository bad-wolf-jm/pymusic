from pydjay.backend.audio_player_server import AudioServer


if __name__ == '__main__':
    main_player = AudioServer("MainPlayer", 2, port=9999, event_port=5557)
    main_player.connect_outputs(output_1="VolumeControl:input_1",
                                output_2="VolumeControl:input_2")
    main_player.connect_outputs(output_1="VolumeControl:input_3",
                                output_2="VolumeControl:input_4")

    main_player.start(threaded=False)
