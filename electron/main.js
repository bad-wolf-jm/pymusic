'use strict';
const { ipcMain } = require('electron');
const { existsSync } = require("fs")
const {homedir} = require("os")
var electron = require('electron');
const path = require("path")
const { MusicDatabase } = require("./pydjay_ui/node_modules/musicdb/model.js")


var app = electron.app;
var BrowserWindow = electron.BrowserWindow;

var mainWindow = null;
var mixerWindow = null;

app.on('ready', async () => {
    mainWindow = new BrowserWindow({
      width: 1728,
      height: 1152,
    });

    if (!(existsSync(path.join(homedir(), ".pymusic-library")))) {
      let library = new MusicDatabase("pymusic")
      await library.initialize()
      library = undefined
    }

    // mixerWindow = new BrowserWindow({
    //   width: 600,
    //   height: 400,
    //   // show:false,
    // });
    //mainWindow.setMenu(null);
    //mainWindow.loadURL('file://' + __dirname + '/pydjay_ui/main_ui.html');
    mainWindow.loadURL('file://' + __dirname + '/pydjay_ui/html_interface/main_window/main_window.html');
    // mixerWindow.loadURL('file://' + __dirname + '/pydjay_ui/html_interface/mixer/main_window.html');

    // mixerWindow.on('close', (e) => {
    //   // if(!force_quit){
    //     e.preventDefault();
    //     mixerWindow.hide();
    //   //     mainWindow.hide();
    //   // }
    // });

    mainWindow.on('close', function(e) {
      var choice = electron.dialog.showMessageBox(this,
          {
            type: 'question',
            buttons: ['Yes', 'No'],
            title: 'Confirm quit',
            message: 'Are you sure you want to quit?'
         });
         if(choice == 1){
           e.preventDefault();
         }
        //  else {
        //    mixerWindow.destroy()
        //  }
      });
});

ipcMain.on('quit-pymusic', (event, message) => {
  mainWindow.close()
})



// ipcMain.on('track-modified', (event, message) => {
//   mainWindow.webContents.send("track-modified", message)
// })

// ipcMain.on('playback-start', (event, message) => {
//   mainWindow.webContents.send("playback-start", message)
// })

// ipcMain.on('playback-stop', (event, message) => {
//   mainWindow.webContents.send("playback-stop", message)
// })


// ipcMain.on("reset-audio-system", (event, message) => {
//   mixerWindow.webContents.send("reset-audio-system", message)
// })


// ipcMain.on("show-mixer-window", (event, message) => {
//   mixerWindow.show()
// })

// // message = {
// //   track:"path",
// //   stream_start: 0,
// //   stream_end: 100,
// //   channel:"master"
// // }
// ipcMain.on("mixer-play", (event, message) => {
//   mixerWindow.webContents.send("play", message)
// })

// // message = {
// //   channel:"master"
// // }
// ipcMain.on("mixer-pause", (event, message) => {
//   mixerWindow.webContents.send("pause", message)
// })

// // message = {
// //   channel:"master"
// // }
// ipcMain.on("mixer-resume", (event, message) => {
//   mixerWindow.webContents.send("resume", message)
// })



// // message = {
// //   channel:"master"
// // }
// ipcMain.on("mixer-toggle-play-pause", (event, message) => {
//   mixerWindow.webContents.send("toggle-play-pause", message)
// })


// // message = {
// //   channel:"master"
// // }
// ipcMain.on("mixer-stop", (event, message) => {
//   mixerWindow.webContents.send("stop", message)
// })


// // message = {
// //   delta: milliseconds
// //   channel:"master"
// // }
// ipcMain.on("mixer-skip", (event, message) => {
//   mixerWindow.webContents.send("skip", message)
// })



// message = {
//   channel:"master"
//   event_type:"master"
//   event_value:"master"
// }
// ipcMain.on("mixer-event", (event, message) => {
//   mixerWindow.webContents.send("stop", message)
// })

// ipcMain.on('headphone-end-of-stream', (event, message) => {
//   mainWindow.webContents.send("headphone-end-of-stream", {})
// })

// ipcMain.on('headphone-playback-stopped',  (event, message) => {
//   mainWindow.webContents.send("headphone-playback-stopped", {})
// })

// ipcMain.on('headphone-playback-paused', (event, message) => {
//   mainWindow.webContents.send("headphone-playback-paused", {})
// })

// ipcMain.on('headphone-playback-started', (event, message) => {
//   mainWindow.webContents.send("headphone-playback-started", {})
// })

// ipcMain.on('headphone-stream-position', (event, pos) => {
//   mainWindow.webContents.send("headphone-stream-position", pos)
// })


// ipcMain.on('master-end-of-stream', (event, message) => {
//   mainWindow.webContents.send("master-end-of-stream", {})
// })

// ipcMain.on('master-playback-stopped',  (event, message) => {
//   mainWindow.webContents.send("master-playback-stopped", {})
// })

// ipcMain.on('master-playback-paused', (event, message) => {
//   mainWindow.webContents.send("master-playback-paused", {})
// })

// ipcMain.on('master-playback-started', (event, message) => {
//   mainWindow.webContents.send("master-playback-started", {})
// })

// ipcMain.on('master-stream-position', (event, pos) => {
//   mainWindow.webContents.send("master-stream-position", pos)
// })
