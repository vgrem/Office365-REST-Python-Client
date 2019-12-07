from office365.runtime.client_object import ClientObject
from office365.runtime.utilities.request_options import RequestOptions


class ClientObjectCollection(ClientObject):
    """Client object collection"""

    def __init__(self, context, item_type, resource_path=None):
        super(ClientObjectCollection, self).__init__(context, resource_path)
        self.__data = []
        self.__next_query_url = None
        self.item_type = item_type

    def create_typed_object(self, properties, client_object_type):
        if client_object_type is None:
            raise AttributeError("No class for object type '{0}' found".format(client_object_type))

        client_object = client_object_type(self.context)
        client_object._parent_collection = self
        client_object.map_json(properties)
        return client_object

    def map_json(self, payload):
        self.__data = []
        for properties in payload["collection"]:
            child_client_object = self.create_typed_object(properties, self.item_type)
            self.add_child(child_client_object)
        self.__next_query_url = payload["next"]

    def add_child(self, client_object):
        client_object._parent_collection = self
        self.__data.append(client_object)

    def __iter__(self):
        for _object in self.__data:
            yield _object
        while self.__next_query_url:
            # create a request with the __next_query_url
            request = RequestOptions(self.__next_query_url)
            request.set_headers(self.context.json_format.build_http_headers())
            response = self.context.execute_request_direct(request)

            # process the response
            payload = self.context.pending_request.process_response_json(response)
            self.__next_query_url = payload["next"]
            child_client_objects = []
            # add the new objects to the collection before yielding the results
            for properties in payload["collection"]:
                child_client_object = self.create_typed_object(properties, self.item_type)
                self.add_child(child_client_object)
                child_client_objects.append(child_client_object)

            for child_client_object in child_client_objects:
                yield child_client_object

    def __len__(self):
        if self.__next_query_url:
            # resolve all items first
            list(iter(self))

        return len(self.__data)

    def __getitem__(self, index):
        # fetch only as much items as necessary
        item_iterator = iter(self)
        while len(self.__data) <= index and self.__next_query_url:
            next(item_iterator)

        return self.__data[index]

    def filter(self, value):
        self.query_options['filter'] = value
        return self

    def order_by(self, value):
        self.query_options['orderby'] = value
        return self

    def skip(self, value):
        self.query_options['skip'] = value
        return self

    def top(self, value):
        self.query_options['top'] = value
        return self
