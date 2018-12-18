
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
    focus_list.move_up()
});


Mousetrap.bind('down', () => {
    focus_list.move_down()
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


Mousetrap.bind('g i', function() { console.log('go to inbox'); });


// webix.UIManager.addHotKey("space",       () => self.audio_player.togglePause(),   $$(self.track_table.track_list));
// webix.UIManager.addHotKey("shift+space", () => self.audio_player.stop(),          $$(self.track_table.track_list));
// webix.UIManager.addHotKey("space",       () => self.audio_player.togglePause(),   $$(self.track_list.list_id));
// webix.UIManager.addHotKey("shift+space", () => self.audio_player.stop(),          $$(self.track_list.list_id));
// webix.UIManager.addHotKey("shift+a",     self.add_to_playlist,                    $$(self.track_table.track_list));
// webix.UIManager.addHotKey("ctrl+shift+enter", self.preview_last_30_seconds,       $$(self.track_table.track_list));
// webix.UIManager.addHotKey("shift+enter",      self.preview_last_10_seconds,       $$(self.track_table.track_list));
// webix.UIManager.addHotKey("enter",            self.preview_selected,              $$(self.track_table.track_list));
// webix.UIManager.addHotKey("ctrl+shift+enter", self.group_preview_last_30_seconds, $$(self.track_list.list_id));
// webix.UIManager.addHotKey("shift+enter",      self.group_preview_last_10_seconds, $$(self.track_list.list_id));
// webix.UIManager.addHotKey("enter",            self.group_preview_selected,        $$(self.track_list.list_id));
// webix.UIManager.addHotKey("delete",           self.remove_from_playlist,          $$(self.track_list.list_id));
// webix.UIManager.addHotKey("backspace",        self.remove_from_playlist,          $$(self.track_list.list_id));