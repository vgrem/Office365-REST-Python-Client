from office365.runtime.client_object import ClientObject


class ClientObjectCollection(ClientObject):
    """Client object collection"""

    def __init__(self, context, resource_path=None):
        super(ClientObjectCollection, self).__init__(context, resource_path)
        self.__data = []

    def from_json(self, payload):
        for properties in payload:
            child_client_object = self.create_typed_object(properties)
            self.add_child(child_client_object)

    def add_child(self, client_object):
        client_object._parent_collection = self
        self.__data.append(client_object)

    def __iter__(self):
        return iter(self.__data)

    def __len__(self):
        return len(self.__data)

    def __getitem__(self, index):
        return self.__data[index]

    def expand(self, value):
        self.query_options['expand'] = value
        return self

    def filter(self, value):
        self.query_options['filter'] = value
        return self

    def order_by(self, value):
        self.query_options['orderby'] = value
        return self

    def select(self, value):
        self.query_options['select'] = value
        return self

    def skip(self, value):
        self.query_options['skip'] = value
        return self

    def top(self, value):
        self.query_options['top'] = value
        return self
