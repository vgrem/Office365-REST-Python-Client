from typing import TypeVar

from office365.runtime.client_object import ClientObject
from office365.runtime.types.event_handler import EventHandler

T = TypeVar('T', bound='ClientObjectCollection')


class ClientObjectCollection(ClientObject):

    def __init__(self, context, item_type, resource_path=None):
        """A collection container which represents a named collections of objects

        :type context: office365.runtime.client_runtime_context.ClientRuntimeContext
        :type item_type: type[ClientObject]
        :type resource_path: office365.runtime.paths.resource_path.ResourcePath
        """
        super(ClientObjectCollection, self).__init__(context, resource_path)
        self._data = []  # type: list[ClientObject]
        self._item_type = item_type
        self._page_loaded = EventHandler(False)
        self._paged_mode = False
        self._page_index = 0
        self.next_request_url = None
        self._clear_results = True

    def clear(self):
        if self._clear_results:
            self._data = []
        self.next_request_url = None
        return self

    def create_typed_object(self, properties=None, persist_changes=False):
        """
        :type properties: dict
        :type persist_changes: bool
        :rtype: ClientObject
        """
        if properties is None:
            properties = {}
        if self._item_type is None:
            raise AttributeError("No class for entity type '{0}' found".format(self._item_type))

        client_object = self._item_type(self.context)
        client_object._parent_collection = self
        for k, v in properties.items():
            client_object.set_property(k, v, persist_changes)
        return client_object

    def set_property(self, index, value, persist_changes=False):
        """
        :type index: int
        :type value: dict
        :type persist_changes: bool
        """
        client_object = self.create_typed_object(value)
        self.add_child(client_object)
        return self

    def add_child(self, client_object):
        """
        Adds client object into collection

        :type client_object: ClientObject
        """
        client_object._parent_collection = self
        self._data.append(client_object)
        return self

    def remove_child(self, client_object):
        """
        :type client_object: ClientObject
        """
        self._data = [item for item in self._data if item != client_object]
        return self

    def __iter__(self):
        """
        :rtype: collections.Iterable[ClientObject]
        """
        for item in self._data:
            yield item
        if self._paged_mode:
            while self.has_next:
                next_items = self._load_next().execute_query()
                for next_item in next_items:
                    yield next_item

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return repr(self._data)

    def __getitem__(self, index):
        """
        :type index: int
        """
        return self._data[index]

    def to_json(self, json_format=None):
        """Serializes the collection into JSON"""
        return [item.to_json(json_format) for item in self._data]

    def filter(self, expression):
        """
        Allows clients to filter a collection of resources that are addressed by a request URL

        :type self: T
        :param str expression: Filter expression, for example: 'Id eq 123'
        """
        self.query_options.filter = expression
        return self

    def order_by(self, value):
        """
        Allows clients to request resources in either ascending order using asc or descending order using desc

        :type self: T
        :type value: int
        """
        self.query_options.orderBy = value
        return self

    def skip(self, value):
        """
        Requests the number of items in the queried collection that are to be skipped and not included in the result

        :type self: T
        :type value: int
        """
        self.query_options.skip = value
        return self

    def top(self, value):
        """
        Specifies the number of items in the queried collection to be included in the result

        :type self: T
        :type value: int
        """
        self.query_options.top = value
        return self

    def paged(self, page_size=None, page_loaded=None):
        """
        Retrieves via server-driven paging mode

        :type self: T
        :param int page_size: Page size
        :param (ClientObjectCollection) -> None page_loaded: Page loaded event
        """
        self._paged_mode = True
        if callable(page_loaded):
            self._page_loaded += page_loaded
        if page_size:
            self.top(page_size)
        return self

    def get(self):
        """
        :type self: T
        """
        def _loaded(items):
            self._page_loaded.notify(self)
        self.context.load(self, after_loaded=_loaded)
        return self

    def get_all(self, page_size=None, page_loaded=None):
        """
        Gets all the items in a collection, regardless of the size.

        :type self: T
        :param int page_size: Page size
        :param (T) -> None page_loaded: Page loaded event
        """
        self.paged(page_size, page_loaded)
        self._clear_results = False

        def _page_loaded(items):
            self._page_loaded.notify(self)
            if self.has_next:
                self._load_next(after_loaded=_page_loaded)

        self.context.load(self, after_loaded=_page_loaded)
        return self

    def _load_next(self, after_loaded=None):
        """
        Submit a request to retrieve next collection of items

        :param (ClientObjectCollection) -> None after_loaded: Page loaded event
        """
        def _construct_next_query(request):
            """
            :type request: office365.runtime.http.request_options.RequestOptions
            """
            self._page_index += 1
            request.url = self.next_request_url

        self.context.load(self, before_loaded=_construct_next_query, after_loaded=after_loaded)
        return self

    @property
    def page_index(self):
        return self._page_index

    @property
    def has_next(self):
        return self.next_request_url is not None

    @property
    def entity_type_name(self):
        """Returns server type name for the collection of entities"""
        name = super(ClientObjectCollection, self).entity_type_name
        return "Collection({0})".format(name)
