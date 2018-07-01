class TrackList extends EventDispatcher {
    constructor() {
        super()
        this.header_id = `list-header-${this.ID()}`
        this.list_id = `list-${this.ID()}`
        this.cover_size = 45
    }

    ID () {
        return '_' + Math.random().toString(36).substr(2, 9);
    }

    init () {

    }

    element_template(element) {
        let cover_source = null;
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
    
    create_layout() {
        return  {
            type:'line',
            css:{
                border: '0px solid #3c3c3c',
            },
            rows:[
                {
                    id: this.header_id,
                    height:30,
                    css:{
                        'background-color':'#303030',
                        border: '1px solid #3c3c3c'
                     },
                     rows: [
                         {height:7},
                        {
                            view: 'label',
                            label: '<b>QUEUE</b>',
                            height: 20,
                            css:{
                                'padding-left':'10px',
                             }
                        },
                        {height:5},
                    ]
                },
                {
                    view:"list",
                    id:this.list_id,
                    css:{
                        border: '1px solid #3c3c3c',
                     },
                    select:true,
                    template: this.element_template,
                    type: { 
                        height: this.cover_size
                    },
                    scroll:"y"
                }
            ]
        }
    }

    set_track_list(list) {
        $$(this.list_id).clearAll()
        for(var i=0; i < list.length; i++){
            $$(this.list_id).add(list[i])
        }
    }

    get_selected() {
        return $$(this.list_id).getSelectedItem();
    }
    
    moveTop (x) {
        $$(this.list_id).moveTop(x.id)
    }

    moveUp (x) {
        $$(this.list_id).moveUp(x.id)
    }

    moveDown (x) {
        $$(this.list_id).moveDown(x.id)
    }

    remove (x) {
        $$(this.list_id).remove(x.id)
    }
}