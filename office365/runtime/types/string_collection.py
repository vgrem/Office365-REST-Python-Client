from office365.runtime.client_value_collection import ClientValueCollection


class StringCollection(ClientValueCollection):

    def __init__(self, initial_values=None):
        super(StringCollection, self).__init__(str, initial_values)

    @property
    def entity_type_name(self):
        return "Collection(Edm.String)"
