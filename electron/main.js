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

    mainWindow.loadURL('file://' + __dirname + '/pydjay_ui/html_interface/main_window/main_window.html');

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
      });
});

ipcMain.on('quit-pymusic', (event, message) => {
  mainWindow.close()
})