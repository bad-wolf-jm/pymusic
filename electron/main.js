'use strict';
const { ipcMain } = require('electron');
var electron = require('electron');

var app = electron.app;
var BrowserWindow = electron.BrowserWindow;

var mainWindow = null;

app.on('ready', function() {
    mainWindow = new BrowserWindow({
      width: 1728,
      height: 1152,
    });
    //mainWindow.setMenu(null);
    //mainWindow.loadURL('file://' + __dirname + '/pydjay_ui/main_ui.html');
    mainWindow.loadURL('file://' + __dirname + '/pydjay_ui/html_interface/main_window/main_window.html');
});

ipcMain.on('track-modified', (event, message) => {
  //console.log(message); // logs out "Hello second window!"
  mainWindow.webContents.send("track-modified", message)
})