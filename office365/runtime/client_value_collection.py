from office365.runtime.client_value import ClientValue


class ClientValueCollection(ClientValue):

    def __init__(self, item_type, initial_values=None):
        super().__init__()
        if initial_values is None:
            initial_values = []
        self._data = initial_values
        self._item_type = item_type

    def add(self, value):
        self._data.append(value)

    def __iter__(self):
        for item in self._data:
            yield item

    def __len__(self):
        return len(self._data)

    def to_json(self):
        return self._data

    def set_property(self, index, value, persist_changes=False):
        child_value = self._item_type()
        if isinstance(child_value, ClientValue):
            for k, v in value.items():
                child_value.set_property(k, v, False)
        else:
            child_value = value
        self.add(child_value)

    @property
    def entity_type_name(self):
        """
        Gets server type name
        """
        primitive_types = {
            bool: "Edm.Boolean",
            int: "Edm.Int32",
            str: "Edm.String",
        }

        item_type_name = None

        is_primitive = primitive_types.get(self._item_type, None) is not None
        if is_primitive:
            item_type_name = primitive_types[self._item_type]
        elif issubclass(self._item_type, ClientValue):
            item_type_name = self._item_type._entity_type_name
        if item_type_name is not None:
            return "Collection({0})".format(item_type_name)
        else:
            return None
