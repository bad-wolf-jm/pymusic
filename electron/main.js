'use strict';

var electron = require('electron');

var app = electron.app;
var BrowserWindow = electron.BrowserWindow;

var mainWindow = null;
var mainWindow2 = null;
//var mysql = require('mysql');

//var db_connection = mysql.createConnection({
//  host: "localhost",
//  user: "root",
//  password: "root"
//});
//
//db_connection.connect(
//  function(err) {
//    if (err) throw err;
//    console.log("Connected!");
//});


app.on('ready', function() {
    mainWindow = new BrowserWindow({
      width: 1728,
      height: 1152
        //transparent: true, frame: false
    });

    mainWindow2 = new BrowserWindow({
      width: 1728,
      height: 1152
        //transparent: true, frame: false
    });

    //mainWindow.loadURL('file://' + __dirname + '/pydjay_ui/index.html');
    //mainWindow.loadURL('file://' + __dirname + '/pydjay_ui/index_queue.html');
    mainWindow.loadURL('file://' + __dirname + '/pydjay_ui/main_ui.html');
    //mainWindow2.loadURL('file://' + __dirname + '/pydjay_ui/index_big_table_simple.html');

    mainWindow.webContents.openDevTools()
});
