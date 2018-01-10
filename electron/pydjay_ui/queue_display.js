
var cover_size = 45


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
    db_connection.query(
        `SELECT SUM(duration) as duration, COUNT(id) as count, AVG(wait_time) as wait_time FROM
         (SELECT 1 as id, tracks.stream_length as duration, session_queue.id as count, settings.wait_time as wait_time
         FROM tracks JOIN session_queue ON tracks.id=session_queue.track_id LEFT JOIN settings on 1
         WHERE session_queue.status='pending' OR session_queue.status='playing') dummy GROUP BY id`,
         function (error, result) {
             //console.log(error);
             if (error) throw error;
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


function update_suggestions() {
    $QUERY(
        `SELECT availability.track_id IS NULL as available, tracks.id as id, tracks.title, tracks.artist, tracks.album,
         tracks.bpm, tracks.stream_length, settings.db_image_cache as image_root, tracks.cover_small as cover
         FROM (tracks LEFT JOIN settings ON 1 LEFT JOIN ((select track_id from unavailable_tracks) UNION
         (select track_id from session_queue)) availability ON availability.track_id=tracks.id) WHERE tracks.id IN
         (SELECT DISTINCT related_track_id FROM track_relations WHERE track_id IN (SELECT track_id FROM session_queue WHERE status='pending'))
         ORDER BY title ASC`,
         function (suggestions) {
             //function(queue_content) {
                 $$('suggestion_list').clearAll();
                 for(var i=0; i < suggestions.length; i++){
                     $$('suggestion_list').add(suggestions[i])
                     if (!(suggestions[i].available)) {
                         $$('suggestion_list').addCss(suggestions[i].id, 'unavailable_track');
                     }
                 }
                 if (suggestions.length == 0) {
                     $$('suggestion_number').define('label', `No tracks`)
                     $$('suggestion_number').refresh()

                 } else {
                     $$('suggestion_number').define('label', `${suggestions.length} track${suggestions.length > 1 ? "s" : ""}`)
                     $$('suggestion_number').refresh()
                 }
             //}
         }
    )



    db_connection.query(
        `SELECT SUM(duration) as duration, COUNT(id) as count, AVG(wait_time) as wait_time FROM
         (SELECT 1 as id, tracks.stream_length as duration, session_queue.id as count, settings.wait_time as wait_time
         FROM tracks JOIN session_queue ON tracks.id=session_queue.track_id LEFT JOIN settings on 1
         WHERE session_queue.status='pending' OR session_queue.status='playing') dummy GROUP BY id`,
         function (error, result) {
             //console.log(error);
             if (error) throw error;

             if (result.length == 0) {
                 $$('queue_duration').define('label', `<b>QUEUE DURATION:</b> ${format_nanoseconds(0)}`);
                 $$('queue_duration').refresh();
                 d = new Date()
                 $$('queue_ends_at').define('label', `<b>ENDS:</b> ${webix.Date.dateToStr('%H:%i:%s')(d)}`);
                 $$('queue_ends_at').refresh();
             } else {
                 queue_duration = result[0].duration;
                 queue_count = result[0].count;
                 wait_time = result[0].wait_time;
                 current_time = new Date().getTime();
                 total_time = queue_duration + (queue_count-1)*wait_time*1000000000;
                 $$('queue_duration').define('label', `<b>QUEUE DURATION:</b> ${format_nanoseconds(total_time)}`);
                 $$('queue_duration').refresh();
                 current_time += (total_time / 1000000);
                 d = new Date(current_time)
                 $$('queue_ends_at').define('label', `<b>ENDS:</b> ${webix.Date.dateToStr('%H:%i:%s')(d)}`);
                 $$('queue_ends_at').refresh();
             }
         }
    )
}



var queue_display_template = {
    type:'line',
    css:{
        border: '0px solid #3c3c3c'
    },
    rows:[
        {
            id: 'queue_list_header_row',
            css:{
                'background-color':'#5c5c5c',
                'padding':'5px',
                border: '1px solid #3c3c3c'
             },

            cols : [
                {width:5},
                {
                     rows: [
                        {
                            view: 'label',
                            label: '<b>QUEUE</b>',
                            height: 20
                        },
                        // {
                        //     cols:[
                        //         {
                        //             view: 'label',
                        //             id: 'queue_duration',
                        //             label: 'Duration:',
                        //             height: 20
                        //         },
                        //         {
                        //             view: 'label',
                        //             id:'queue_ends_at',
                        //             css: {'text-align':'right'},
                        //             label: 'Ends at:',
                        //             height: 20
                        //         }
                        //     ]
                        // }
                    ]
                },
                {width:15}
            ]

        },
        {
            view:"list",
            id:'queue_list',
            itemHeight:35,
            css:{
                border: '1px solid #3c3c3c'
             },
            select:true,
            template: queue_element_template,
            type: { height: cover_size  },
            scroll:"y"
        }]
}



var suggestions_display_template = {
    type:'line',
    //gravity:.75,
    height:440,
    css:{
        border: '0px solid #3c3c3c'
    },
    rows:[
        {
            id: 'suggestion_list_header_row',
            //height:40,
            css:{
                'background-color':'#5c5c5c',
                'padding':'5px',
                border: '1px solid #3c3c3c'
             },

            cols : [
                {width:5},
                {
                     rows: [
                        {
                            view: 'label',
                            label: '<b>SUGGESTIONS</b>',
                            height: 20
                        }
                        //,
                        // {
                        //     cols:[
                        //         {
                        //             view: 'label',
                        //             id: 'suggestion_number',
                        //             label: '### tracks',
                        //             height: 20
                        //         }
                        //     ]
                        // }
                    ]
                },
                {width:15}
            ]

        },
        {
            view:"list",
            id:'suggestion_list',
            itemHeight:45,
            css:{
                border: '1px solid #3c3c3c'
             },
            select:true,
            template: queue_element_template,
            type: { height: cover_size  },
            scroll:"y"

        }]
}
