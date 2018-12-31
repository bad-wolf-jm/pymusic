class UnavailableModel extends BaseObjectSubsetModel {

    constructor(tracks_model) {
        super(tracks_model)
        this.initialize()
    }

    refresh(k) {
        DB.get_unavailable_tracks( (tracks) => {
            this.objects = {}
            tracks.forEach((t) => {
                this.objects[t.id] = t
            })
            super.refresh(k)
        })
    }


    compare_objects(a, b) {
        let x = a.title.toLowerCase();
        let y = b.title.toLowerCase();
        if (x < y) {return -1;}
        if (x > y) {return 1;}
        return 0;
    }

    get_all_tracks() {
        return this.get_all_objects()
    }

    get_track_by_id(id) {
        return this.get_object_by_id(id)
    }

    _check_availability(element, do_insert) {
        return (this.objects[element.id] == undefined)
    }

    add(element) {
        if (this.is_ready() && this._check_availability(element))  {
            super.add(element)
            this.save()
        }
    }
    
    remove(index) {
        if (this.is_ready()) {
            super.remove(index)
            this.save()
        }
    }

    save() {
        $QUERY("TRUNCATE unavailable_tracks", () => {
            let queue_tuples = []
            Object.keys(this.objects).forEach((k) => {
                queue_tuples.push(`(${k})`)
            })
            $QUERY(`INSERT INTO unavailable_tracks (track_id) VALUES ${queue_tuples.join(",")}`, () => {})
        })
    }
}
