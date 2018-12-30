class BaseOrderedObjectSubsetModel extends BaseObjectSubsetModel {
    constructor(model) {
        super(model)
        this.ordering = undefined
    }

    get_all_objects() {
        return this.model.get_objects(this.ordering)
    }

    reorder(new_order) {
        if (new_order.length == this.ordering.length) {
            if (new_order.every((x) => {return (this.objects[x] != undefined)})) {
                this.ordering = new_order
                this.dispatch("reorder", this.get_all_objects())
            }
        }
    }

    insert(element, index) {
        this.ordering.splice(index, 0, element.id)
        super.add(element)
    }

    append(element) {
        this.add(element)
    }

    add(element) {
        this.ordering.push(element.id)
        super.add(element)        
    }

    remove(element) {
        let index = this.ordering.indexOf(element.id)
        if (index != -1) {
            this.ordering.splice(index, 1)
            super.remove(element)
        }
    }
}