
//var keyboard_listener = Mousetrap()

var focus_list = undefined

// var main_list_area = document.getElementById("main-list")
// var queue_list_area = document.getElementById("queue-list")


function focusWindow(w) {
    if (focus_list != undefined) {
        focus_list.blur() //classList.remove("focus")
    }
    focus_list = w
    if (focus_list != undefined) {
        focus_list.focus()
    }
}


var lists = [T, Q]


Mousetrap.bind('esc', () => {
    console.log('escape');
});


Mousetrap.bind('up', () => {
    if (focus_list != undefined) {
        focus_list.move_up()
    }
});


Mousetrap.bind('down', () => {
    if (focus_list != undefined) {
        focus_list.move_down()
    }
});


Mousetrap.bind('left', () => {
    index = lists.indexOf(focus_list)
    if (index != -1) {
        if (index - 1 < 0) {
            focusWindow(undefined)
        } else {
            focusWindow(lists[index - 1])
        }
    } else {
        focusWindow(lists[lists.length - 1])
    }
});


Mousetrap.bind('right', () => {
    index = lists.indexOf(focus_list)
    if (index != -1) {
        if (index + 1 >= lists.length) {
            focusWindow(undefined)
        } else {
            focusWindow(lists[index + 1])
        }
    } else {
        focusWindow(lists[0])
    }
});


Mousetrap.bind('home', () => {
    console.log('home');
});


Mousetrap.bind('shift+home', () => {
    console.log('home');
});



Mousetrap.bind('pagedown', () => {
    console.log('');
});

Mousetrap.bind('pageup', () => {
    console.log('');
});


Mousetrap.bind('end', () => {
    console.log('');
});


Mousetrap.bind('alt+end', () => {
    console.log('');
});


Mousetrap.bind('g i', function() { console.log('go to inbox'); });


Mousetrap.bind("space", () => {
    if ((pc.state == "PAUSED") || (pc.state == "PLAYING")) {
        pc.togglePause()
    } else {
        if (pc.track != undefined) {
            pc.play(pc.track)
        }
    }
})


Mousetrap.bind("shift+space", () => {
    pc.stop()
})


Mousetrap.bind("enter", () => {
    if (focus_list != undefined) {
        pc.play(focus_list.controller.selection[0])
    }
})

Mousetrap.bind("shift+enter", () => {
    if (focus_list != undefined) {
        pc.play_last_30_seconds(focus_list.controller.selection[0])
    }
})

Mousetrap.bind("ctrl+shift+enter", () => {
    if (focus_list != undefined) {
        pc.play_last_10_seconds(focus_list.controller.selection[0])
    }
})


Mousetrap.bind("shift+left", () => {
    if (focus_list != undefined) {
        // pc.play_last_10_seconds(focus_list.controller.selection[0])
    }
})

Mousetrap.bind("shift+right", () => {
    if (focus_list != undefined) {
        // pc.play_last_10_seconds(focus_list.controller.selection[0])
    }
})


Mousetrap.bind("ctrl+shift+left", () => {
    if (focus_list != undefined) {
        // pc.play_last_10_seconds(focus_list.controller.selection[0])
    }
})

Mousetrap.bind("ctrl+shift+right", () => {
    if (focus_list != undefined) {
        // pc.play_last_10_seconds(focus_list.controller.selection[0])
    }
})



Mousetrap.bind(": T", () => {
    let window = electron.remote.getCurrentWindow();
    window.openDevTools();
})


Mousetrap.bind(": F", () => {
    let window = electron.remote.getCurrentWindow();
    window.setFullScreen(!(window.isFullScreen()));
})

// webix.UIManager.addHotKey("shift+a",     self.add_to_playlist,                    $$(self.track_table.track_list));
// webix.UIManager.addHotKey("ctrl+shift+enter", self.group_preview_last_30_seconds, $$(self.track_list.list_id));
// webix.UIManager.addHotKey("shift+enter",      self.group_preview_last_10_seconds, $$(self.track_list.list_id));
// webix.UIManager.addHotKey("enter",            self.group_preview_selected,        $$(self.track_list.list_id));
// webix.UIManager.addHotKey("delete",           self.remove_from_playlist,          $$(self.track_list.list_id));
// webix.UIManager.addHotKey("backspace",        self.remove_from_playlist,          $$(self.track_list.list_id));
