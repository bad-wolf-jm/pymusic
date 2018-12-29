class BaseObjectSubsetModel extends BaseObjectListModel {
    constructor(model) {
        super()
        this.model = model
        this.model.on('metadata-changed', (x) => {
            this.dispatch("metadata-changed", x)
        })
    }

    get_object_by_id(id) {
        return this.model.get_object_by_id(id)
    }

    get_all_objects() {
        let idxs = Object.keys(this.objects).map((i) => {return parseInt(i)})
        return this.model.get_objects(idxs, this.compare_objects)
    }

    check_membership(element) {
        return (this.objects[element.id] != undefined)
    }

    set_metadata(track, metadata) {
        this.model.set_metadata(track, metadata)
    }

    is_empty() {
        return (this.objects == undefined) || (Objects.keys(this.objects).length == 0)
    }

    duration() {
        return this.model.duration(Object.keys(this.objects).map((i) => {return parseInt(i)}))
    }
}