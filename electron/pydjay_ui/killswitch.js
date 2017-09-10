
const os = require('os');
const {spawn} = require ('child_process');
var platform = os.platform();

function kill_audio_server() {
    if (platform == 'win32') {
        kill = spawn('Taskkill' ['/F', '/IM', 'python.exe']);
    } else {
        kill = spawn('killall', ['-9', 'Python']);
    }
}

kill_audio_server()
