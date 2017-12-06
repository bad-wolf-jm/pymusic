function custom_checkbox(obj, common, value){
    if (value)
        return "<div class='webix_table_checkbox checked'><img src='../resources/images/love-focus.png' height='13'> </div>";
    else
        return "<div class='webix_table_checkbox notchecked'><img src='../resources/images/love.png' height='13'> </div>";
};

function cover_art_template(element, common, value) {
    var cover_source = null;
    var cover_size = 30;
    //console.log(element, common, value);
    if (element.cover == null) {
        cover_source = "../resources/images/default_album_cover.png"
    } else {
        cover_source = `file://${element.image_root}/${element.cover}`
    }
    return `<img style="padding-right:0px; padding-left:-10px; margin-left:-10px" src="${cover_source}" height='${cover_size}' width='${cover_size}'></img>`
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
        {
            view:"datatable",
            id:"display_list",
            select:"row",
            editable:true,
            editaction:'dblclick',
            resizeColumn:{headerOnly:true},
            css:{
                'background-color':'#303030',
                border: '0px solid #5c5c5c'
             },
            columns:[
                { id:"id",            header:"",  width:30, hidden:true, template:"<img src='../resources/images/precue.png' style='filter: invert(1);' height='20'>", checkValue:1, uncheckValue:0},
                { id:"enabled",       header:"", width:35, checkValue:1, uncheckValue:0,  template:"{common.checkbox()}", sort:'int'},
                { id:"favorite",      header:{text:"", height:25},  width:35, template:custom_checkbox, checkValue:1, uncheckValue:0, sort:'int'},
                { id:"cover",         header:{text:"", height:25},  width:30, template:cover_art_template, checkValue:1, uncheckValue:0, sort:'int'},
                { id:"title",         header:"<b>Title</b>",  fillspace:true, sort:'string', editor: 'text'},
                { id:"artist",        header:"<b>Artist</b>", fillspace:true, sort:'string', editor: 'text'},
                { id:"album",         header:"<b>Album</b>",  fillspace:true, sort:'string', editor: 'text'},
                { id:"year",          header:"<b>Year</b>",   width:50, sort:'string', editor: 'text'},
                { id:"genre",         header:"<b>Genre</b>",  width:110, sort:'string', editor: 'text'},
                { id:"category",      header:"<b>Category</b>",  fillspace:true, sort:'string', editor: 'text'},
                { id:"description",   header:"<b>Description</b>", fillspace:true, sort:'string', editor: 'text'},
                { id:"play_count",    header:{text:"<b>Plays</b>", css:{"text-align":'center'}},  width:50, template:"<div style='text-align: right'>#play_count#</div>", sort:'int'},
                { id:"rating",        header:{text:"<b>Rating</b>", css:{"text-align":'center'}}, width:75, template:"<img src='../resources/images/rating#rating#.png' style='' height='10'>", css:{"text-align":'right'}, sort:'int'},
                { id:"bpm",           header:{text:"<b>BPM</b>", css:{"text-align":'center'}},    width:50, css:{"text-align":'right'}, sort:'int', editor: 'text'},
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
