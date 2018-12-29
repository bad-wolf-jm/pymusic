class BaseOrderedObjectSubsetModel extends BaseObjectSubsetModel {
    constructor(model) {
        super(model)
        this.ordering = []
    }

    get_all_objects() {
        return this.model.get_objects(this.ordering)
    }
}