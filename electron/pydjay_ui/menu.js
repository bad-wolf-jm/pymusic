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
    
    playback_settings() {
        db_connection.query(
            'SELECT wait_time FROM settings',
            function (e, r) {
                if (e) throw e;
                let wait_time = r[0].wait_time;
                let x = webix.ui({
                    view:"window",
                    modal:true,
                    position:"center",
                    width:600,
                    height:400,
                    head: "PLAYBACK SETTINGS",
                    body:{
                        rows:[
                            {height:10},
                            {
                                id:'wait_time',
                                view: "text",
                                value: `${wait_time}`,
                                labelWidth:225,
                                label:"Delay between tracks (seconds):"
                            },
                            {height:30},
                            {
                                view: "button",
                                type: 'icon',
                                icon: "headphones",
                                label: "Reset audio system",
                                click: reset_audio
    
                            },
                            {height:30},
                            {
                                cols:[
                                    {},
                                    {
                                        view: 'button',
                                        label: 'APPLY',
                                        click: () => {
                                            db_connection.query(
                                                `UPDATE settings SET wait_time=${parseInt($$('wait_time').getValue())}`,
                                                (error, _) => {
                                                    if (error) throw error;
                                                    x.hide();
                                                }
                                            )
                                            x.hide();
                                        }
                                    },
                                    {},
                                    {
                                        view: 'button',
                                        label: 'CANCEL',
                                        click: () => {x.hide()}
                                    },
                                    {}
                                ]
                            },
                            {height:10}
                        ]
                    }
                })
                x.show();
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
                        {
                            id: 'settings',
                            value: "Settings"
                        },
                    ]
                }
            ],
            on:{
                onMenuItemClick: (id) => {
                    if (id == "add-tracks") {
                        this.add_files()
                    } else if (id == "settings") {
                        this.playback_settings()
                    }
                }
            }
        }
    }
}