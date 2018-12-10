// Sortable              = require("../../../lib/Sortable.js")
// WaveSurfer            = require("wavesurfer.js")
// var WaveSurferRegions = require('wavesurfer.js/dist/plugin/wavesurfer.regions.min.js');
var path              = require('path');
const { ipcRenderer } = require('electron');

mpc = new PlaybackController() //S_controller, Q_controller)
pc  = new PrecueController() //S_controller, Q_controller)
vc  = new VolumeController(mpc, pc)

mpc.init_audio()
pc.init_audio()

ipcRenderer.on('play', (event, arg) => {        
    let channel = arg.channel
    let track = arg.track
    if (channel == "headphones") {
        pc.play(track, arg.stream_start, arg.stream_end)
    } else if (channel == "master") {
        mpc.play(track, arg.stream_start, arg.stream_end)
    }
});


ipcRenderer.on('pause', (event, arg) => {        
    let channel = arg.channel
    if (channel == "headphones") {
        pc.pause()
    } else if (channel == "master") {
        mpc.pause() 
    }
});

ipcRenderer.on('resume', (event, arg) => {        
    let channel = arg.channel
    if (channel == "headphones") {
        pc.resume()
    } else if (channel == "master") {
        mpc.resume() 
    }

});


ipcRenderer.on('stop', (event, arg) => {        
    let channel = arg.channel
    if (channel == "headphones") {
        pc.stop() 
    } else if (channel == "master") {
        mpc.stop() 
    }
});


ipcRenderer.on('toggle-play-pause', (event, arg) => {        
    let channel = arg.channel
});


pc.on('playback-stopped',  () => {
    vc.restore_monitor()
})

pc.on('playback-paused', () => {
    vc.restore_monitor()
})

pc.on('playback-started', () => {
    vc.mute_monitor()
})

