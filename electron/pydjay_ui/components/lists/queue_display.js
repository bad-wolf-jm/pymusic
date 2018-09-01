

var cover_size = 42

function queue_element_template(element) {
    var cover_source = null;
    if (element.cover == null) {
        cover_source = "../resources/images/default_album_cover.png"
    } else {
        cover_source = `file://${element.image_root}/${element.cover}`
    }
    return `<img style="float:left; padding-right:7px; padding-left:-3px" src="${cover_source}" height='${cover_size}' width='${cover_size}'></img>
            <div style="margin:0px; padding:0px; float:left; width:275px">
                <div class="queue_element_title"><b>${element.title}</b></div>
                <div class="queue_element_artist"><i>${element.artist}</i></div>
            </div>
            <div class="queue_element_bpm">${element.bpm} BPM</div>
            <div class="queue_element_duration">
                <b>${format_nanoseconds(element.stream_length)}</b>
            </div>`
}

function update_queue_labels() {
    DB.get_queue_duration(
        function (result) {
            if (result.length == 0) {
                $$('queue_duration').define('label', `Duration: ${format_nanoseconds(0)}`);
                $$('queue_duration').refresh();
                d = new Date()
                $$('queue_ends_at').define('label', `Ends at: ${webix.Date.dateToStr('%H:%i:%s')(d)}`);
                $$('queue_ends_at').refresh();
            } else {
                queue_duration = result[0].duration;
                queue_count = result[0].count;
                wait_time = result[0].wait_time;
                current_time = new Date().getTime();
                total_time = queue_duration + (queue_count-1)*wait_time*1000000000;
                $$('queue_duration').define('label', `<span style="font-size:13px; color:rgb(150,150,150)"><b>QUEUE DURATION:</b></span> <span style="font-size:15px; color:rgb(225,225,225)">${format_nanoseconds(total_time)}</span>`);
                $$('queue_duration').refresh();
                current_time += (total_time / 1000000);
                d = new Date(current_time)
                $$('queue_ends_at').define('label', `<span style="font-size:13px; color:rgb(150,150,150)"><b>ENDS:</b></span> <span style="font-size:15px; color:rgb(225,225,225)">${webix.Date.dateToStr('%H:%i:%s')(d)}</span>`);
                $$('queue_ends_at').refresh();
            }
        }       
    )
}

var  queue_display_template = {
    type:'line',
    css:{
        border: '0px solid #3c3c3c',
    },
    rows:[
        {
            id: 'queue_list_header_row',
            height:50,
            css:{
                'background-color':'#303030',
                border: '1px solid #3c3c3c'
             },
             rows: [
                {height:15},
                {
                    view: 'label',
                    label: '<b>QUEUE</b>',
                    height: 20,
                    css:{
                        'padding-left':'10px',
                     }
                },
                {height:15},
            ]
        },
        {
            view:"list",
            id:'queue_list',
            css:{
                border: '1px solid #3c3c3c',
             },
            select:true,
            template: queue_element_template,
            type: { 
                height: cover_size
            },
            scroll:"y"
        }
    ]
}