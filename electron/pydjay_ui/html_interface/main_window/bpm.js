class BPM {

    constructor() {
        this.count = 0;
        this.ts = 0;
        this.old_ts = 0;
    }
  
    tap() {
        this.ts = Date.now();
        if (!this.first_ts) this.first_ts = this.ts;
    
        let ret = {};
    
        // ignore the first tap
        if (this.old_ts) {
            let ms = this.ts - this.old_ts;
        
            let avg = 60000 * this.count / (this.ts - this.first_ts);
        
            ret.avg = avg;
            ret.ms = ms;
        }
    
        ret.count = ++this.count;
    
        // Store the old timestamp
        this.old_ts = this.ts;
        return ret;
    }
    
    reset() {
        this.count = 0;
        this.ts = 0;
        this.old_ts = 0;
        this.first_ts = 0;
    }
}
  