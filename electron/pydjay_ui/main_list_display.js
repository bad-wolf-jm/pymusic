function custom_checkbox(obj, common, value){
    if (value)
        return "<div class='webix_table_checkbox checked'><img src='../resources/images/love-focus.png' height='13'> </div>";
    else
        return "<div class='webix_table_checkbox notchecked'><img src='../resources/images/love.png' height='13'> </div>";
};

var preview_player_window = {
    height:90,
    //gravity:1,
    css:{
        'background-color':'#6c6c6c',
        'padding':'1px',
        border: '1px solid #3c3c3c'
     },
     rows: [{
            cols:[
                {
                    id:'preview-cover-image',
                    view: 'template',
                    width:58,
                    height:58,
                    template: "FOO"
                },
                {width:10},
                {
                    rows:[
                        {},
                        {
                            id:'preview_title',
                            view: 'label',
                            css: {
                                'text-align':'left',
                                'font-weight':'bold',
                                'text-transform':'uppercase',
                                'white-space':'nowrap',
                                'overflow': 'hidden',
                                'text-overflow': 'ellipsis'
                            },
                            label: 'Title Of Song',
                            height:20
                        },
                        {
                            id:'preview_artist',
                            view: 'label',
                            css: {
                                'text-align':'left',
                                'white-space':'nowrap',
                                'overflow': 'hidden',
                                'text-overflow': 'ellipsis'
                            },
                            label: 'Artist - Album',
                            height:20
                        },
                        {}
                    ]
                },
                {width:10},
                {
                    id:'preview_play_button',
                    view:'button',
                    type: 'icon',
                    icon: 'pause',
                    label:'PAUSE',
                    width:100,
                    click : function () {
                        preview_pause();
                    }
                },

                {
                    id:'preview_play_last_30_seconds_button',
                    view:'button',
                    type: 'icon',
                    icon: 'play',
                    label: '-30 SECS',
                    width:100,
                    click : function () {
                        if (preview_track_id != undefined) {
                            preview_play_track_id(preview_track_id, -30000000000);
                        }
                        webix.UIManager.setFocus($$('track_edit_window'));
                    }
                },
                {width:10},
                {
                    id:'preview_play_last_10_seconds_button',
                    view:'button',
                    type: 'icon',
                    icon: 'play',
                    label: '-10 SECS',
                    width:100,
                    click : function () {
                        if (preview_track_id != undefined) {
                            preview_play_track_id(preview_track_id, -10000000000);
                        }
                        webix.UIManager.setFocus($$('track_edit_window'));
                    }
                },
                {
                    id:'preview_stop_button',
                    view:'button',
                    type: 'icon',
                    icon: 'stop',
                    label:'STOP',
                    width:100,
                    click : function () {
                        preview_stop();
                    }

                },

            ]
        },
        {height: 5},
        {
            height:5,
            template:'<div id="preview-progress" style="margin:0px; padding:0px; width:100%; height:100%; position:relative; top:0%; left:0%; transform: translateY(-200%)"></div>'
        },
        {height: 3},
        {cols:[
            {
                id:'preview_time',
                view: 'label',
                css:{
                    'text-align':'left',
                    'text-transform':'uppercase'
                },
                label: '0:00',
                height:20
            },
            {},
            {
                id:'preview_length',
                view: 'label',
                css:{'text-align':'right'},
                label: '0:00',
                height:20
            }

        ]},
        {height:15},
        {
            rows: [
                // {
                //     cols: [
                //         {width: 10},
                //         // {
                //         //     id:'preview_play_last_30_seconds_button',
                //         //     view:'button',
                //         //     type: 'icon',
                //         //     icon: 'play-circle',
                //         //     label: '-30 SECS',
                //         //     click : function () {
                //         //         if (preview_track_id != undefined) {
                //         //             preview_play_track_id(preview_track_id, -30000000000);
                //         //         }
                //         //         webix.UIManager.setFocus($$('track_edit_window'));
                //         //     }
                //         // },
                //         // {width:10},
                //         // {
                //         //     id:'preview_play_last_10_seconds_button',
                //         //     view:'button',
                //         //     type: 'icon',
                //         //     icon: 'play-circle',
                //         //     label: '-10 SECS',
                //         //     click : function () {
                //         //         if (preview_track_id != undefined) {
                //         //             preview_play_track_id(preview_track_id, -10000000000);
                //         //         }
                //         //         webix.UIManager.setFocus($$('track_edit_window'));
                //         //     }
                //         // },
                //         {width: 10},
                //     ]
                // },
                {height:5},
                // {
                //     cols: [
                //         {width: 10},
                //         {
                //             id:'preview_play_button',
                //             view:'button',
                //             label:'PLAY/PAUSE',
                //             click : function () {
                //                 preview_pause();
                //             }
                //         },
                //         {width:10},
                //         // {
                //         //     id:'preview_stop_button',
                //         //     view:'button',
                //         //     label:'STOP',
                //         //     click : function () {
                //         //         preview_stop();
                //         //     }
                //         //
                //         // },
                //         {width: 10},
                //     ]
                // },
            ]
        },
        {}
    ]
}


