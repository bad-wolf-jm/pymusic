function queue_element_template(element) {
    var cover_source = null;
    if (element.cover == null) {
        cover_source = "../resources/images/default_album_cover.png"
    } else {
        cover_source = `${element.image_root}/${element.cover}`
    }
    return `<img class="ui left floated image"  style="float:left; width:auto;" src="${cover_source}" height='75' width='75'></img>
                <div style="float:left; width:200px">
                    <div style="height:20px; white-space:nowrap; overflow: hidden; text-overflow: ellipsis;"><b>${element.title}</b></div>
                    <div style="height:20px; white-space:nowrap; overflow: hidden; text-overflow: 'ellipsis'"><i>${element.artist}</i></div>
                    <div style="width:85px; height:20px">${element.bpm} BPM</div>
                </div>
                <div class="ui grey label" style="float:right; font-size:12px; flex-grow:0; position:relative; top:50%; transform: translateY(-50%)">
                    ${format_nanoseconds(element.stream_length)}
                </div>`
}


var queue_display_template = {
    //view:'template',
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
            itemHeight:40,
            css:{height:"1000px"},
            template: queue_element_template,
            type: { height: 75  },
        }]
}
