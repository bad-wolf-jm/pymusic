//<span class='fa fa-heart'/>

function custom_checkbox(obj, common, value){
    if (value)
        return "<div class='webix_table_checkbox checked'><span class='fa fa-heart' style='font-size: 12px'/></div>";
    else
        return "<div class='webix_table_checkbox notchecked'><span class='fa fa-heart-o' style='font-size: 12px'/></div>";
};

var preview_player_window = {
    height:75,
    css:{
        'background-color':'#6c6c6c',
        'padding':'1px',
        border: '1px solid #3c3c3c'
     },
    cols:[
        {
            id:'preview-cover-image',
            view: 'template',
            width:75,
            height:75,
            template: ""
        },
        {width:10},
        {
            cols: [
                {

                    rows: [
                        {},

                        {
                            cols: [
                                {
                                    id:'preview_play_button',
                                    view:'button',
                                    type: 'icon',
                                    icon: 'headphones',
                                    width: 30,
                                },
                                {width:5},
                                {
                                    rows: [
                                        {
                                            height:18,
                                            template:'<div id="preview-progress" style="margin:0px; padding:0px; width:100%; height:100%; position:relative; top:0%; left:0%;"></div>'
                                            // template:'<div id="preview-progress" style="margin:0px; padding:0px; width:100%; height:100%; position:relative; top:0%; left:0%; transform: translateY(-200%)"></div>'
                                        },
                                        {height: 7},
                                        {cols:[
                                            {
                                                id:'preview_time',
                                                view: 'label',
                                                css:{
                                                    'text-align':'left',
                                                    'text-transform':'uppercase'
                                                },
                                                label: '0:00',
                                                height:15
                                            },
                                            {},
                                            {
                                                id:'preview_length',
                                                view: 'label',
                                                css:{'text-align':'right'},
                                                label: '0:00',
                                                height:15
                                            }
                        
                                        ]},                
                                    ]
                                },
                                {width:5},
                                {
                                    id:'preview_test_play_button',
                                    view:'button',
                                    type: 'icon',
                                    icon: 'play',
                                    width:30,
                                    popup: "preview_popup_menu"
                                },
                            ]
                        },
                        {}
                    ]
        
                },
                {width:10}
            ]
        }
    ]
    
}


// var preview_player_window_2 = {
//     height:75,
//     css:{
//         'background-color':'#6c6c6c',
//         'padding':'1px',
//         border: '1px solid #3c3c3c'
//      },
//     cols:[
//         {
//             id:'preview-cover-image',
//             view: 'template',
//             width:75,
//             height:75,
//             template: ""
//         },
//         {width:10},
//         {
//             rows: [
//                 {height:5},
//                 {
//                     cols: [
//                         {
//                             rows:[
//                                 {},
//                                 {
//                                     id:'preview_title',
//                                     view: 'label',
//                                     css: {
//                                         'text-align':'left',
//                                         'font-weight':'bold',
//                                         'text-transform':'uppercase',
//                                         'white-space':'nowrap',
//                                         'overflow': 'hidden',
//                                         'text-overflow': 'ellipsis'
//                                     },
//                                     label: 'Title Of Song',
//                                     height:20
//                                 },
//                                 {
//                                     id:'preview_artist',
//                                     view: 'label',
//                                     css: {
//                                         'text-align':'left',
//                                         'white-space':'nowrap',
//                                         'overflow': 'hidden',
//                                         'text-overflow': 'ellipsis'
//                                     },
//                                     label: 'Artist - Album',
//                                     height:20
//                                 },
//                                 // {
//                                 //     id:'preview_album',
//                                 //     view: 'label',
//                                 //     css: {
//                                 //         'text-align':'left',
//                                 //         'white-space':'nowrap',
//                                 //         'overflow': 'hidden',
//                                 //         'text-overflow': 'ellipsis'
//                                 //     },
//                                 //     label: 'Artist - Album',
//                                 //     height:20
//                                 // },
//                                 {}
//                             ]
//                         },
//                         {width:10},
//                         // {
//                         //     id:'preview_play_button',
//                         //     view:'button',
//                         //     type: 'icon',
//                         //     icon: 'pause',
//                         //     label:'PAUSE',
//                         //     width:100,
//                         //     click : function () {
//                         //         preview_pause();
//                         //     }
//                         // },

