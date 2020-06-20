from office365.runtime.clientValue import ClientValue


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

    @property
    def entity_type_name(self):
        edm_primitive_types = {
            int: "Edm.Int32",
            str: "Edm.String",
        }
        item_type_name = edm_primitive_types.get(self._item_type, "Edm.Int32")
        return "Collection({0})".format(item_type_name)
