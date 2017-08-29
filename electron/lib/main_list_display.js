function custom_checkbox(obj, common, value){
    if (value)
        return "<div class='webix_table_checkbox checked'><img src='../resources/images/love-focus.png' height='13'> </div>";
    else
        return "<div class='webix_table_checkbox notchecked'><img src='../resources/images/love.png' height='13'> </div>";
};

var main_list_display_template = {
//container:"mainArticle",
rows:
[
    // {height:7},
    // {
    //     cols: [
    //         {
    //             rows:[
    //             {
    //                 view: 'label',
    //                 label: '<b>ALL SONGS</b>',
    //                 height: 20
    //             },
    //             {
    //                 view: 'label',
    //                 css: {'text-align':'left'},
    //                 label: 'Ends at:',
    //                 height: 20
    //             }
    //             ]
    //         },
    //         {
    //             view: 'search',
    //             placeholder:"Filter list..."
    //         },
    //         {width:10}
    //     ]
    // },
    // {height:5},
    {
        view:"datatable",
        id:"display_list",
        select:"row",
        resizeColumn:{headerOnly:true},
        css:{height:"1000px"},
        columns:[
            { id:"id",            header:"",  width:30, hidden:true, template:"<img src='../resources/images/precue.png' style='filter: invert(1);' height='20'>", checkValue:1, uncheckValue:0},
            { id:"favorite",      header:{text:"", height:25},  width:30, template:custom_checkbox, checkValue:1, uncheckValue:0, sort:'int'},
            { id:"title",         header:"<b>Title</b>",  fillspace:true, sort:'string'},
            { id:"artist",        header:"<b>Artist</b>", fillspace:true, sort:'string'},
            { id:"album",         header:"<b>Album</b>",  fillspace:true, sort:'string'},
            { id:"genre",         header:"<b>Genre</b>",  width:110, sort:'string'},
            { id:"play_count",    header:{text:"<b>Plays</b>", css:{"text-align":'center'}},  width:50,     template:"<div class='ui right floated label' style='text-align: right'>#play_count#</div>", sort:'int'},
            { id:"rating",        header:{text:"<b>Rating</b>", css:{"text-align":'center'}}, width:75,  template:"<img src='../resources/images/rating#rating#.png' style='filter: invert(1);' height='10'>", css:{"text-align":'right'}, sort:'int'},
            { id:"bpm",           header:{text:"<b>BPM</b>", css:{"text-align":'center'}},    width:50,     css:{"text-align":'right'}, sort:'int'},
            { id:"stream_length",      header:{text:"<b>Length</b>", css:{"text-align":'center'}},   width:75,       format:format_nanoseconds, css:{"text-align":'right'}},
        ]}
]
}
