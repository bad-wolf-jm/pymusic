'use strict';
const { ipcMain } = require('electron');
var electron = require('electron');

var app = electron.app;
var BrowserWindow = electron.BrowserWindow;

var mainWindow = null;
var mixerWindow = null;

app.on('ready', function() {
    mainWindow = new BrowserWindow({
      width: 1728,
      height: 1152,
    });
    mixerWindow = new BrowserWindow({
      width: 600,
      height: 400,
    });
    //mainWindow.setMenu(null);
    //mainWindow.loadURL('file://' + __dirname + '/pydjay_ui/main_ui.html');
    mainWindow.loadURL('file://' + __dirname + '/pydjay_ui/html_interface/main_window/main_window.html');
    mixerWindow.loadURL('file://' + __dirname + '/pydjay_ui/html_interface/mixer/main_window.html');
});

ipcMain.on('track-modified', (event, message) => {
  mainWindow.webContents.send("track-modified", message)
})

ipcMain.on('playback-start', (event, message) => {
  mainWindow.webContents.send("playback-start", message)
})

ipcMain.on('playback-stop', (event, message) => {
  mainWindow.webContents.send("playback-stop", message)
})


// message = {
//   track:"path",
//   stream_start: 0,
//   stream_end: 100,
//   channel:"master"
// }
ipcMain.on("mixer-play", (event, message) => {
  mixerWindow.webContents.send("play", message)
})

// message = {
//   channel:"master"
// }
ipcMain.on("mixer-pause", (event, message) => {
  mixerWindow.webContents.send("pause", message)
})

// message = {
//   channel:"master"
// }
ipcMain.on("mixer-resume", (event, message) => {
  mixerWindow.webContents.send("resume", message)
})



// message = {
//   channel:"master"
// }
ipcMain.on("mixer-toggle-play-pause", (event, message) => {
  mixerWindow.webContents.send("toggle-play-pause", message)
})


// message = {
//   channel:"master"
// }
ipcMain.on("mixer-stop", (event, message) => {
  mixerWindow.webContents.send("stop", message)
})


// message = {
//   channel:"master"
//   event_type:"master"
//   event_value:"master"
// }
ipcMain.on("mixer-event", (event, message) => {
  mixerWindow.webContents.send("stop", message)
})

ipcMain.on('headphone-end-of-stream', (event, message) => {
  mainWindow.webContents.send("headphone-end-of-stream", {})
})

ipcMain.on('headphone-playback-stopped',  (event, message) => {
  mainWindow.webContents.send("headphone-playback-stopped", {})
})

ipcMain.on('headphone-playback-paused', (event, message) => {
  mainWindow.webContents.send("headphone-playback-paused", {})
})

ipcMain.on('headphone-playback-started', (event, message) => {
  mainWindow.webContents.send("headphone-playback-started", {})
})

ipcMain.on('headphone-stream-position', (event, pos) => {
  mainWindow.webContents.send("headphone-stream-position", pos)
})


ipcMain.on('master-end-of-stream', (event, message) => {
  mainWindow.webContents.send("master-end-of-stream", {})
})

ipcMain.on('master-playback-stopped',  (event, message) => {
  mainWindow.webContents.send("master-playback-stopped", {})
})

ipcMain.on('master-playback-paused', (event, message) => {
  mainWindow.webContents.send("master-playback-paused", {})
})

ipcMain.on('master-playback-started', (event, message) => {
  mainWindow.webContents.send("master-playback-started", {})
})

ipcMain.on('master-stream-position', (event, pos) => {
  mainWindow.webContents.send("master-stream-position", pos)
})

