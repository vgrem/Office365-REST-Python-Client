from office365.runtime.client_object import ClientObject
from office365.runtime.client_value_object import ClientValueObject


class ClientResult(object):
    """Client result"""

    def __init__(self, value):
        self.value = value

    def map_json(self, value):
        if isinstance(self.value, ClientValueObject) or isinstance(self.value, ClientObject):
            self.value.map_json(value)
        else:
            self.value = value
