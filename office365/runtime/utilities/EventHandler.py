class EventHandler:
    def __init__(self):
        self._listeners = []

    def __iadd__(self, listener):
        self._listeners.append(listener)
        return self

    def __isub__(self, listener):
        self._listeners.remove(listener)
        return self

    def notify(self, *args, **kwargs):
        for listener in self._listeners:
            listener(*args, **kwargs)
