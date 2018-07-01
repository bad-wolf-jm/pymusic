

class TrackTable extends EventDispatcher {
    constructor() {
        super()
        this.track_list = `playlist_track_list_${ID()}`
        this.track_list_filter = `playlist_track_list_filter_${ID()}`
        this.playlist_name = `playlist_name_${ID()}`
        this.playlist_track_count = `playlist_track_count_filter_${ID()}`
        this.header = `header_${ID()}`
        this.filtering = false
    }

    ID () {
        return '_' + Math.random().toString(36).substr(2, 9);
    }

    init() {
        $$(this.track_list).filterByAll = () => {
            this.filter_list($$(this.track_list_filter).getValue())
        } 
        $$(this.track_list).attachEvent('onAfterLoad', () => {
                this.update_list_labels()
            }
        )
        $$(this.track_list).attachEvent('onItemDblClick',
            (id) => {
                var id = this.get_selected_item()
                this.dispatch("item-selected", id)
            }
        );
        $$(this.track_list).attachEvent('onFocus',
            (id) => {
                this.dispatch("focus-in-list", id)
            }
        );
        $$(this.track_list).attachEvent('onBlur',
            (id) => {
                this.dispatch("focus-out-list", id)
            }
        );
        $$(this.track_list_filter).attachEvent('onFocus', (x) => {
                this.filtering=true;
                this.dispatch("focus-in-filter", id)
            }
        );
        $$(this.track_list_filter).attachEvent('onBlur', (x) => {
                this.filtering=false;
                this.dispatch("focus-out-filter", id)
            }
        );
    }

    update_list_labels() {
        var count = $$(this.track_list).data.count();
        var length = 0;
        $$(this.track_list).data.each((row) => {length += row.stream_length})
        $$(this.playlist_track_count).define('label', `${count} tracks - ${format_seconds_long(length / 1000000000)}`);
        $$(this.playlist_track_count).refresh();
    }

    custom_checkbox(obj, common, value){
        if (value)
            return `<div class='webix_table_checkbox checked'>
                        <span class='fa fa-heart' style='font-size: 12px; color:${obj.color}'/>
                    </div>`;
        else
            return `<div class='webix_table_checkbox notchecked'>
                        <span class='fa fa-heart-o' style='font-size: 12px; color:${obj.color}'/>
                    </div>`;
    };

    filter_list (text) {
        var i=0;
        let search_tokens = text.split(' ')
        let search_f = [];
        for (var i=0; i<search_tokens.length; i++) {
            let token = search_tokens[i];
            if (token.length > 0) {
                if (search_tokens[i].startsWith('@bpm<')) {
                    let x = parseInt(search_tokens[i].split('<')[1]);
                    if (!isNaN(x)) {
                        search_f.push(
                            function (obj) {
                                return obj.bpm <= x;
                            }
                        )
                    } else {
                        search_f.push( (x) => {return true} )
                    }
                } else if (search_tokens[i].startsWith('@bpm>')) {
                    let x = parseInt(search_tokens[i].split('>')[1]);
                    if (!isNaN(x)) {
                        search_f.push(
                            function (obj) {
                                return (obj.bpm >= x);
                            }
                        )
                    } else {
                        search_f.push( (x) => {return true} )
                    }
                } else if (search_tokens[i].startsWith('@bpm~')) {
                    let x = parseInt(search_tokens[i].split('~')[1]);
                    if (!isNaN(x)) {
                        search_f.push(
                            function (obj) {
                                return (obj.bpm < x*1.2) && (obj.bpm > x*0.9) ;
                            }
                        )
                    } else {
                        search_f.push( (x) => {return true} )
                    }
                } else {
                    search_f.push(
                        function (x) {
                            let fields = [x.title, x.artist, x.genre, `@rat=${x.rating}`, '@bpm']
                            if (x.favorite) {
                                fields.push('@loved')
                            }
                            for (let j=0; j<fields.length; j++) {
                                if (fields[j] != null) {
                                    if ((fields[j].toLowerCase().search(token) != -1)) {
                                        return true;
                                    }
                                }
                            }
                            return false;
                        }
                    )
                }
            }
        }
        $$(this.track_list).filter(
            function (obj) {
                for(i=0; i<search_f.length; i++) {
                    let x = search_f[i](obj);
                    if (!x) {
                        return false;
                    }
                }
                return true;
            }
        )
    };

    set_track_list (name, list_elements) {
        $$(this.track_list).clearAll()
        if (list_elements.length > 0) {
            for(let i=0; i<list_elements.length; i++){
                if (!list_elements[i].available){
                    list_elements[i].$css = "unavailable_track";
                }
            }
        }
        $$(this.track_list).define("data", list_elements)
        $$(this.track_list).refresh()  
        $$(this.playlist_name).define('label', name);
        $$(this.playlist_name).refresh();
    }
    
