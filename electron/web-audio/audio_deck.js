class AudioDeck extends EventDispatcher{
    constructor () {
        super()
        this.main = new AudioPlayer()
        this.prelisten = new AudioPlayer()
    }
}