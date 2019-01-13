

class VolumeController extends EventDispatcher {
    constructor(main_player_controller, precue_player_controller) {
        super()
        this.monitor_set_volume = 1;
        this.monitor_volume = 1;
        this.monitor_muted_volume = 0;

        this.main_player_controller = main_player_controller 
        this.precue_player_controller = precue_player_controller
    }

    init_audio() {
        this.main_player_controller.init_audio()  
        this.precue_player_controller.init_audio()
    }

    reset_audio() {
        this.main_player_controller.reset_audio()  
        this.precue_player_controller.reset_audio()
    }

    set_main_player_volume(value) {
        this.main_player_controller.setVolume('master', 'left', value)
        this.main_player_controller.setVolume('master', 'right', value)
    }
    
    set_monitor_volume(value) {
        this.main_player_controller.setVolume('headphones', 'left', value)
        this.main_player_controller.setVolume('headphones', 'right', value)
    }
    
    set_precue_player_volume(value) {
        this.precue_player_controlle.setVolume('master', 'left', value)
        this.precue_player_controlle.setVolume('master', 'right', value)
    }

    mute_monitor() {
        var a_monitor_volume = {volume: this.monitor_volume};
        $(a_monitor_volume).animate(
            {volume: this.monitor_muted_volume},
            {
                duration:100,
                step: (now, tween) => {
                    this.set_monitor_volume(now);
                },
            }
        )
    }
        
    restore_monitor() {
        var a_monitor_volume = {volume: this.monitor_volume};
        $(a_monitor_volume).animate(
            {volume: this.monitor_set_volume},
            {
                duration:100,
                step: (now, tween) => {
                    this.set_monitor_volume(now);
                },
            }
        )
    }
    
}