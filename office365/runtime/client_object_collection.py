from office365.runtime.resource_path import ResourcePath
from office365.runtime.client_object import ClientObject
from office365.runtime.client_runtime_context import ClientRuntimeContext
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.utilities.EventHandler import EventHandler


class ClientObjectCollection(ClientObject):

    def __init__(self, context, item_type, resource_path=None):
        """Client object collection

        :type context: ClientRuntimeContext
        :type item_type: type[ClientObject]
        :type resource_path: ResourcePath
        """
        super(ClientObjectCollection, self).__init__(context, resource_path)
        self._data = []
        self._item_type = item_type
        self.page_loaded = EventHandler(False)
        self._page_size = 100
        self._page_index = 0
        self.next_request_url = None

    @property
    def page_size(self):
        return self._page_size

    @page_size.setter
    def page_size(self, value):
        self._page_size = value
        self.top(value)

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
        """
        Adds client object into collection

        :type client_object: ClientObject
        """
        client_object._parent_collection = self
        self._data.append(client_object)

    def remove_child(self, client_object):
        self._data.remove(client_object)

    def __iter__(self):
        for cur_item in self._data:
            yield cur_item

        while self.next_request_url:
            self._page_index += 1
            next_index = self._page_size * self._page_index
            self._load_next_items()
            self.page_loaded.notify(len(self._data))
            next_items = self._data[next_index:]
            for cur_item in next_items:
                yield cur_item

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
        """

        :type expression: str
        """
        self.query_options.filter = expression
        return self

    def order_by(self, value):
        self.query_options.orderBy = value
        return self

    def skip(self, value):
        self.query_options.skip = value
        return self

    def top(self, value):
        self.query_options.top = value
        return self

    def _load_next_items(self):
        request = RequestOptions(self.next_request_url)
        response = self.context.execute_request_direct(request)
        json = response.json()
        self.next_request_url = None
        self.context.get_pending_request().map_json(json, self)
