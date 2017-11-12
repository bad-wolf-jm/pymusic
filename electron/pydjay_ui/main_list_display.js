function custom_checkbox(obj, common, value){
    if (value)
        return "<div class='webix_table_checkbox checked'><img src='../resources/images/love-focus.png' height='13'> </div>";
    else
        return "<div class='webix_table_checkbox notchecked'><img src='../resources/images/love.png' height='13'> </div>";
};

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
                { id:"rating",        header:{text:"<b>Rating</b>", css:{"text-align":'center'}}, width:75, template:"<img src='../resources/images/rating#rating#.png' style='' height='10'>", css:{"text-align":'right'}, sort:'int'},
                { id:"bpm",           header:{text:"<b>BPM</b>", css:{"text-align":'center'}},    width:50, css:{"text-align":'right'}, sort:'int'},
                { id:"stream_length", header:{text:"<b>Time</b>", css:{"text-align":'center'}},   width:55, format:format_nanoseconds, css:{"text-align":'right'}},
            ],
    }    ]
}


function update_list_labels() {
    var count = $$('display_list').data.count();
    var length = 0;
    $$('display_list').data.each((row) => {length += row.stream_length})
    $$('playlist_track_count').define('label', `${count} tracks - ${format_seconds_long(length / 1000000000)}`);
    $$('playlist_track_count').refresh();
}
