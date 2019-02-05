class SessionsView extends EventDispatcher {
    constructor(dom_ids) {
        super()
        this.dom_id          = dom_ids.list
        this.controller      = undefined
        this.list_dom        = document.getElementById(dom_ids.list); 
        this.view_list_order = []
    }

    set_controller(controller) {
        this.controller = controller
        this.controller.addView(this)
        this.controller.on("content-changed", this.set_list.bind(this))
        //this.controller.ready(this.set_list.bind(this))
    }

    set_list(list) {
        this.view_list_order = []
        let list_rows = []
        list.sort((a, b) => {return (b.date_start - a.date_start)})

        for(let i=0; i<list.length; i++) {
            let element = {
                id:   list[i]._id,
                name: list[i].event,
                data: list[i],
                date: moment(list[i].date_start).format("MM-DD-YYYY"),
            }
            list_rows.push(element)
        }

        jui.ready([ "grid.table" ], function(table) {
                table("#session-list-elements", {
                    data:   list_rows,
                    scroll: false,
                    resize: false
                });
            }
        )
    }
}