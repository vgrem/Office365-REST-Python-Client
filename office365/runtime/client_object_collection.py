from office365.runtime.client_object import ClientObject
from office365.runtime.http.request_options import RequestOptions


class ClientObjectCollection(ClientObject):
    """Client object collection"""

    def __init__(self, context, item_type, resource_path=None):
        super(ClientObjectCollection, self).__init__(context, resource_path)
        self._data = []
        self.__next_query_url = None
        self._item_type = item_type

    def create_typed_object(self, properties, client_object_type):
        if client_object_type is None:
            raise AttributeError("No class for object type '{0}' found".format(client_object_type))

        client_object = client_object_type(self.context)
        client_object._parent_collection = self
        client_object.map_json(properties)
        return client_object

    def map_json(self, json):
        self._data = []
        for properties in json["collection"]:
            child_client_object = self.create_typed_object(properties, self._item_type)
            self.add_child(child_client_object)
        self.__next_query_url = json["next"]

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
            request.set_headers(self.context.json_format.build_http_headers())
            response = self.context.execute_request_direct(request)

            # process the response
            payload = self.context.pending_request.process_response(response)
            self.__next_query_url = payload["next"]
            child_client_objects = []
            # add the new objects to the collection before yielding the results
            for properties in payload["collection"]:
                child_client_object = self.create_typed_object(properties, self._item_type)
                self.add_child(child_client_object)
                child_client_objects.append(child_client_object)

            for child_client_object in child_client_objects:
                yield child_client_object

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

    def filter(self, value):
        self.queryOptions['filter'] = value
        return self

    def order_by(self, value):
        self.queryOptions['orderby'] = value
        return self

    def skip(self, value):
        self.queryOptions['skip'] = value
        return self

    def top(self, value):
        self.queryOptions['top'] = value
        return self
