
var cover_size = 55


function queue_element_template(element) {
    var cover_source = null;
    if (element.cover == null) {
        cover_source = "../resources/images/default_album_cover.png"
    } else {
        cover_source = `${element.image_root}/${element.cover}`
    }
    return `<img class="ui left floated image"  style="float:left; width:auto;" src="${cover_source}" height='${cover_size}' width='${cover_size}'></img>
            <div style="margin:0px; padding:0px; float:left; width:250px">
                <div style="margin:0px; padding:0px; height:22px; font_size:10px; white-space:nowrap; overflow: hidden; text-overflow: ellipsis;"><b>${element.title}</b></div>
                <div style="margin:0px; padding:0px; height:22px; font_size:10px; white-space:nowrap; overflow: hidden; text-overflow: ellipsis"><i>${element.artist}</i></div>
            </div>
            <div style="margin:0px; padding:0px; width:85px; font_size:8px; float:left; text-align:right; position:relative; top:50%; transform: translateY(-50%)">${element.bpm} BPM</div>
            <div style="float:right; position:relative; top:50%; transform: translateY(-50%)">
                <b>${format_nanoseconds(element.stream_length)}</b>
            </div>`
}


var queue_display_template = {
    type:'line',
    rows:[
        {height:7},
        {
            rows: [
                {
                    view: 'label',
                    label: '<b>QUEUE</b>',
                    height: 20
                },
                {
                    cols:[
                    {
                        view: 'label',
                        label: 'Duration:',
                        height: 20
                    },
                    {
                        view: 'label',
                        css: {'text-align':'right'},
                        label: 'Ends at:',
                        height: 20
                    }
                    ]
                }
            ]
        },
        {height:3},
        {
            view:"list",
            id:'queue_list',
            itemHeight:35,
            //css:{height:"1000px"},
            select:true,
            template: queue_element_template,
            type: { height: cover_size  },
        }]
}

//$$('queue_list').focus()
