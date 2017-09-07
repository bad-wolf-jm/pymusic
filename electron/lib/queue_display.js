
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

function update_queue_labels() {
    db_connection.query(
        `SELECT SUM(duration) as duration, COUNT(id) as count, AVG(wait_time) as wait_time FROM
         (SELECT 1 as id, tracks.stream_length as duration, session_queue.id as count, settings.wait_time as wait_time
         FROM tracks JOIN session_queue ON tracks.id=session_queue.track_id LEFT JOIN settings on 1
         WHERE session_queue.status='pending' OR session_queue.status='playing') dummy GROUP BY id`,
         function (error, result) {
             console.log(error);
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
                 $$('queue_duration').define('label', `Duration: ${format_nanoseconds(total_time)}`);
                 $$('queue_duration').refresh();
                 current_time += (total_time / 1000000);
                 d = new Date(current_time)
                 $$('queue_ends_at').define('label', `Ends at: ${webix.Date.dateToStr('%H:%i:%s')(d)}`);
                 $$('queue_ends_at').refresh();
             }
         }
    )
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
                        id: 'queue_duration',
                        label: 'Duration:',
                        height: 20
                    },
                    {
                        view: 'label',
                        id:'queue_ends_at',
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
