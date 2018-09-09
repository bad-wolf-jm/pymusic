class PlaylistsView extends EventDispatcher {
    constructor(dom_ids) {
        super()
        this.dom_id          = dom_ids.list
        this.controller      = undefined
        this.list_dom        = document.getElementById(dom_ids.list); 
        // this.num_tracks_dom = document.getElementById(dom_ids.num_tracks); 
        // this.duration_dom   = document.getElementById(dom_ids.duration);
        this.view_list_order = []
        // this.sortable = Sortable.create(this.list_dom, 
        //     {
        //         animation: 150,
        //         ghostClass: "ghost",

        //         onStart: function (evt) {
        //             console.log("start");
        //         },
            
        //         onEnd: (evt) => {
        //             let new_order = []
        //             for(i=0; i<this.list_dom.rows.length; i++) {
        //                 new_order.push(parseInt(this.list_dom.rows[i].attributes["data-track-id"].value))
        //             }
        //             this.view_list_order = new_order
        //             this.dispatch("reorder", this.view_list_order)
        //         },
        //     }
        // )
    }

    set_controller(controller) {
        this.controller = controller
        this.controller.addView(this)
        this.controller.on("content-changed", this.set_list.bind(this))
        this.controller.ready(this.set_list.bind(this))
    }

    set_list(list) {
        this.view_list_order = []
        let list_rows = []  

        for(i=0; i<list.length; i++) {
            let element = {
                id:   list[i].id,
                name: list[i].name,
            }
            list_rows.push(element)
        }
        jui.ready([ "grid.table" ], function(table) {
                table("#playlist-list-elements", {
                    data:   list_rows,
                    scroll: false,
                    resize: false
                });
            }
        )
    }
}