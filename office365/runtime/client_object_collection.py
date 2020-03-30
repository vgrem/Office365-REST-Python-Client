from office365.runtime.client_object import ClientObject
from office365.runtime.http.request_options import RequestOptions


class ClientObjectCollection(ClientObject):
    """Client object collection"""

    def __init__(self, context, item_type, resource_path=None):
        super(ClientObjectCollection, self).__init__(context, resource_path)
        self._data = []
        self.__next_query_url = None
        self._item_type = item_type

    def create_typed_object(self, properties):
        if self._item_type is None:
            raise AttributeError("No class for object type '{0}' found".format(self._item_type))

        client_object = self._item_type(self.context)
        client_object._parent_collection = self
        client_object.map_json(properties)
        return client_object

    def map_json(self, json, next_query_url=None):
        self._data = []
        for properties in json:
            child_client_object = self.create_typed_object(properties)
            self.add_child(child_client_object)
        self.__next_query_url = next_query_url

    def add_child(self, client_object):
        client_object._parent_collection = self
        self._data.append(client_object)

    def remove_child(self, client_object):
        self._data.remove(client_object)

    def __iter__(self):
        for _object in self._data:
            yield _object
        while self.__next_query_url:
            # create a request with the __next_query_url
            request = RequestOptions(self.__next_query_url)
            response = self.context.execute_request_direct(request)
            payload = response.json()
            next_collection = ClientObjectCollection(self.context, self._item_type)
            next_collection.map_json(payload["collection"], payload["next"])

            # add the new objects to the collection before yielding the results
            for item in next_collection:
                self.add_child(item)
                yield item

    def __len__(self):
        if self.__next_query_url:
            # resolve all items first
            list(iter(self))
        return len(self._data)

    def __getitem__(self, index):
        # fetch only as much items as necessary
        item_iterator = iter(self)
        while len(self._data) <= index and self.__next_query_url:
            next(item_iterator)

        return self._data[index]

    def filter(self, expression):
        self.queryOptions.filter = expression
        return self

    def order_by(self, value):
        self.queryOptions.orderBy = value
        return self

    def skip(self, value):
        self.queryOptions.skip = value
        return self

    def top(self, value):
        self.queryOptions.top = value
        return self
