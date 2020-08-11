from office365.runtime.client_object import ClientObject
from office365.runtime.client_value import ClientValue


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

    def set_property(self, key, value, persist_changes=False):
        if isinstance(self._value, ClientValue) or isinstance(self._value, ClientObject):
            self._value.set_property(key, value, persist_changes)
        else:
            self._value = value
