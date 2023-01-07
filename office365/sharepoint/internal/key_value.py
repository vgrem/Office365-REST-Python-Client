from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


class KeyValue(ClientValue):
    """Represents a key value pair."""

    def __init__(self, key=None, value=None, value_type=None):
        """
        :param str key: The value of the key in the key value pair.
        :param str value: The string representation of the value in the key value pair.
        :param str value_type: The EDM type name of the value in the key value pair.
        """
        self.Key = key
        self.Value = value
        self.ValueType = value_type

    @property
    def entity_type_name(self):
        return "SP.KeyValue"


class KeyValueCollection(ClientValueCollection):

    def __init__(self, initial_values=None):
        """
        :type initial_values: list[KeyValue] or None
        """
        super(KeyValueCollection, self).__init__(KeyValue, initial_values)
