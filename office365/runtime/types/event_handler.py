class EventHandler:
    def __init__(self, once=False):
        self._listeners = []
        self._once = once

    def __contains__(self, e):
        return e in self._listeners

    def __iter__(self):
        return iter(self._listeners)

    def __iadd__(self, listener):
        self._listeners.append(listener)
        return self

    def __isub__(self, listener):
        self._listeners.remove(listener)
        return self

    def __len__(self):
        return len(self._listeners)

    def notify(self, *args, **kwargs):
        for listener in self._listeners:
            if self._once:
                self._listeners.remove(listener)
            listener(*args, **kwargs)
