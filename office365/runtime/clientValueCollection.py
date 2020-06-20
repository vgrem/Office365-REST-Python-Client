from office365.runtime.clientValue import ClientValue


class ClientValueCollection(ClientValue):

    def __init__(self):
        super().__init__()
        self._data = []

    def add(self, value):
        self._data.append(value)

    def __iter__(self):
        for item in self._data:
            yield item
