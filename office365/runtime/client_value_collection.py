import uuid

from office365.runtime.client_value import ClientValue
from office365.runtime.odata.odata_type import ODataType
from office365.runtime.odata.v3.json_light_format import JsonLightFormat


class ClientValueCollection(ClientValue):

    def __init__(self, item_type, initial_values=None):
        """
        :type item_type: type[ClientValue or int or str or bool or uuid]
        :type initial_values: list or dict or None
        """
        super(ClientValueCollection, self).__init__()
        if initial_values is None:
            initial_values = []
        self._data = initial_values
        self._item_type = item_type

    def add(self, value):
        self._data.append(value)

    def __getitem__(self, index):
        """

        :type index: int
        :rtype: ClientValue
        """
        return self._data[index]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return repr(self._data)

    def to_json(self, json_format=None):
        """
        Serializes a client value's collection

        :type json_format: office365.runtime.odata.odata_json_format.ODataJsonFormat or None
        """
        json = [v for v in self]
        for i, v in enumerate(json):
            if isinstance(v, ClientValue):
                json[i] = v.to_json(json_format)
            elif isinstance(v, uuid.UUID):
                json[i] = str(v)
        if isinstance(json_format, JsonLightFormat) and json_format.include_control_information():
            json = {json_format.collection_tag_name: json,
                    json_format.metadata_type_tag_name: {'type': self.entity_type_name}}
        return json

    def _create_value(self, initial_value=None):
        """
        :type initial_value: int or bool or str or ClientValue or dict or None
        """
        if initial_value is None:
            return uuid.uuid4() if self._item_type == uuid.UUID else self._item_type()

        if self._item_type == uuid.UUID:
            return uuid.UUID(initial_value)
        elif issubclass(self._item_type, ClientValue):
            value = self._item_type()
            [value.set_property(k, v, False) for k, v in initial_value.items()]
            return value
        else:
            return initial_value

    def set_property(self, index, value, persist_changes=False):
        item_value = self._create_value(value)
        self.add(item_value)
        return self

    @property
    def item_type_name(self):
        return ODataType.resolve_type(self._create_value())

    @property
    def entity_type_name(self):
        """
        Returns server type name of value's collection
        """
        return ODataType.resolve_type(self)
