from office365.runtime.client_object import ClientObject
from office365.runtime.http.request_options import RequestOptions


class ClientObjectCollection(ClientObject):
    """Client object collection"""

    def __init__(self, context, item_type, resource_path=None):
        super(ClientObjectCollection, self).__init__(context, resource_path)
        self._data = []
        self.next_request_url = None
        self._item_type = item_type

    def clear(self):
        self._data = []

    def create_typed_object(self, properties):
        if self._item_type is None:
            raise AttributeError("No class for object type '{0}' found".format(self._item_type))

        client_object = self._item_type(self.context)
        client_object._parent_collection = self
        for k, v in properties.items():
            client_object.set_property(k, v, False)
        return client_object

    def set_property(self, name, value, persist_changes=False):
        child_client_object = self.create_typed_object(value)
        self.add_child(child_client_object)

    def add_child(self, client_object):
        client_object._parent_collection = self
        self._data.append(client_object)

    def remove_child(self, client_object):
        self._data.remove(client_object)

    def __iter__(self):
        for _item in self._data:
            yield _item
        for item in self._get_next_items():
            self.add_child(item)
            yield item

    def __len__(self):
        list(iter(self))
        return len(self._data)

    def __getitem__(self, index):
        # fetch only as much items as necessary
        item_iterator = iter(self)
        while len(self._data) <= index:
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

    def _get_next_items(self):
        if self.next_request_url:
            items = ClientObjectCollection(self.context, self._item_type, self.resourcePath)
            request = RequestOptions(self.next_request_url)
            response = self.context.execute_request_direct(request)
            json = response.json()
            self.context.get_pending_request().map_json(json, items)
            self.next_request_url = None
            for item in items:
                yield item
