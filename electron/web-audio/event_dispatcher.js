class EventDispatcher {
    constructor() {
        this.handlers = null;
    }

    on(event, fn) {
        if (!this.handlers) {
            this.handlers = {};
        }

        let handlers = this.handlers[event];
        if (!handlers) {
            handlers = this.handlers[event] = [];
        }
        handlers.push(fn);
        return {name: event, callback: fn, un: (e, fn) => this.un(e, fn)};
    }

    un(event, fn) {
        if (!this.handlers) {
            return;
        }

        const handlers = this.handlers[event];
        let i;
        if (handlers) {
            if (fn) {
                for (i = handlers.length - 1; i >= 0; i--) {
                    if (handlers[i] == fn) {
                        handlers.splice(i, 1);
                    }
                }
            } else {
                handlers.length = 0;
            }
        }
    }

    unAll() {
        this.handlers = null;
    }

    once(event, handler) {
        const fn = (...args) => {
            handler.apply(this, args);
            setTimeout(() => {
                this.un(event, fn);
            }, 0);
        };
        return this.on(event, fn);
    }

    dispatch(event, ...args) {
        if (!this.handlers) {
            return;
        }
        const handlers = this.handlers[event];
        //console.log(event, args)
        handlers && handlers.forEach(fn => {fn(...args)});
    }
}