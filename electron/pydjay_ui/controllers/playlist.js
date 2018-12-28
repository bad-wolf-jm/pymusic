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
}