'use strict';

var electron = require('electron');

var app = electron.app;
var BrowserWindow = electron.BrowserWindow;

var mainWindow = null;

app.on('ready', function() {
    mainWindow = new BrowserWindow({
      width: 1728,
      height: 1152,
    });
    mainWindow.setMenu(null);
    mainWindow.loadURL('file://' + __dirname + '/pydjay_ui/main_ui.html');
    // mainWindow.loadURL('file://' + __dirname + '/dbedit_ui/main_ui_edit.html');
});