    get_selected_item() {
        return $$(this.track_list).getSelectedId();
    }

    create_layout() {
        return {
            type:'line',
            autoheight:true,
            css:{
                border: '0px solid #3c3c3c',
            },
            rows: [
                {
                    id: this.header,
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
                                id: this.playlist_name,
                                label: '<b>ALL SONGS</b>',
                                height: 20,
                                css:{
                                    'font-weight':  'bold',
                                    "text-transform": "uppercase"}
                            },
                            {
                                view: 'label',
                                id: this.playlist_track_count,
                                css: {'text-align':'left'},
                                label: 'Ends at:',
                                height: 20
                            }
                            ]
                        },
                        {
                            gravity:1,
                            id: this.track_list_filter,
                            view: 'search',
                            placeholder:"Filter list...",
                            keyPressTimeout:50,
                            on: {
                                onTimedKeyPress: () => {
                                    $$(this.track_list).filterByAll();
                                }
                            }
        
                        },
                        {width:10}
                    ]
                },
                {
                    view:"datatable",
                    id: this.track_list,
                    select:"row",
                    resizeColumn:{headerOnly:true},
                    rowHeight:25,
                    css:{
                        'background-color':'#303030',
                        border: '0px solid #5c5c5c',
                        "font-size":'13px',
                     },
                    columns:[
                        { 
                            id:       "id",            
                            header:   "",  
                            width:    30, 
                            hidden:   true, 
                            template: "<img src='../resources/images/precue.png' style='filter: invert(1);' height='20'>", 
                        },
                        { 
                            id:     "favorite",      
                            header: {
                                text: "<b><span class='fa fa-heart' style='font-size: 12px'/></b>", 
                                height:25
                            },  
                            width:        30, 
                            template:     this.custom_checkbox.bind(this), 
                            checkValue:   1, 
                            uncheckValue: 0, 
                            sort:        'int'
                        },
                        { 
                            id:       "title",         
                            header:   "<b style='font-size: 13px'>Title</b>",  
                            fillspace: true, 
                            sort:     'string', 
                            template: (o) => {
                                return `<span style="color:${o.color}">${o.title}</span>`
                            }
                        },
                        { 
                            id:       "artist",        
                            header:   "<b style='font-size: 13px'>Artist</b>", 
                            fillspace: true, 
                            sort:     'string', 
                            template: (o) => {
                                return `<span style="color:${o.color}">${o.artist}</span>`
                            }
                        },
                        { 
                            id:     "genre",         
                            header: "<b style='font-size: 13px'>Genre</b>",  
                            width:  100, 
                            sort:   'string', 
                            template: (o) => {
                                return `<span style="color:${o.color}">${o.genre}</span>`
                            }
                        },
                        { 
                            id:     "play_count",    
                            header: {
                                text:"<b><span class='fa fa-play'/></b>", 
                                css: {
                                    "text-align":'center'
                                }
                            },  
                            width:    30, 
                            template: `<div style='text-align: right; color:#color#'>#play_count#</div>`, 
                            sort:     'int'
                        },
                        { 
                            id:     "last_played",   
                            header: {
                                text:"<b><span class='fa fa-calendar' style='font-size: 15px'/></b>", 
                                css:{"text-align":'right'}
                            },  
                            width:    80, 
                            template: function(element) { 
                                return `<span style="color:${element.color}">
                                            ${webix.Date.dateToStr("%Y-%m-%d")(element.last_played)}
                                        </span>`
                            }, 
                            sort: 'int'
                        },
                        {
                            id:    "rating",        
                            header: {
                                text:"<b style='font-size: 13px'>Rating</b>", 
                                css:{"text-align":'center'}
                            }, 
                            width:    75, 
                            template: "<img src='../resources/images/rating#rating#.png' style='' height='10'>", 
                            css: {
                                "text-align":'right'
                            }, 
                            sort: 'int'
                        },
                        { 
                            id:     "bpm",           
                            header: {
                                text:"<b style='font-size: 13px'><span class='fa fa-heartbeat' style='font-size: 15px'/></b>", 
                                css:{"text-align":'center'}
                            }, 
                            width: 45, 
                            css: {
                                "text-align":'right'
                            }, 
                            sort: 'int', 
                            template: (o) => {
                                return `<span style="color:${o.color}">${o.bpm}</span>`
                            }
                        },
                        { 
                            id:     "stream_length", 
                            header: {
                                text: "<b style='font-size: 13px'>Time</b>", 
                                css:  {
                                    "text-align":'center'
                                }
                            }, 
                            width :55, 
                            css: {
                                "text-align":'right'
                            }, 
                            template: (o) => {
                                return `<span style="color:${o.color}">${format_nanoseconds(o.stream_length)}</span>`
                            }
                        },
                    ],
                    scroll:"y"
                },
                {height:18}
            ]
        }
        
    }
}