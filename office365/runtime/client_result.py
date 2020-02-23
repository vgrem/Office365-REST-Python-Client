from office365.runtime.client_object import ClientObject
from office365.runtime.client_value_object import ClientValueObject


class ClientResult(object):
    """Client result"""

    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def map_json(self, json):
        if isinstance(self._value, ClientValueObject) or isinstance(self._value, ClientObject):
            self._value.map_json(json)
        else:
            self._value = json
