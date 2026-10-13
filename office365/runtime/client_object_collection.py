from __future__ import annotations

import warnings
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncIterator,
    Callable,
    Dict,
    Generic,
    Iterator,
    List,
    Optional,
    Type,
    cast,
)

from typing_extensions import Self

from office365.runtime.client_object import ClientObject, ClientObjectT
from office365.runtime.client_runtime_context import ClientRuntimeContext
from office365.runtime.http.prefer import add_prefer
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.odata.json_format import ODataJsonFormat
from office365.runtime.operations import Progress
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.query_capabilities import (
    QueryCapability,
    QueryOptionNotSupportedError,
    QueryPropertyNotSupportedError,
    hint,
    property_hint,
    query_capabilities_of,
)
from office365.runtime.types.event_handler import EventHandler
from office365.runtime.types.exceptions import NotFoundException

if TYPE_CHECKING:
    from office365.runtime.operations import ProgressCallback


class ClientObjectCollection(ClientObject, Generic[ClientObjectT]):
    """
    A strongly-typed collection container for SharePoint client objects.

    This collection supports:
    - Server-driven paging for large result sets
    - LINQ-style query operations (filter, order, skip, top)
    - Type-safe object creation and manipulation
    - Event-based loading notifications

    Subclasses backed by a SharePoint list view (list items, files, folders) set
    ``_list_view_threshold`` so a single-shot load that reaches the threshold warns
    instead of silently returning a truncated page.
    """

    _list_view_threshold: int | None = None
    _truncation_hint: str = "page it with get_all(page_size=2000)"
    #: OData query options this collection's endpoint rejects (or the exact set
    #: it allows). Declared with
    #: :func:`~office365.runtime.query_capabilities.query_capabilities`.
    _query_capability_decl: Optional[QueryCapability] = None

    def __init__(
        self,
        context: ClientRuntimeContext,
        item_type: Type[ClientObjectT],
        resource_path: Optional[ResourcePath] = None,
        parent: Optional[ClientObject] = None,
    ) -> None:
        """
        Initialize a new collection of client objects.

        Args:
            context: Client context for API operations
            item_type: The class type of items in this collection
            resource_path: Relative API path for this collection
            parent: Parent object that owns this collection
        """
        super().__init__(context, resource_path)
        self._data: list[ClientObjectT] = []
        self._item_type: Type[ClientObjectT] = item_type
        self._page_loaded: EventHandler = EventHandler(False)
        self._paged_mode: bool = False
        self._page_size: int | None = None
        self._current_pos: int | None = None
        self._next_request_url: str | None = None
        self._page_headers: dict[str, str] | None = None
        self._server_paged: bool = False
        self._next_page: Callable[[], Any] | None = None
        self._truncation_warned: bool = False
        self._parent = parent

    def clear_state(self) -> Self:
        """
        Reset the collection's internal state while maintaining configuration.

        Note:
            In paged mode, only clears the next page pointer and the
            server-paging flag, preserving loaded items.

        Returns:
            self: Supports fluent method chaining
        """
        if not self._paged_mode:
            self._data = []
            self._server_paged = False
        elif self._next_request_url is None:
            # A fresh request (not a ``$skiptoken`` continuation): a previous
            # server-paged run must not keep the client-driven ``$skip`` offset
            # fallback disabled for the new enumeration.
            self._server_paged = False
        self._next_request_url = None
        self._page_headers = None
        self._current_pos = len(self._data)
        return self

    def create_typed_object(
        self,
        initial_properties: Optional[Dict] = None,
        resource_path: Optional[ResourcePath] = None,
    ) -> ClientObjectT:
        """
        Factory method to create a new item of the collection's type.

        Args:
            initial_properties: Property values to initialize the object with
            resource_path: Custom API path for the new object

        Returns:
            ClientObjectT: New instance of the collection's item type

        Raises:
            AttributeError: If no item type was specified for the collection
        """
        if self._item_type is None:
            raise AttributeError("Cannot create object - no type specified for collection")
        if resource_path is None:
            resource_path = ResourcePath(None, self.resource_path)
        client_object = self._item_type(context=self.context, resource_path=resource_path)
        if initial_properties is not None:
            [client_object.set_property(k, v) for k, v in initial_properties.items() if v is not None]
        return client_object

    def set_property(self, name: str, value: Dict[str, Any], persist_changes: bool = False) -> Self:
        """
        Set a property on the collection or handle special properties.

        Special Cases:
            - "__nextLinkUrl": Stores pagination URL for server-driven paging

        Args:
            key: Property name or index
            value: Property value to set
            persist_changes: Whether to mark the change for server update

        Returns:
            self: Supports fluent method chaining
        """
        if name == "__nextLinkUrl":
            if isinstance(value, str):
                self._next_request_url = value
                self._server_paged = True
            else:
                raise ValueError(f"Invalid value for __nextLinkUrl: expected a string {value}")
        else:
            client_object = self.create_typed_object()
            self.add_child(client_object)
            [client_object.set_property(k, v, persist_changes) for k, v in value.items()]
        return self

    def add_child(self, client_object: ClientObjectT) -> Self:
        """
        Add an item to the collection and set its parent reference.

        Args:
            client_object: The item to add to the collection

        Returns:
            self: Supports fluent method chaining
        """
        client_object._parent_collection = self
        self._data.append(client_object)
        self._maybe_warn_truncated()
        return self

    def _maybe_warn_truncated(self) -> None:
        """Warn once when a single-shot load fills the SharePoint list view threshold.

        A non-paged collection that returns the threshold number of rows may have
        been silently trimmed by SharePoint, so point the caller at the paged API.
        """
        threshold = self._list_view_threshold
        if threshold is None or self._truncation_warned or self._paged_mode:
            return
        if len(self._data) >= threshold:
            self._truncation_warned = True
            warnings.warn(
                f"This collection returned {len(self._data):,} items in a single request and may be "
                f"truncated at the SharePoint list view threshold ({threshold:,}); {self._truncation_hint}.",
                UserWarning,
                stacklevel=3,
            )

    def remove_child(self, client_object: ClientObjectT) -> Self:
        """
        Remove an item from the collection.

        Args:
            client_object: The item to remove from the collection

        Returns:
            self: Supports fluent method chaining
        """
        self._data = [item for item in self._data if item != client_object]
        return self

    def clear(self) -> Self:
        """Discard the collection's items, keeping its configuration.

        Unlike :meth:`clear_state` this only drops the loaded/queued entities
        (``_data``) — used by streaming imports to keep memory bounded between
        chunks.

        Returns:
            self: Supports fluent method chaining
        """
        self._data = []
        return self

    def __iter__(self) -> Iterator[ClientObjectT]:
        """Iterate through all items, automatically handling paged results."""
        yield from self._data

        # Handle server-side paging: follow __next, yielding each new page only
        # (a local position, so it stays correct regardless of _current_pos).
        if self._paged_mode:
            position = len(self._data)
            while self.has_next:
                self._get_next().execute_query()
                yield from self._data[position:]
                position = len(self._data)

    def __aiter__(self) -> AsyncIterator[ClientObjectT]:
        """Iterate all items, fetching pages without blocking the loop.

        The async twin of :meth:`__iter__`: items already loaded are yielded
        first, then any remaining server pages are awaited and their new items
        yielded as they arrive. If nothing has been loaded yet the first page is
        fetched on demand, so ``async for item in collection`` works without an
        explicit :meth:`get_all_async`.
        """
        return self._iter_async()

    async def _iter_async(self) -> AsyncIterator[ClientObjectT]:
        # Paged mode keeps already-loaded items when a page response arrives
        # (``clear_state`` otherwise resets ``_data``), matching ``get_all``.
        self.paged(self._page_size)
        if not self._data and self._next_request_url is None:
            self.get()
            await self.context.execute_query_async()

        for item in self._data:
            yield item

        if self._paged_mode or self._next_request_url is not None:
            position = len(self._data)
            while self.has_next:
                self._get_next()
                await self.context.execute_query_async()
                for item in self._data[position:]:
                    yield item
                position = len(self._data)

    def __len__(self) -> int:
        """Get the current number of loaded items in the collection."""
        return len(self._data)

    def __repr__(self) -> str:
        """Return a bounded preview of the already-loaded items (never fetches)."""
        from office365.runtime.display import describe_collection

        return describe_collection(self._data, type(self).__name__, more=self.has_next)

    def __str__(self) -> str:
        """Return the same bounded preview as :meth:`__repr__`."""
        return self.__repr__()

    def _repr_html_(self) -> str:
        """Render the loaded items as an HTML table (Jupyter/rich display)."""
        from office365.runtime.display import collection_html

        return collection_html(self._data, type(self).__name__, more=self.has_next)

    def to_string(self, max_items: int | None = None) -> str:
        """Render the loaded items as a full, aligned table.

        Unlike :meth:`__repr__`/:meth:`__str__` (a bounded preview), this
        renders **every** loaded item so it can back a report. Pass
        ``max_items`` to cap the rows. Nothing is fetched: call
        :meth:`get_all` first if the collection is paged. Columns are not
        truncated, so a report never loses identifier digits.
        """
        from office365.runtime.display import describe_collection

        return describe_collection(
            self._data,
            type(self).__name__,
            max_items=max_items,
            max_column_width=None,
            more=self.has_next,
        )

    def __getitem__(self, index: int) -> ClientObjectT:
        """Get an item by its index position."""
        return self._data[index]

    def to_json(self, json_format: Optional[ODataJsonFormat] = None) -> list[dict[str, Any]]:
        """
        Serialize the collection to OData JSON format.

        This is **payload serialization** (for request bodies, includes type
        metadata when requested) — for data export use :meth:`to_records` /
        :meth:`to_csv` instead.

        Args:
            json_format: Serialization options

        Returns:
            JSON-serializable list of item dictionaries
        """
        return [cast(Dict[str, Any], item.to_json(json_format)) for item in self._data]

    def _ensure_query_option(self, option: str) -> bool:
        """Whether ``option`` may be applied to this collection's endpoint.

        Collections declare this with
        :func:`~office365.runtime.query_capabilities.query_capabilities` — e.g. the
        ``callRecords`` feed rejects ``$top``. Raises
        :class:`QueryOptionNotSupportedError` by default, or warns and returns
        ``False`` (so the option is ignored) when the declaration uses
        ``on_unsupported="warn"``.
        """
        capability = query_capabilities_of(type(self))
        if capability is None or capability.supports(option):
            return True
        if capability.on_unsupported == "warn":
            warnings.warn(hint(type(self), option, capability), UserWarning, stacklevel=3)
            return False
        raise QueryOptionNotSupportedError(type(self), option, capability)

    def _may_apply_query_option(self, option: str) -> bool:
        """Whether the endpoint accepts ``option``, without raising or warning.

        Used by :meth:`first` / :meth:`first_or_none` / :meth:`single` to bound
        their query with ``$top`` only where the feed accepts it. Endpoints such
        as ``directoryRoles`` reject custom page sizes, so when this returns
        ``False`` the caller bounds the result client-side from the filtered
        response instead of sending an unsupported option.
        """
        capability = query_capabilities_of(type(self))
        return capability is None or capability.supports(option)

    def _bounded(self, count: int) -> Self:
        """``self.get()`` with a ``$top`` bound, applied only if supported."""
        query = self.get()
        if self._may_apply_query_option("top"):
            query = query.top(count)
        return query

    def _ensure_query_properties(self, option: str, expression: str) -> None:
        """Validate the properties an expression references against the declaration.

        A property-level restriction (e.g. a drive's ``size``, which the service
        maps to the non-filterable ``SMTotalFileStreamSize``) is caught here,
        before a round trip. With ``on_unsupported="warn"`` the expression is
        kept as-is: silently dropping one side of a filter would change its
        meaning, so the warning is a caution rather than a rewrite.
        """
        capability = query_capabilities_of(type(self))
        if capability is None:
            return
        violations = (
            capability.filter_violations(expression) if option == "filter" else capability.orderby_violations(expression)
        )
        if not violations:
            return
        if capability.on_unsupported == "warn":
            warnings.warn(property_hint(type(self), option, violations[0], capability), UserWarning, stacklevel=3)
            return
        raise QueryPropertyNotSupportedError(type(self), option, violations[0], capability)

    def _apply_query_preferences(self, request: RequestOptions) -> None:
        """Attach the ``Prefer`` values the declared capability requires for this query."""
        capability = query_capabilities_of(type(self))
        if capability is None or not capability.prefer:
            return
        values = capability.preference_values(self.query_options.filter, self.query_options.order_by)
        if values:
            add_prefer(request, *values)

    def select(self, names: List[str]) -> Self:
        """Include specific properties in the query (``$select``)."""
        if self._ensure_query_option("select"):
            super().select(names)
        return self

    def expand(self, names: List[str]) -> Self:
        """Include related resources in the query (``$expand``)."""
        if self._ensure_query_option("expand"):
            super().expand(names)
        return self

    def filter(self, expression: str) -> Self:
        """
        Get the first item matching the filter criteria.

        Args:
            expression: OData filter expression

        Returns:
            T: The first matching item

        Raises:
            ValueError: If no matching items found
        """
        if self._ensure_query_option("filter"):
            self._ensure_query_properties("filter", expression)
            self.query_options.filter = expression
        return self

    def order_by(self, value: str) -> Self:
        """
        Add sorting to the query.

        Args:
            value: OData order expression (e.g. "CreatedDate desc")

        Returns:
            self: Supports fluent method chaining
        """
        if self._ensure_query_option("order_by"):
            self._ensure_query_properties("order_by", value)
            self.query_options.order_by = value
        return self

    def skip(self, value: int) -> Self:
        """
        Skip the specified number of items in the query results.

        Args:
            value: Number of items to skip

        Returns:
            self: Supports fluent method chaining
        """
        if self._ensure_query_option("skip"):
            self.query_options.skip = value
        return self

    def top(self, value: int) -> Self:
        """
        Limit the number of items returned by the query.

        Args:
            value: Maximum number of items to return

        Returns:
            self: Supports fluent method chaining
        """
        if self._ensure_query_option("top"):
            self.query_options.top = value
        return self

    def paged(self, page_size: int | None = None, page_loaded: Callable[[Self], None] | None = None) -> Self:
        """
        Enable server-driven paging mode.

        Args:
            page_size: Items per page (uses server default if None)
            page_loaded: Callback when each page loads

        Returns:
            self: Supports fluent method chaining
        """
        self._paged_mode = True
        self._page_size = page_size
        if callable(page_loaded):
            self._page_loaded += page_loaded
        if page_size:
            self.top(page_size)
        return self

    def get(self) -> Self:
        """
        Load the collection data from the server.

        Returns:
            self: Supports fluent method chaining
        """

        def _loaded(col: Any) -> None:
            self._page_loaded(self)

        def _capture_headers(resp: Any) -> None:
            # remember the headers of the first page so subsequent page
            # requests can re-apply them (e.g. ConsistencyLevel on Graph)
            request = getattr(resp, "request", None)
            if self._paged_mode and self._page_headers is None and request is not None:
                self._page_headers = dict(request.headers)

        self.context.load(self)
        capability = query_capabilities_of(type(self))
        if capability is not None and capability.prefer:
            self.context.before_execute(self._apply_query_preferences)
        self.context.after_execute(_capture_headers, include_response=True).after_execute(_loaded)
        return self

    def get_all(
        self,
        page_size: int | None = None,
        page_loaded: Callable[[Self], None] | None = None,
        progress: "ProgressCallback | None" = None,
        dedupe_by: str | None = None,
    ) -> Self:
        """
        Load all items in the collection, automatically handling paging.

        Args:
            page_size: Items per page (uses server default if None)
            page_loaded: Legacy callback invoked with the loaded collection after
              each page.
            progress: Optional hook invoked per page with a ``Progress`` snapshot
              (``done`` = items loaded so far; ``total`` unknown for server-driven
              paging, so the bar is indeterminate).
            dedupe_by: Optional property name (e.g. ``"id"``) used to drop an
              item that repeats one already seen on an earlier page. Some Graph
              export APIs repeat rows during service updates; ``None`` (the
              default) keeps every item. De-duplication runs once the last page
              has loaded, so it does not disturb ``$skip`` offsets.

        Returns:
            self: Supports fluent method chaining
        """

        def _page_loaded(col: ClientObjectCollection) -> None:
            if callable(progress):
                progress(Progress(done=len(self._data), stage="loading"))
            if self.has_next:
                self._get_next().after_execute(_page_loaded)
            elif dedupe_by:
                self._dedupe_loaded(dedupe_by)

        self.paged(page_size, page_loaded).get().after_execute(_page_loaded)
        return self

    async def get_all_async(
        self,
        page_size: int | None = None,
        page_loaded: Callable[[Self], None] | None = None,
        progress: "ProgressCallback | None" = None,
        dedupe_by: str | None = None,
    ) -> Self:
        """
        Async twin of :meth:`get_all`: load every page without blocking the loop.

        Pages are fetched sequentially (server-driven paging) and the event loop
        stays free while each request is in flight. ``page_loaded`` / ``progress``
        fire per page exactly as in the synchronous path.

        Args:
            page_size: Items per page (uses server default if None)
            page_loaded: Legacy callback invoked with the loaded collection after
              each page.
            progress: Optional hook invoked per page with a ``Progress`` snapshot
              (``done`` = items loaded so far; ``total`` unknown for server-driven
              paging, so the bar is indeterminate).
            dedupe_by: Optional property name (e.g. ``"id"``) used to drop an
              item that repeats one already seen on an earlier page. Some Graph
              export APIs repeat rows during service updates; ``None`` (the
              default) keeps every item. De-duplication runs once the last page
              has loaded, so it does not disturb ``$skip`` offsets.

        Returns:
            self: Supports fluent method chaining
        """
        self.paged(page_size, page_loaded)

        def _page_loaded(_col: ClientObjectCollection) -> None:
            if callable(progress):
                progress(Progress(done=len(self._data), stage="loading"))

        self.get().after_execute(_page_loaded)
        await self.context.execute_query_async()
        while self.has_next:
            self._get_next().after_execute(_page_loaded)
            await self.context.execute_query_async()
        if dedupe_by:
            self._dedupe_loaded(dedupe_by)
        return self

    def _dedupe_loaded(self, key: str) -> None:
        """Drop items whose ``key`` already appeared on a previous page.

        Preserves the first occurrence and the original order. Called only after
        enumeration completes so it never affects ``$skip`` offsets mid-run.
        """
        seen: set[Any] = set()
        unique: list[ClientObjectT] = []
        for item in self._data:
            value = self._dedupe_key(item, key)
            if value is not None:
                try:
                    hash(value)
                except TypeError:
                    # An unhashable value cannot be tracked; keep the item.
                    unique.append(item)
                    continue
                if value in seen:
                    continue
                seen.add(value)
            unique.append(item)
        self._data = unique
        self._current_pos = len(self._data)

    @staticmethod
    def _dedupe_key(item: ClientObjectT, key: str) -> Any:
        props = getattr(item, "properties", None)
        if isinstance(props, dict) and key in props:
            return props[key]
        try:
            return getattr(item, key, None)
        except Exception:  # a missing or still-loading property must not abort de-dup
            return None

    def _can_offset_next(self) -> bool:
        """Whether the next page can be fetched with a client-driven offset request.

        Some SharePoint endpoints (e.g. ``SP.Publishing.SitePageService/pages``)
        never emit a server-side ``__next`` link, even when more items exist.
        When the client requested an explicit page size and the last page came
        back full, fall back to ``$skip``/``$top`` paging. Graph is excluded:
        it always reports ``@odata.nextLink`` and does not honor ``$skip``.
        """
        if not self._paged_mode or not self._page_size or self._next_request_url is not None:
            return False
        if self._server_paged:
            # The server drives paging (``__next``/``$skiptoken``); a ``$skip``
            # fallback would conflict with the token on the final page.
            return False
        from office365.runtime.odata.v3.json_light_format import JsonLightFormat

        json_format = getattr(self.context.pending_request(), "json_format", None)
        if not isinstance(json_format, JsonLightFormat):
            return False
        return len(self.current_page) == self._page_size

    def _get_next(self) -> Self:
        """Submit a request to retrieve next collection of items"""

        if self._next_page is not None:
            # Custom loader (e.g. CAML paging via ListItemCollectionPosition).
            self._next_page()
            return self

        _PAGE_EXCLUDED_HEADERS = ("authorization", "content-length")

        def _construct_request(request: RequestOptions) -> None:
            request.url = self._next_request_url  # type: ignore[assignment]
            if self._page_headers:
                request.headers.update(
                    {k: v for k, v in self._page_headers.items() if k.lower() not in _PAGE_EXCLUDED_HEADERS}
                )

        if self._next_request_url is None:
            if not self._can_offset_next():
                raise ValueError("Next page not available")
            self.skip(len(self._data))
            return self.get()
        return self.get().before_execute(_construct_request)

    def first(self, expression: str) -> ClientObjectT:
        """Get the first item matching the filter criteria.

        Args:
            expression: OData filter expression

        Returns:
            The first matching item

        Raises:
            NotFoundException: If no matching items found
        """
        return_type = self.create_typed_object()
        self.add_child(return_type)

        def _after_loaded(col: ClientObjectCollection) -> None:
            if len(col) < 1:
                raise NotFoundException(return_type, expression)
            for k, v in col[0].properties.items():
                return_type.set_property(k, v, False)

        self._bounded(1).filter(expression).after_execute(_after_loaded)
        return return_type

    def first_or_none(self, expression: str | None = None) -> ClientObjectT:
        """Queue a read for the first item matching ``expression``.

        Deferred exactly like :meth:`first`: nothing is sent until the caller runs
        ``execute_query()``. When an item matches it is copied into the returned
        object; when nothing matches the object is left uninitialized instead of
        raising — detect that with :attr:`ClientObject.is_loaded`:

            item = col.first_or_none("displayName eq 'X'").execute_query()
            if item.is_loaded:
                ...

        Args:
            expression: Optional OData filter expression

        Returns:
            The first matching item, or an uninitialized object when there is none
        """
        return_type = self.create_typed_object()
        self.add_child(return_type)

        def _after_loaded(col: ClientObjectCollection) -> None:
            if len(col) > 0:
                for k, v in col[0].properties.items():
                    return_type.set_property(k, v, False)

        query = self._bounded(1)
        if expression:
            query = query.filter(expression)
        query.after_execute(_after_loaded)
        return return_type

    def single(self, expression: str) -> ClientObjectT:
        """Get exactly one item matching the filter criteria.

        Args:
            expression: OData filter expression

        Returns:
            The single matching item

        The query is bounded to ``$top=2`` when the endpoint accepts it: enough to
        detect an ambiguous match without downloading every matching item just to
        reject it. Feeds that reject ``$top`` fall back to bounding client-side.

        Raises:
            NotFoundException: If no items match
            ValueError: If multiple items match
        """
        return_type = self.create_typed_object()
        self.add_child(return_type)

        def _after_loaded(col: ClientObjectCollection) -> None:
            if len(col) == 0:
                raise NotFoundException(return_type, expression)
            if len(col) > 1:
                raise ValueError(f"Ambiguous match found for filter: {expression}")
            for k, v in col[0].properties.items():
                return_type.set_property(k, v, False)

        self._bounded(2).filter(expression).after_execute(_after_loaded)
        return return_type

    def _find_by_filter(self, expression: str, *, required: bool = False) -> ClientObjectT:
        """Shared implementation behind the typed ``find_by_*`` lookups.

        Tolerant by default: a miss leaves the returned object uninitialized
        (``is_loaded`` is ``False``) instead of raising. Pass ``required=True``
        for the strict :meth:`single` semantics — a miss raises
        :class:`~office365.runtime.types.exceptions.NotFoundException` and an
        ambiguous match raises :class:`ValueError`.
        """
        if required:
            return self.single(expression)
        return self.first_or_none(expression)

    def _find_by_predicate(
        self,
        predicate: Callable[[ClientObjectT], bool],
        description: str,
        *,
        required: bool = False,
    ) -> ClientObjectT:
        """Client-side twin of :meth:`_find_by_filter` for endpoints without ``$filter``.

        The collection is fetched and the first item satisfying ``predicate`` is
        copied into a fresh object, leaving it uninitialized when nothing matches.
        ``required=True`` raises
        :class:`~office365.runtime.types.exceptions.NotFoundException` on a miss
        and :class:`ValueError` on an ambiguous match, mirroring :meth:`single`.
        """
        return_type = self.create_typed_object()
        self.add_child(return_type)

        def _after_loaded(col: ClientObjectCollection) -> None:
            matches = [item for item in col if predicate(item)]
            if not matches:
                if required:
                    raise NotFoundException(return_type, description)
                return
            if required and len(matches) > 1:
                raise ValueError(f"Ambiguous match found for filter: {description}")
            for k, v in matches[0].properties.items():
                return_type.set_property(k, v, False)

        self.get().after_execute(_after_loaded)
        return return_type

    @property
    def parent(self) -> ClientObject | None:
        """Get the parent object that owns this collection."""
        return self._parent

    @property
    def has_next(self) -> bool:
        """Check if more pages are available.

        True when the server signalled a next page (``__next``/``@odata.nextLink``)
        or when a SharePoint collection loaded a full explicit page and the next
        one can still be fetched via ``$skip``.
        """
        if self._next_page is not None:
            # Custom loader (e.g. CAML): more pages while the last one was full.
            return self._paged_mode and self._page_size is not None and len(self.current_page) == self._page_size
        return self._next_request_url is not None or self._can_offset_next()

    @property
    def current_page(self) -> List[ClientObjectT]:
        """Get items from the most recently loaded page."""
        return self._data[self._current_pos :]

    @property
    def entity_type_name(self) -> str | None:  # type: ignore[override]
        """Get the OData type name for this collection."""
        if self._entity_type_name is None:
            client_object = self.create_typed_object()
            self._entity_type_name = f"Collection({client_object.entity_type_name})"
        return self._entity_type_name
