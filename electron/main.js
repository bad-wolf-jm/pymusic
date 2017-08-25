'use strict';

var electron = require('electron');

var app = electron.app;
var BrowserWindow = electron.BrowserWindow;

var mainWindow = null;

var mysql = require('mysql');

var db_connection = mysql.createConnection({
  host: "localhost",
  user: "root",
  password: "root"
});

db_connection.connect(
  function(err) {
    if (err) throw err;
    console.log("Connected!");
});


app.on('ready', function() {
    mainWindow = new BrowserWindow({
      width: 2160,
      height: 1440
        //transparent: true, frame: false
    });

    mainWindow.loadURL('file://' + __dirname + '/pydjay_ui/index.html');
});
