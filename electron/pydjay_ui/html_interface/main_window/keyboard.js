
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


Mousetrap.bind('up', (e) => {
    if (focus_list != undefined) {
        focus_list.move_up()
        e.preventDefault()
    }
});


Mousetrap.bind('down', (e) => {
    if (focus_list != undefined) {
        focus_list.move_down()
        e.preventDefault()
    }
});


Mousetrap.bind('left', (e) => {
    index = lists.indexOf(focus_list)
    if (index != -1) {
        if (index - 1 < 0) {
            focusWindow(undefined)
            e.preventDefault()
            // e.preventDefault()
        } else {
            focusWindow(lists[index - 1])
            e.preventDefault()
        }
    } else {
        focusWindow(lists[lists.length - 1])
        e.preventDefault()
    }
});


Mousetrap.bind('right', (e) => {
    index = lists.indexOf(focus_list)
    if (index != -1) {
        if (index + 1 >= lists.length) {
            focusWindow(undefined)
            e.preventDefault()
        } else {
            focusWindow(lists[index + 1])
            e.preventDefault()
        }
    } else {
        focusWindow(lists[0])
        e.preventDefault()
    }
});


Mousetrap.bind('home', () => {
    console.log('home');
});


Mousetrap.bind('shift+home', (e) => {
    if (focus_list != undefined) {
        focus_list.move_first()
        e.preventDefault()
    }
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


Mousetrap.bind('shift+end', (e) => {
    if (focus_list != undefined) {
        focus_list.move_last()
        e.preventDefault()
    }
});


// Mousetrap.bind('g i', function() { console.log('go to inbox'); });


Mousetrap.bind("space", (e) => {
    if ((pc.state == "PAUSED") || (pc.state == "PLAYING")) {
        pc.togglePause()
    } else {
        if (pc.track != undefined) {
            pc.play(pc.track)
        }
    }
    e.preventDefault()
})


Mousetrap.bind("shift+space", (e) => {
    pc.stop()
    e.preventDefault()
})


Mousetrap.bind("enter", () => {
    if (focus_list != undefined) {
        pc.play(focus_list.controller.selection[0])
        e.preventDefault()
    }
})

Mousetrap.bind("shift+enter", (e) => {
    if (focus_list != undefined) {
        pc.play_last_30_seconds(focus_list.controller.selection[0])
        e.preventDefault()
    }
})

Mousetrap.bind("ctrl+shift+enter", (e) => {
    if (focus_list != undefined) {
        pc.play_last_10_seconds(focus_list.controller.selection[0])
        e.preventDefault()
    }
})


Mousetrap.bind("shift+left", (e) => {
    if (focus_list != undefined) {
        // pc.play_last_10_seconds(focus_list.controller.selection[0])
    }
})

Mousetrap.bind("shift+right", (e) => {
    if (focus_list != undefined) {
        // pc.play_last_10_seconds(focus_list.controller.selection[0])
    }
})


Mousetrap.bind("ctrl+shift+left", (e) => {
    if (focus_list != undefined) {
        // pc.play_last_10_seconds(focus_list.controller.selection[0])
    }
})

Mousetrap.bind("ctrl+shift+right", (e) => {
    if (focus_list != undefined) {
        // pc.play_last_10_seconds(focus_list.controller.selection[0])
    }
})


Mousetrap.bind(": alt+t", (e) => {
    let window = electron.remote.getCurrentWindow();
    window.openDevTools();
})


Mousetrap.bind(": alt+f", () => {
    let window = electron.remote.getCurrentWindow();
    window.setFullScreen(!(window.isFullScreen()));
})


Mousetrap.bind(": alt+r", () => {
    let window = electron.remote.getCurrentWindow();
    window.reload();
})


Mousetrap.bind(": alt+q", () => {
    let window = electron.remote.getCurrentWindow();
    // QUIT
    //window.reload();
})


// webix.UIManager.addHotKey("shift+a",     self.add_to_playlist,                    $$(self.track_table.track_list));
// webix.UIManager.addHotKey("ctrl+shift+enter", self.group_preview_last_30_seconds, $$(self.track_list.list_id));
// webix.UIManager.addHotKey("shift+enter",      self.group_preview_last_10_seconds, $$(self.track_list.list_id));
// webix.UIManager.addHotKey("enter",            self.group_preview_selected,        $$(self.track_list.list_id));
// webix.UIManager.addHotKey("delete",           self.remove_from_playlist,          $$(self.track_list.list_id));
// webix.UIManager.addHotKey("backspace",        self.remove_from_playlist,          $$(self.track_list.list_id));
