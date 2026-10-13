from __future__ import annotations

from enum import Enum
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    TypeVar,
)

from typing_extensions import Self

from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.client_runtime_context import ClientRuntimeContext
from office365.runtime.converters.value import (
    _add_type_metadata,
    declared_type,
    deserialize_value,
    serialize_value,
    to_snake_case,
)
from office365.runtime.exceptions import ObjectNotFoundException
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.limits import Limit, LimitDecl, collect_class_limits, collect_limit_meta
from office365.runtime.odata.json_format import ODataJsonFormat
from office365.runtime.odata.query_options import QueryOptions
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.retry import DEFAULT_RETRY_EXCEPTIONS
from office365.runtime.types.odata_property import _ODATA_MARKER, ODataPropertyMeta

if TYPE_CHECKING:
    from office365.runtime.client_object_collection import ClientObjectCollection


ClientObjectT = TypeVar("ClientObjectT", bound="ClientObject")


def _swallow_object_not_found(error: ClientRequestException) -> None:
    """Error handler that suppresses a 404 (:class:`ObjectNotFoundException`).

    Any other failure is re-raised so it still propagates to the caller.
    """
    if not isinstance(error, ObjectNotFoundException):
        raise error


class ClientObject:
    """Base client object which defines named properties and relationships of an entity."""

    _odata_meta: dict[str, ODataPropertyMeta] = {}
    _limit_meta: dict[str, Tuple[LimitDecl, ...]] = {}
    _class_limit_decls: Tuple[LimitDecl, ...] = ()

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        meta: dict[str, ODataPropertyMeta] = dict(getattr(cls, "_odata_meta", {}))
        for attr_name, attr in cls.__dict__.items():
            target = attr.fget if isinstance(attr, property) else attr
            m: ODataPropertyMeta | None = getattr(target, _ODATA_MARKER, None)
            if m is not None:
                m.attr = attr_name
                meta[m.name] = m
        cls._odata_meta = meta
        cls._limit_meta = collect_limit_meta(cls)
        cls._class_limit_decls = collect_class_limits(cls)

    def __init__(
        self,
        context: ClientRuntimeContext,
        resource_path: Optional[ResourcePath] = None,
        parent_collection: Optional[ClientObjectCollection] = None,
    ) -> None:
        """
        Initialize a new ClientObject instance.

        Args:
            context: The runtime context for executing operations
            resource_path: The path to this resource in the API
            parent_collection: The collection that contains this object
        """
        self._properties: dict[str, Any] = {}
        self._changes: set[str] = {name for name, m in type(self)._odata_meta.items() if m.persist}
        self._query_options = QueryOptions()
        self._parent_collection = parent_collection
        self._context = context
        self._entity_type_name: Optional[str] = None
        self._resource_path = resource_path

    def add_to_parent_collection(self) -> Self:
        """
        Adds this object to its parent collection.

        Returns:
            The current instance for method chaining

        Raises:
            ValueError: If no parent collection exists
        """
        if self._parent_collection is None:
            raise ValueError("Cannot add to parent collection: no parent collection exists")

        if self._resource_path is None:
            self._resource_path = ResourcePath(None, self._parent_collection.resource_path)
        self._parent_collection.add_child(self)
        return self

    def remove_from_parent_collection(self) -> Self:
        """
        Removes this object from its parent collection, if one exists.

        Returns:
            The current instance for method chaining
        """
        if self._parent_collection is not None:
            self._parent_collection.remove_child(self)
        return self

    def clear_state(self) -> Self:
        """
        Resets the client object's state, clearing any pending changes.

        Persist-marked properties are kept so they stay present and are sent
        again on subsequent updates (``persist=True`` means "always include"),
        while explicitly changed, non-persistable props are dropped.
        """
        persistable = self._persistable_names
        self._properties = {k: v for k, v in self._properties.items() if k not in self._changes or k in persistable}
        self._changes.clear()
        self._query_options = QueryOptions()
        return self

    @property
    def _persistable_names(self) -> set[str]:
        """Names of properties marked ``@odata(persist=True)``."""
        return {name for name, m in type(self)._odata_meta.items() if m.persist}

    @classmethod
    def declared_limits(cls) -> Tuple[Limit, ...]:
        """The limits declared on this class and its methods/properties (``@limit``)."""
        class_limits = tuple(decl.limit for decl in cls._class_limit_decls)
        member_limits = tuple(decl.limit for decls in cls._limit_meta.values() for decl in decls)
        return (*class_limits, *member_limits)

    def execute_query(self) -> Self:
        """
        Submits all pending requests to the server.

        Returns:
            The current instance for method chaining
        """
        self.context.execute_query()
        return self

    async def execute_query_async(self) -> Self:
        """
        Submits all pending requests to the server without blocking the loop.

        Returns:
            The current instance for method chaining
        """
        await self.context.execute_query_async()
        return self

    def execute_query_retry(
        self,
        max_retry: int = 5,
        timeout_secs: int = 5,
        max_delay=None,
        jitter: bool = True,
        success_callback=None,
        failure_callback=None,
        exceptions=DEFAULT_RETRY_EXCEPTIONS,
        is_retriable=None,
    ) -> Self:
        """Executes the current set of data retrieval queries and method invocations and retries it if needed.

        Args:
            max_retry (int): Number of times to retry the request
            timeout_secs (int): Base delay for exponential backoff (seconds)
            max_delay (int): Optional cap on the exponential delay (seconds)
            jitter (bool): Whether to randomize the delay
            success_callback (callable): A callback to call if the request executes successfully.
            failure_callback (callable): A callback to call if the request fails to execute.
            exceptions (tuple): Tuple of exceptions that we retry.
            is_retriable (callable): Optional predicate deciding whether a caught
                exception is retried. Defaults to transient errors; pass
                ``retry_on(...)`` to also retry otherwise-permanent errors.
        """
        self.context.execute_query_retry(
            max_retry=max_retry,
            timeout_secs=timeout_secs,
            max_delay=max_delay,
            jitter=jitter,
            success_callback=success_callback,
            failure_callback=failure_callback,
            exceptions=exceptions,
            is_retriable=is_retriable,
        )
        return self

    async def execute_query_async_retry(
        self,
        max_retry: int = 5,
        timeout_secs: int = 5,
        max_delay=None,
        jitter: bool = True,
        success_callback=None,
        failure_callback=None,
        exceptions=DEFAULT_RETRY_EXCEPTIONS,
        is_retriable=None,
    ) -> Self:
        """Async counterpart of :meth:`execute_query_retry`.

        Args:
            max_retry (int): Number of times to retry the request
            timeout_secs (int): Base delay for exponential backoff (seconds)
            max_delay (int): Optional cap on the exponential delay (seconds)
            jitter (bool): Whether to randomize the delay
            success_callback (callable): Called if the request executes successfully.
            failure_callback (callable): Called if a retry attempt fails.
            exceptions (tuple): Tuple of exceptions that we retry.
            is_retriable (callable): Optional predicate deciding whether a caught
                exception is retried. Defaults to transient errors.
        """
        await self.context.execute_query_async_retry(
            max_retry=max_retry,
            timeout_secs=timeout_secs,
            max_delay=max_delay,
            jitter=jitter,
            success_callback=success_callback,
            failure_callback=failure_callback,
            exceptions=exceptions,
            is_retriable=is_retriable,
        )
        return self

    def before_execute(self, action: Callable[[RequestOptions], None]) -> Self:
        """
        Attaches an event handler that runs before query execution.

        Args:
            action: The callback function to execute

        Returns:
            The current instance for method chaining
        """
        self.context.before_execute(action)
        return self

    def after_execute(
        self,
        action: Callable[[Any], Any],
        execute_first: bool = False,
        include_response: bool = False,
    ) -> Self:
        """
        Attaches an event handler that runs after query execution.

        Args:
            action: The callback function to execute
            execute_first: Whether this handler should run before others
            include_response: Whether to include the raw response

        Returns:
            The current instance for method chaining
        """

        def _wrapped(result):
            action(result if include_response else self)

        self.context.after_execute(_wrapped, execute_first, include_response)
        return self

    def on_error(self, action: Callable[[ClientRequestException], None], once: bool = True) -> Self:
        self.context.on_error(action, once)
        return self

    def copy_from(self, other: ClientObject) -> Self:
        """Copies all properties from the other object into this one."""
        for k, v in other._properties.items():
            self.set_property(k, v, False)
        return self

    def get(self) -> Self:
        """
        Retrieves the client object's data from the server.

        Returns:
            The current instance for method chaining
        """
        self.context.load(self)
        return self

    def get_or_none(self) -> Self:
        """Queue a read that tolerates a missing entity.

        Deferred exactly like :meth:`get`: nothing is sent until the caller runs
        ``execute_query()``. When the entity exists the object is populated; when
        the server reports it missing (HTTP 404, classified as
        :class:`~office365.runtime.exceptions.ObjectNotFoundException`) the error
        is swallowed and the object is left uninitialized — detect that with
        :attr:`is_loaded` (or a typed property being ``None``):

            user = client.users["missing@contoso.com"].get_or_none().execute_query()
            if not user.is_loaded:
                ...

        Any other failure (authentication, throttling, ...) still propagates.

        Returns:
            The current instance for method chaining
        """
        self.get().on_error(_swallow_object_not_found)
        return self

    def _tolerate_missing(self, enabled: bool = True) -> Self:
        """Mark the most recently queued query as tolerating a 404 (one-shot).

        Shared by the ``ignore_missing`` write helpers (``delete_object`` /
        ``recycle``): the error is swallowed only when it is an
        :class:`ObjectNotFoundException`; any other failure propagates.

        Args:
            enabled: When ``False`` this is a no-op, so callers can forward the
                flag unconditionally.
        """
        if enabled:
            self.on_error(_swallow_object_not_found)
        return self

    @property
    def is_loaded(self) -> bool:
        """Whether the object carries data (from a read or a local property set).

        An object that was never initialized — e.g. a lookup that tolerated a 404
        via :meth:`get_or_none` or an empty :meth:`ClientObjectCollection.first_or_none`
        — has no properties and reports ``False``.
        """
        return len(self._properties) > 0

    def __str__(self) -> str:
        """Return the object's natural label (``displayName``/``name``/``title``).

        Falls back to :meth:`__repr__` when no obvious label is loaded, so
        ``print(obj)`` is always meaningful without reaching for a property.
        """
        for name in ("displayName", "name", "title"):
            value = self._properties.get(name)
            if isinstance(value, str) and value:
                return value
        return self.__repr__()

    def __repr__(self) -> str:
        """Return a bounded ``ClassName(prop=value, …)`` rendering.

        Only already-loaded properties are projected; this never triggers a
        request. Used by ``print``/``repr`` and logging.
        """
        from office365.runtime.display import describe

        return describe(self)

    def is_property_available(self, name: str) -> bool:
        """
        Checks if a property has been retrieved or set.

        Args:
            name: The property name to check

        Returns:
            True if the property is available, False otherwise
        """
        if name in self.properties:
            return True
        return False

    def expand(self, names: List[str]) -> Self:
        """
        Specifies related resources to include in the response.

        Args:
            names: List of related resource names to expand

        Returns:
            The current instance for method chaining
        """
        self.query_options.expand = names
        return self

    def select(self, names: List[str]) -> Self:
        """
        Specifies which properties to include in the response.

        Args:
            names: List of property names to select

        Returns:
            The current instance for method chaining
        """
        self.query_options.select = names
        return self

    def get_property(self, name: str, default_value: Any = None) -> Any:
        """
        Gets the value of a property.

        Resolves JSON keys to Python properties via ``@odata`` declaration on the
        property method. Falls back to attribute name normalization for backwards
        compatibility.

        Args:
            name: The property name
            default_value: Default value if property doesn't exist

        Returns:
            The property value or default value
        """
        if default_value is None:
            meta = type(self)._odata_meta.get(name)
            if meta is not None:
                return getattr(self, meta.attr)
            normalized_name = name[0].lower() + name[1:]
            default_value = getattr(self, normalized_name, None)
            if default_value is None:
                # Multi-word names (``onlineMeeting``) map to a snake_case getter.
                default_value = getattr(self, to_snake_case(name), None)
        return self._properties.get(name, default_value)

    def set_property(self, name: str, value: Any, persist_changes: bool = True) -> Self:
        """Set a property, coercing the value to its declared type.

        Uses the shared conversion core (``deserialize_value``/``declared_type``) so
        deserialization and the CSV/JSON pipeline use the same conversions.

        Args:
            name: The property name
            value: The value to set
            persist_changes: Whether to mark the property for persistence

        Returns:
            The current instance for method chaining
        """
        if name == "__odata_type":
            return self
        if persist_changes:
            self._changes.add(name)
        current = self.get_property(name)
        # A getter can return a default enum when nothing is stored yet; that
        # fallback must not drive enum coercion (an unrecognized server value
        # would otherwise be discarded).
        if isinstance(current, Enum) and name not in self._properties:
            current = None
        self._properties[name] = deserialize_value(declared_type(type(self), name), value, current, persist_changes)
        return self

    def ensure_property(self, name: str) -> Self:
        """Ensures a property is loaded before executing an action."""
        return self.ensure_properties([name])

    def ensure_properties(self, names: List[str]) -> Self:
        """Ensures multiple properties are loaded before executing an action."""
        if self.property_ref_name is not None and self.property_ref_name not in names:
            names.append(self.property_ref_name)

        names_to_include = [n for n in names if not self.is_property_available(n)]
        if names_to_include:
            from office365.runtime.queries.read_entity import ReadEntityQuery

            qry = ReadEntityQuery[ClientObject](self, names_to_include)
        else:
            from office365.runtime.queries.deferred import DeferredOperationQuery

            qry = DeferredOperationQuery(self.context, return_type=self)
        self.context.add_query(qry)
        return self

    @property
    def entity_type_name(self) -> str:
        """
        Gets the server type name for this entity.

        Returns:
            The entity type name
        """
        if self._entity_type_name is None:
            self._entity_type_name = type(self).__name__
        return self._entity_type_name

    @property
    def property_ref_name(self) -> Optional[str]:
        """Returns property reference name"""
        return None

    @property
    def resource_url(self) -> Optional[str]:
        """
        Gets the full resource URL for this object.

        Returns:
            The full URL or None if path isn't set
        """
        if self.resource_path is None:
            return None
        return self.context.service_root_url + str(self.resource_path)

    @property
    def context(self) -> ClientRuntimeContext:
        """
        Gets the runtime context for this object.

        Returns:
            The runtime context
        """
        return self._context

    @property
    def resource_path(self) -> Optional[ResourcePath]:
        """
        Gets the resource path for this object.

        Returns:
            The resource path
        """
        return self._resource_path

    @property
    def query_options(self) -> QueryOptions:
        """
        Gets the OData query options for this object.

        Returns:
            The query options
        """
        return self._query_options

    @property
    def properties(self) -> Dict[str, Any]:
        """
        Gets all properties of this object.

        Returns:
            Dictionary of property names and values
        """
        return self._properties

    @property
    def persistable_properties(self):
        return {k: self.get_property(k) for k in self._changes if k in self._properties}

    @property
    def parent_collection(self) -> Optional[ClientObjectCollection]:
        """
        Gets the parent collection of this object.

        Returns:
            The parent collection or None
        """
        return self._parent_collection

    def to_json(self, json_format: Optional[ODataJsonFormat] = None) -> Dict[str, Any] | List[Any]:
        """
        Serializes the client object to a JSON-compatible dictionary.

        Args:
            json_format: The OData JSON format settings

        Returns:
            Dictionary (or list, for collections) representing the serialized object
        """
        if json_format is None:
            include_control_info = False
            json = {k: self.get_property(k) for k in self._properties}
        else:
            include_control_info = self.entity_type_name is not None and json_format.include_control_information
            persistable = self._persistable_names
            json = {k: self.get_property(k) for k in self._properties if k in self._changes or k in persistable}
        json = {k: serialize_value(v, json_format) for k, v in json.items()}

        if json and include_control_info:
            _add_type_metadata(json, json_format, self.entity_type_name)
        return json