//                         // {
//                         //     id:'preview_play_last_30_seconds_button',
//                         //     view:'button',
//                         //     type: 'icon',
//                         //     icon: 'play',
//                         //     label: '-30 SECS',
//                         //     width:100,
//                         //     click : function () {
//                         //         if (preview_track_id != undefined) {
//                         //             preview_play_track_id(preview_track_id, -30000000000);
//                         //         }
//                         //         webix.UIManager.setFocus($$('track_edit_window'));
//                         //     }
//                         // },
//                         // {width:10},
//                         // {
//                         //     id:'preview_play_last_10_seconds_button',
//                         //     view:'button',
//                         //     type: 'icon',
//                         //     icon: 'play',
//                         //     label: '-10 SECS',
//                         //     width:100,
//                         //     click : function () {
//                         //         if (preview_track_id != undefined) {
//                         //             preview_play_track_id(preview_track_id, -10000000000);
//                         //         }
//                         //         webix.UIManager.setFocus($$('track_edit_window'));
//                         //     }
//                         // },
//                         // {
//                         //     id:'preview_stop_button',
//                         //     view:'button',
//                         //     type: 'icon',
//                         //     icon: 'stop',
//                         //     label:'STOP',
//                         //     width:100,
//                         //     click : function () {
//                         //         preview_stop();
//                         //     }

//                         // },
//                         {
//                             id:'preview_test_play_button',
//                             view:'button',
//                             type: 'icon',
//                             icon: 'play',
//                             width:30,
//                             // click : function () {
//                             // }
//                         },

//                     ]
//                 },

//                 {height: 5},
//                 {
//                     height:5,
//                     template:'<div id="preview-progress" style="margin:0px; padding:0px; width:100%; height:100%; position:relative; top:0%; left:0%; transform: translateY(-200%)"></div>'
//                 },
//                 {height: 3},
//                 {cols:[
//                     {
//                         id:'preview_time',
//                         view: 'label',
//                         css:{
//                             'text-align':'left',
//                             'text-transform':'uppercase'
//                         },
//                         label: '0:00',
//                         height:20
//                     },
//                     {},
//                     {
//                         id:'preview_length',
//                         view: 'label',
//                         css:{'text-align':'right'},
//                         label: '0:00',
//                         height:20
//                     }

//                 ]},
//             ]

//         },
//         {width:10}
//     ]
// }



var main_list_display_template = {
    type:'line',
    autoheight:true,
    css:{
        border: '0px solid #3c3c3c',
        //height: "100% !important"
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
        {
            view:"datatable",
            id:"display_list",
            select:"row",
            resizeColumn:{headerOnly:true},
            rowHeight:25,
            //autoheight:true,
            css:{
                'background-color':'#303030',
                border: '0px solid #5c5c5c',
                "font-size":'13px',
                //height: "87.5% !important"
             },
            columns:[
                { id:"id",            header:"",  width:30, hidden:true, template:"<img src='../resources/images/precue.png' style='filter: invert(1);' height='20'>", checkValue:1, uncheckValue:0},
                { id:"favorite",      header:{text:"<b><span class='fa fa-heart' style='font-size: 12px'/></b>", height:25},  width:30, template:custom_checkbox, checkValue:1, uncheckValue:0, sort:'int'},
                { id:"title",         header:"<b style='font-size: 13px'>Title</b>",  fillspace:true, sort:'string'},
                { id:"artist",        header:"<b style='font-size: 13px'>Artist</b>", fillspace:true, sort:'string'},
                //{ id:"album",         header:"<b style='font-size: 13px'>Album</b>",  fillspace:true, sort:'string'},
                { id:"genre",         header:"<b style='font-size: 13px'>Genre</b>",  width:100, sort:'string'},
                //{ id:"grouping",      header:"<b style='font-size: 13px'>Grouping</b>",  width:80, sort:'string'},
                { id:"play_count",    header:{text:"<b><span class='fa fa-play'/></b>", css:{"text-align":'center'}},  width:30, template:"<div style='text-align: right'>#play_count#</div>", sort:'int'},
                { id:"last_played",   header:{text:"<b><span class='fa fa-calendar' style='font-size: 15px'/></b>", css:{"text-align":'right'}},  width:80, template: function(element) { return `${webix.Date.dateToStr("%Y-%m-%d")(element.last_played)}`}, sort:'int'},
                { id:"rating",        header:{text:"<b style='font-size: 13px'>Rating</b>", css:{"text-align":'center'}}, width:75, template:"<img src='../resources/images/rating#rating#.png' style='' height='10'>", css:{"text-align":'right'}, sort:'int'},
                { id:"bpm",           header:{text:"<b style='font-size: 13px'><span class='fa fa-heartbeat' style='font-size: 15px'/></b>", css:{"text-align":'center'}}, width:45, css:{"text-align":'right'}, sort:'int'},
                { id:"stream_length", header:{text:"<b style='font-size: 13px'>Time</b>", css:{"text-align":'center'}}, width:55, format:format_nanoseconds, css:{"text-align":'right'}},
            ],
            scroll:"y"
        },
        //preview_player_window,
        {height:18}

    ]
}

function update_list_labels() {
    var count = $$('display_list').data.count();
    var length = 0;
    $$('display_list').data.each((row) => {length += row.stream_length})
    $$('playlist_track_count').define('label', `${count} tracks - ${format_seconds_long(length / 1000000000)}`);
    $$('playlist_track_count').refresh();
}
