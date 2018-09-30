class AccordionView extends EventDispatcher {
    constructor(div_name) {
        super()
        this.div           = document.getElementById(div_name)
        let children       = this.div.children
        this.panels        = []
        this.headers       = []
        this.panel_heights = []
        this.panel_open    = []
        for (let i=0; i<children.length; i = i+2) {
            this.headers.push(children[i])
            this.panels.push(children[i+1])
            this.panel_open.push(false)
            let fixed_height_request = children[i+1].attributes["data-fixed-height"]
            if (fixed_height_request != undefined) {
                this.panel_heights.push(parseInt(fixed_height_request.value))
            } else {
                this.panel_heights.push(undefined)
            }
            children[i].addEventListener("click", (event) => {
                    console.log(event.target.classList)
                    if (event.target.classList.contains("action-icon")) {
                        if (!(this.panel_open[i / 2])) {
                            this.open_panel(i / 2)
                        }
                        //if (event.target.attributes["action"].value)    
                        this.dispatch(event.target.attributes["action"].value)
                    } else {
                        if (this.panel_open[i / 2]) {
                            this.close_panel(i / 2)
                        } else {
                            this.open_panel(i / 2)
                        }    
                    }
                    //console.log(event)
                }
            )
        }

        let total_height = this.div.clientHeight
        let header_height = 0
        for(let i=0; i<this.headers.length; i++) {
            header_height += this.headers[i].clientHeight
        }
        this.available_height = total_height - header_height
    }

    open_panel(i) {
        if (!(this.panel_open[i])) {
            this.headers[i].classList.add("active")
            let panel = this.panels[i]
            let height;
            if (this.panel_heights[i] != undefined) {
                height = this.panel_heights[i]
                let invariable_height = height
                let variable_height_panels = []
                for (let k=0; k<this.panels.length; k++) {
                    if (this.panel_open[k] && (this.panel_heights[k] != undefined)) {
                        invariable_height += this.panel_heights[k]
                    } else if (this.panel_open[k]) {
                        variable_height_panels.push(this.panels[k])
                    }
                }
                let available_height = this.available_height - invariable_height
                let split_height = available_height / (variable_height_panels.length)
                for (let j=0; j<variable_height_panels.length; j++) {
                    variable_height_panels[j].style.height = split_height + "px";
                    variable_height_panels[j].style.maxHeight = split_height + "px";
                }
            } else {
                let invariable_height = 0
                let variable_height_panels = []
                for (let k=0; k<this.panels.length; k++) {
                    if (this.panel_open[k] && (this.panel_heights[k] != undefined)) {
                        invariable_height += this.panel_heights[k]
                    } else if (this.panel_open[k]) {
                        variable_height_panels.push(this.panels[k])
                    }
                }
                let available_height = this.available_height - invariable_height
                let split_height = available_height / (variable_height_panels.length + 1)
                for (let j=0; j<variable_height_panels.length; j++) {
                    variable_height_panels[j].style.height = split_height + "px";
                    variable_height_panels[j].style.maxHeight = split_height + "px";
                }
                height = split_height
            }
            panel.style.height = height + "px";
            panel.style.maxHeight = height + "px";
            this.panel_open[i] = true
        }
    }

    close_panel(i) {
        if (this.panel_open[i]) {
            this.headers[i].classList.remove("active")
            let panel = this.panels[i]
            panel.style.maxHeight = null;
            this.panel_open[i] = false
            let invariable_height = 0
            let variable_height_panels = []
            for (let k=0; k<this.panels.length; k++) {
                if (this.panel_open[k] && (this.panel_heights[k] != undefined)) {
                    invariable_height += this.panel_heights[k]
                } else if (this.panel_open[k]) {
                    variable_height_panels.push(this.panels[k])
                }
            }
            let available_height = this.available_height - invariable_height
            let split_height = available_height / (variable_height_panels.length )
            for (let j=0; j<variable_height_panels.length; j++) {
                variable_height_panels[j].style.height = split_height + "px";
                variable_height_panels[j].style.maxHeight = split_height + "px";
            }
        }
    }
}