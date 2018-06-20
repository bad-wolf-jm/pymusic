class AudioDeck extends EventDispatcher{
    constructor () {
        super()
        this.speakers = new AudioPlayer()
        this.headphones = new AudioPlayer()
        this.editor = new AudioPlayer()
    }
}