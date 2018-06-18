class AudioDecoder {

    constructor() {
        this.arraybuffer = null;
    }

    load(url, callback, errback) { 
        var xhr = new XMLHttpRequest();
        this.arraybuffer = null;
        xhr.open('GET', url, true);
        xhr.responseType = "arraybuffer";

        xhr.addEventListener('load', e => {
            if (200 == xhr.status || 206 == xhr.status) {
                this.decodeArrayBuffer(xhr.response, callback, errback);
            } else {
                errback(e);
            }
        });
        xhr.send();
    }

    elapsed(x) {
        console.log(x)
        console.log(new Date() - this.start_time)
    }

    decodeArrayBuffer(arraybuffer, callback, errback) {
        this.arraybuffer = arraybuffer
        this.start_time = new Date()
        this.decoding_audio_context = new OfflineAudioContext(2, 16*4096*4096, 44100)
        this.decoding_audio_context.decodeAudioData(arraybuffer, callback.bind(this), errback);
    }
}