var main_list_display_template = {
    type:'line',
    css:{
        border: '0px solid #3c3c3c'
     },
    rows: [
        {
            id: 'main_list_header_row',
            css:{
                'background-color':'#5c5c5c',
                'padding':'5px',
                border: '1px solid #3c3c3c'
             },

            cols: [
                {width:5},
                {
                    rows:[
                    {
                        view: 'label',
                        id: 'playlist_name',
                        label: '<b>ALL SONGS</b>',
                        height: 20,
                        css:{
                            'font-weight':  'bold',
                            "text-transform": "uppercase"}
                    },
                    {
                        view: 'label',
                        id: 'playlist_track_count',
                        css: {'text-align':'left'},
                        label: 'Ends at:',
                        height: 20
                    }
                    ]
                },
                {
                    gravity:1,
                    id: 'track_filter',
                    view: 'search',
                    placeholder:"Filter list...",
                    keyPressTimeout:50,
                    on: {
                        onTimedKeyPress: function (){
                            $$("display_list").filterByAll();
                        }
                    }

                },
                {width:10}
            ]
        },
        preview_player_window,
        {
            view:"datatable",
            id:"display_list",
            select:"row",
            resizeColumn:{headerOnly:true},
            css:{
                'background-color':'#303030',
                border: '0px solid #5c5c5c'
             },
            columns:[
                { id:"id",            header:"",  width:30, hidden:true, template:"<img src='../resources/images/precue.png' style='filter: invert(1);' height='20'>", checkValue:1, uncheckValue:0},
                { id:"favorite",      header:{text:"", height:25},  width:30, template:custom_checkbox, checkValue:1, uncheckValue:0, sort:'int'},
                { id:"title",         header:"<b>Title</b>",  fillspace:true, sort:'string'},
                { id:"artist",        header:"<b>Artist</b>", fillspace:true, sort:'string'},
                { id:"album",         header:"<b>Album</b>",  fillspace:true, sort:'string'},
                { id:"genre",         header:"<b>Genre</b>",  width:110, sort:'string'},
                { id:"play_count",    header:{text:"<b>Plays</b>", css:{"text-align":'center'}},  width:50, template:"<div style='text-align: right'>#play_count#</div>", sort:'int'},
                { id:"last_played",   header:{text:"<b>LAST</b>", css:{"text-align":'right'}},  width:100, template: function(element) { return `${webix.Date.dateToStr("%Y-%m-%d")(element.last_played)}`}, sort:'int'},
                { id:"rating",        header:{text:"<b>Rating</b>", css:{"text-align":'center'}}, width:75, template:"<img src='../resources/images/rating#rating#.png' style='' height='10'>", css:{"text-align":'right'}, sort:'int'},
                { id:"bpm",           header:{text:"<b>BPM</b>", css:{"text-align":'center'}},    width:50, css:{"text-align":'right'}, sort:'int'},
                { id:"stream_length", header:{text:"<b>Time</b>", css:{"text-align":'center'}},   width:55, format:format_nanoseconds, css:{"text-align":'right'}},
            ],
    }    ]
}

//${webix.Date.dateToStr("%Y-%m-%d")(element.date)}

function update_list_labels() {
    var count = $$('display_list').data.count();
    var length = 0;
    $$('display_list').data.each((row) => {length += row.stream_length})
    $$('playlist_track_count').define('label', `${count} tracks - ${format_seconds_long(length / 1000000000)}`);
    $$('playlist_track_count').refresh();
}
