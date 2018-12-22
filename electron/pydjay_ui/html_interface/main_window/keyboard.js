var focus_list = undefined


function focusWindow(w) {
    if (focus_list != undefined) {
        focus_list.blur()
    }
    focus_list = w
    if (focus_list != undefined) {
        focus_list.focus()
    }
}


var lists = [T, Q]


Mousetrap.bind(["shift+delete", "shift+backspace"], (e) => {
    if (focus_list != undefined) {
        focus_list.delete_selection()
        e.preventDefault()
    }
})

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


Mousetrap.bind('Q', (e) => {
    if (focus_list != undefined) {
        focus_list.add_selection_to_queue()
        e.preventDefault()
    }
});


Mousetrap.bind('S', (e) => {
    if (focus_list != undefined) {
        focus_list.add_selection_to_shortlist()
        e.preventDefault()
    }
});


Mousetrap.bind(': + u', (e) => {
    if (focus_list != undefined) {
        focus_list.add_selection_to_unavailable()
        e.preventDefault()
    }
});


Mousetrap.bind(': - u', (e) => {
    if (focus_list != undefined) {
        focus_list.remove_selection_from_unavailable()
        e.preventDefault()
    }
});


Mousetrap.bind('ctrl+f', (e) => {
    document.getElementById("filter-track-list").focus()
    e.preventDefault()
});


Mousetrap.bind('left', (e) => {
    index = lists.indexOf(focus_list)
    if (index != -1) {
        if (index - 1 < 0) {
            focusWindow(undefined)
            e.preventDefault()
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


Mousetrap.bind('shift+home', (e) => {
    if (focus_list != undefined) {
        focus_list.move_first()
        e.preventDefault()
    }
});


Mousetrap.bind('pagedown', (e) => {
    if (focus_list != undefined) {
        focus_list.page_down()
        e.preventDefault()
    }
});


Mousetrap.bind('pageup', (e) => {
    if (focus_list != undefined) {
        focus_list.page_up()
        e.preventDefault()
    }
});


Mousetrap.bind('shift+end', (e) => {
    if (focus_list != undefined) {
        focus_list.move_last()
        e.preventDefault()
    }
});


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
        pc.play(focus_list.selected_element())
        e.preventDefault()
    }
})

Mousetrap.bind("shift+enter", (e) => {
    if (focus_list != undefined) {
        pc.play_last_30_seconds(focus_list.selected_element())
        e.preventDefault()
    }
})

Mousetrap.bind("ctrl+shift+enter", (e) => {
    if (focus_list != undefined) {
        pc.play_last_10_seconds(focus_list.selected_element())
        e.preventDefault()
    }
})

Mousetrap.bind("shift+left", (e) => {
    if (focus_list != undefined) {
        pc.skip(-1)
        e.preventDefault()
    }
})

Mousetrap.bind("shift+right", (e) => {
    if (focus_list != undefined) {
        pc.skip(1)
        e.preventDefault()
    }
})

Mousetrap.bind("ctrl+shift+left", (e) => {
    if (focus_list != undefined) {
        pc.skip(-5)
        e.preventDefault()
    }
})

Mousetrap.bind("ctrl+shift+right", (e) => {
    if (focus_list != undefined) {
        pc.skip(5)
        e.preventDefault()
    }
})


Mousetrap.bind(": alt+t", (e) => {
    let window = electron.remote.getCurrentWindow();
    window.openDevTools();
    e.preventDefault()
})


Mousetrap.bind(": alt+f", () => {
    let window = electron.remote.getCurrentWindow();
    window.setFullScreen(!(window.isFullScreen()));
    e.preventDefault()
})


Mousetrap.bind(": alt+r", () => {
    let window = electron.remote.getCurrentWindow();
    window.reload();
    e.preventDefault()
})


Mousetrap.bind(": alt+q", () => {
    let window = electron.remote.getCurrentWindow();
    e.preventDefault()
})
