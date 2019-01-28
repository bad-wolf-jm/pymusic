class PlaylistController extends TrackListController {
    constructor(unavailable) {
        super(unavailable)
    }

    set_model(info, model) {
        super.set_model(info.name, model)
        this.info = info
    }

    save_playlist_tracks(y, k) {
        this.model.set_tracks(y, k)
    }

    append(e) {
        this.model.append(e)
    }

    remove(element) {
        //console.log(element)
        this.model.remove(element)
    }

    async get_id(id) {
        return this.model.getElementById(id)
    }

}