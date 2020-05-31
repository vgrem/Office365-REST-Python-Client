class EventHandler:
    def __init__(self, once=False):
        self._listeners = []
        self._once = once

    def __iadd__(self, listener):
        self._listeners.append(listener)
        return self

    def __isub__(self, listener):
        self._listeners.remove(listener)
        return self

    def notify(self, *args, **kwargs):
        for listener in self._listeners:
            if self._once:
                self._listeners.remove(listener)
            listener(*args, **kwargs)
