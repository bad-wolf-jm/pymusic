zmq = require('zmq');

command_socket = zmq.socket('req');
command_socket.connect('tcp://127.0.0.1:9898');
command_socket.on("message", function( status, type, payload ) {
       console.log("Received reply", payload);
});

function preview_play(file_name, start_time, end_time){
    command_socket.send(JSON.stringify({'name': 'preview_play', 'args': [file_name, start_time, end_time], 'kwargs': {}}));
}

function preview_pause(file_name){
    command_socket.send(JSON.stringify({'name': 'preview_pause', 'args': [], 'kwargs': {}}));
}

function preview_stop(file_name){
    command_socket.send(JSON.stringify({'name': 'preview_stop', 'args': [], 'kwargs': {}}));
}



preview_time_socket = zmq.socket('pull');
preview_time_socket.connect('tcp://127.0.0.1:5556');
preview_time_socket.on("message", function( payload ) {
       //console.log("Received reply time", JSON.parse(payload.toString()));//, ": [", reply.toString(), ']');
       data = JSON.parse(payload.toString());
       if (data.event == 'track_position_notice') {
           $$('preview_time').define('label', format_nanoseconds(data.args[0]))
           $$('preview_time').refresh()
       } else if (data.event == 'track_duration_notice') {
           $$('preview_length').define('label', format_nanoseconds(data.args[0]))
           $$('preview_length').refresh()
       }
});


main_time_socket = zmq.socket('pull');
main_time_socket.connect('tcp://127.0.0.1:5557');
main_time_socket.on("message", function( payload ) {
       console.log("Received reply", payload);//, ": [", reply.toString(), ']');
});
