from typing import TypeVar, Iterator

from office365.runtime.client_object import ClientObject
from office365.runtime.types.event_handler import EventHandler

T = TypeVar('T', bound='ClientObjectCollection')
P_T = TypeVar("P_T", bound=ClientObject)


class ClientObjectCollection(ClientObject):

    def __init__(self, context, item_type, resource_path=None, parent=None):
        """A collection container which represents a named collections of objects

        :type context: office365.runtime.client_runtime_context.ClientRuntimeContext
        :type item_type: type[ClientObject]
        :type resource_path: office365.runtime.paths.resource_path.ResourcePath
        :type parent: ClientObject or None
        """
        super(ClientObjectCollection, self).__init__(context, resource_path)
        self._data = []  # type: list[ClientObject]
        self._item_type = item_type
        self._page_loaded = EventHandler(False)
        self._paged_mode = False
        self._current_pos = None
        self._next_request_url = None
        self._parent = parent

    def clear(self):
        """Clears client object collection"""
        if not self._paged_mode:
            self._data = []
        self._next_request_url = None
        self._current_pos = len(self._data)
        return self

    def create_typed_object(self, initial_properties=None, resource_path=None):
        """
        :type self: T
        :type initial_properties: dict or None
        :type resource_path: office365.runtime.paths.resource_path.ResourcePath or None
        """
        if self._item_type is None:
            raise AttributeError("No class model for entity type '{0}' was found".format(self._item_type))
        client_object = self._item_type(context=self.context, resource_path=resource_path)   # type: ClientObject
        if initial_properties is not None:
            [client_object.set_property(k, v) for k, v in initial_properties.items() if v is not None]
        return client_object

    def set_property(self, key, value, persist_changes=False):
        """
        :type key: int or str
        :type value: dict
        :type persist_changes: bool
        """
        if key == "__nextLinkUrl":
            self._next_request_url = value
        else:
            client_object = self.create_typed_object()
            self.add_child(client_object)
            [client_object.set_property(k, v, persist_changes) for k, v in value.items()]
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
        :type self: T
        :rtype: Iterator[ClientObject]
        """
        for item in self._data:
            yield item
        if self._paged_mode:
            while self.has_next:
                self._get_next().execute_query()
                next_items = self._data[self._current_pos:]
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
        :type value: str
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

        def _page_loaded(items):
            self._page_loaded.notify(self)
            if self.has_next:
                self._get_next(after_loaded=_page_loaded)

        self.context.load(self, after_loaded=_page_loaded)
        return self

    def _get_next(self, after_loaded=None):
        """
        Submit a request to retrieve next collection of items

        :param (ClientObjectCollection) -> None after_loaded: Page loaded event
        """

        def _construct_next_query(request):
            """
            :type request: office365.runtime.http.request_options.RequestOptions
            """
            request.url = self._next_request_url

        self.context.load(self, before_loaded=_construct_next_query, after_loaded=after_loaded)
        return self

    def first(self, expression):
        """Return the first Entity instance that matches current query

        :param str expression: Filter expression
        """
        return_type = self.create_typed_object()
        self.add_child(return_type)
        key = return_type.property_ref_name

        def _after_loaded(col):
            """
            :type col: ClientObjectCollection
            """
            if len(col) < 1:
                message = "Not found for filter: {0}".format(self.query_options.filter)
                raise ValueError(message)
            return_type.set_property(key, col[0].get_property(key))

        self.filter(expression).top(1)
        self.context.load(self, [key], after_loaded=_after_loaded)
        return return_type

    def single(self, expression):
        """
        Return only one resulting Entity

        :param str expression: Filter expression
        """
        return_type = self.create_typed_object()
        self.add_child(return_type)
        key = return_type.property_ref_name

        def _after_loaded(col):
            """
            :type col: ClientObjectCollection
            """
            if len(col) == 0:
                message = "Not found for filter: {0}".format(expression)
                raise ValueError(message)
            elif len(col) > 1:
                message = "Ambiguous match found for filter: {0}".format(expression)
                raise ValueError(message)
            return_type.set_property(key, col[0].get_property(key), False)

        self.filter(expression).top(2)
        self.context.load(self, after_loaded=_after_loaded)
        return return_type

    @property
    def parent(self):
        return self._parent

    @property
    def has_next(self):
        """"""
        return self._next_request_url is not None

    @property
    def entity_type_name(self):
        """Returns server type name for the collection of entities"""
        if self._entity_type_name is None:
            client_object = self.create_typed_object()
            self._entity_type_name = "Collection({0})".format(client_object.entity_type_name)
        return self._entity_type_name
