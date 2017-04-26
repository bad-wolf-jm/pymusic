class CallbackDispatcher(object):
    def __init__(self, **kw):
        super(CallbackDispatcher, self).__init__()
        self._callbacks = {}

    def register_callback(self, event_name, cb = None):
        if event_name not in self._callbacks:
            self._callbacks[event_name] = []
        if cb is not None:
            self._callbacks[event_name].append(cb)

    def dispatch(self, event_name, *args, **kwargs):
        #if event_name in self._callbacks:
        for cb in self._callbacks.get(event_name, []):
            value = cb(*args, **kwargs)
            if value:
                break
