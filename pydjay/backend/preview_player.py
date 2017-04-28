from pydjay.backend.audio_player_server import AudioServer

if __name__ == '__main__':
    main_player = AudioServer("PreviewPlayer", 2, port = 9998, event_port = 5556)
    main_player.connect_outputs(output_1 = "VolumeControl:input_5",
                                output_2 = "VolumeControl:input_6")
    main_player.start(threaded = False)
