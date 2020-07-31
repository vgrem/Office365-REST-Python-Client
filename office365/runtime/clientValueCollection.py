from office365.runtime.client_value import ClientValue


class ClientValueCollection(ClientValue):

    def __init__(self, item_type):
        super().__init__()
        self._data = []
        self._item_type = item_type

    def add(self, value):
        self._data.append(value)

    def __iter__(self):
        for item in self._data:
            yield item

    def to_json(self):
        return self._data

    def set_property(self, index, value, persist_changes=False):
        child_value = self._item_type
        if isinstance(child_value, ClientValue):
            for k, v in value.items():
                child_value.set_property(k, v, False)
        else:
            child_value = value
        self.add(child_value)

    @property
    def entity_type_name(self):
        primitive_types = {
            "bool": "Edm.Boolean",
            "int": "Edm.Int32",
            "str": "Edm.String",
        }
        item_type_name = type(self._item_type).__name__
        is_primitive = primitive_types.get(item_type_name, None) is not None
        if is_primitive:
            item_type_name = primitive_types[item_type_name]
        elif isinstance(self._item_type, ClientValue):
            item_type_name = self._item_type.entity_type_name
        return "Collection({0})".format(item_type_name)
