class TopMenu {
    constructor () {
        // pass
    }

    ID () {
        return Math.random().toString(36).substr(2, 9);
    }

    add_files() {
        dialog.showOpenDialog(
            { 
                properties: [ 'openFile', 'multiSelections'],
                filters: [
                    {name: 'MP# Music files', extensions: ['mp3', 'MP3']},
                ]
            },
            function (filenames) {
                var x = new TrackAdder(filenames)
            }
        )
    }
    

    create_layout() {
        return {
            view: 'menu',
            width:70,
            data:[
                { 
                    id:1, 
                    value: "", 
                    icon: "cog",
                    submenu: [
                        {
                            id: 'add-tracks',
                            value: "Add tracks"
                        },
                        {
                            $template: "Separator"
                        },
                    ]
                }
            ],
            on:{
                onMenuItemClick: (id) => {
                    if (id == "add-tracks") {
                        this.add_files()
                    }
                }
            }
        }
    }
}