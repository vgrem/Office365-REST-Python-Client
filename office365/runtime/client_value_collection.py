from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Generic, Iterator, TypeVar, cast

from typing_extensions import Self

from office365.runtime.client_value import ClientValue
from office365.runtime.converters.scalars import parse_enum
from office365.runtime.converters.value import serialize_value
from office365.runtime.odata.json_format import ODataJsonFormat
from office365.runtime.odata.v3.json_light_format import JsonLightFormat

ValueT = TypeVar("ValueT")


@dataclass(init=False)
class ClientValueCollection(ClientValue, Generic[ValueT]):
    """A type-safe collection of ClientValue objects or primitives.

    This collection provides:
    - Type enforcement through generics
    - JSON serialization following OData standards
    - Support for both primitive and complex types
    - SharePoint-compatible metadata generation

    Example:
        >>> str_collection = ClientValueCollection(str, ["a", "b"])
        >>> str_collection.add("c")

        >>> uuid_collection = ClientValueCollection(uuid.UUID)
        >>> uuid_collection.add(uuid.uuid4())

        >>> class Address(ClientValue): ...
        >>> addr_collection = ClientValueCollection(Address)
        >>> addr_collection.add(Address())
    """

    _item_type: type[ValueT] | None = field(init=False)
    _data: list[ValueT] = field(default_factory=list)

    def __init__(self, item_type: type[ValueT] | None = None, _data: list[ValueT] | None = None):
        """Initialize a typed collection.

        Args:
            item_type: The type of items in this collection
            _data: Optional initial values (list or dict for complex types)
        """
        self._data = _data or []
        self._item_type = item_type

    def add(self, value: ValueT) -> Self:
        """Adds an item to the collection.

        Args:
            value: Item to add (must match collection type)

        Returns:
            Self: For method chaining

        Raises:
            TypeError: If value doesn't match collection type
        """
        if self._item_type is not None and not isinstance(value, self._item_type):
            raise TypeError(f"Expected {self._item_type}, got {type(value)}")
        self._data.append(value)
        return self

    def __getitem__(self, index: int) -> ValueT:
        """Gets an item by index.

        Args:
            index: Zero-based index

        Returns:
            The item at the specified index

        Raises:
            IndexError: If index is out of range
        """
        return self._data[index]

    def __iter__(self) -> Iterator[ValueT]:  # type: ignore[reportIncompatibleMethodOverride]
        """Iterates through all items in the collection.

        Yields:
            Items in the collection
        """
        return iter(self._data)

    def __len__(self) -> int:
        """Gets the number of items in the collection.

        Returns:
            int: The collection count
        """
        return len(self._data)

    def __add__(self, other: ClientValueCollection) -> list[ValueT]:
        """Concatenate two collections into a plain list."""
        return list(self._data) + list(other._data)

    def clear(self) -> None:
        """Remove all items from the collection."""
        self._data.clear()

    def _display_name(self) -> str:
        """Name used in rendered previews."""
        if self._item_type is not None:
            return f"ClientValueCollection[{self._item_type.__name__}]"
        return "ClientValueCollection"

    def __str__(self) -> str:
        """Items as a bounded list (primitive) or aligned table (complex)."""
        from office365.runtime.display import describe_collection

        return describe_collection(self._data, self._display_name())

    def __repr__(self) -> str:
        """Return the same bounded preview as :meth:`__str__`."""
        return self.__str__()

    def _repr_html_(self) -> str:
        """Render the items as an HTML table (Jupyter/rich display)."""
        from office365.runtime.display import collection_html

        return collection_html(self._data, self._display_name())

    def to_string(self, max_items: int | None = None) -> str:
        """Render every loaded item as a full, aligned table.

        Unlike :meth:`__str__`/:meth:`__repr__` (a bounded preview), this
        renders all items so it can back a report; pass ``max_items`` to cap
        the rows. Columns are not truncated, so a report never loses identifier
        digits.
        """
        from office365.runtime.display import describe_collection

        return describe_collection(self._data, self._display_name(), max_items=max_items, max_column_width=None)

    def to_json(self, json_format: ODataJsonFormat | None = None) -> list[Any] | dict[str, Any]:
        """Serializes the collection to OData JSON format.

        Args:
            json_format: Controls serialization behavior:
                - None: Returns simple array
                - JsonLightFormat: Returns metadata-enriched structure

        Returns:
            list or dict: Serialized data

        Example Outputs:
            Simple: ["a", "b", "c"]
            JsonLight: {
                "results": ["a", "b", "c"],
                "__metadata": {"type": "Collection(Edm.String)"}
            }
        """
        json: list[Any] | dict[str, Any] = [serialize_value(v) for v in self]
        if isinstance(json_format, JsonLightFormat) and json_format.include_control_information:
            json = {
                json_format.collection: json,
                json_format.metadata_type: {"type": self.entity_type_name},
            }
        return json

    def create_typed_value(self, initial_value: ValueT | None = None) -> ValueT:
        """Creates a new item of the collection's type.

        Args:
            initial_value: Optional initialization value

        Returns:
            A new instance of the collection's item type

        Raises:
            TypeError: If collection item type is not set
            ValueError: If initial_value cannot be converted to item_type
        """
        if self._item_type is None:
            raise TypeError("Collection item type is not set")

        if initial_value is None:
            if self._item_type is uuid.UUID:
                return cast(ValueT, uuid.uuid4())
            return cast(ValueT, self._item_type())

        if self._item_type is uuid.UUID:
            return cast(ValueT, uuid.UUID(cast(str, initial_value)))

        if issubclass(self._item_type, Enum):
            return cast(ValueT, parse_enum(self._item_type, cast(str, initial_value)))  # type: ignore[arg-type]

        if issubclass(self._item_type, ClientValue) and isinstance(initial_value, dict):
            value = self._item_type()
            for k, v in initial_value.items():
                value.set_property(k, v, False)
            return cast(ValueT, value)

        return cast(ValueT, initial_value)

    def set_property(self, index: int, value: Any, persist_changes: bool = False) -> Self:  # type: ignore[reportIncompatibleMethodOverride]
        """Adds an item to the collection after type conversion.

        Args:
            index: Unused (maintained for interface compatibility)
            value: Value to add (will be converted to collection type)
            persist_changes: Unused (maintained for interface compatibility)

        Returns:
            Self: For method chaining
        """
        client_value = self.create_typed_value(value)
        self.add(client_value)
        return self

    @property
    def entity_type_name(self) -> str:
        """Gets the OData type name for this collection.

        Returns:
            str: The collection type name (e.g., "Collection(Edm.String)")
        """
        from office365.runtime.odata.type import ODataType

        if self._item_type is None:
            return "Collection(Edm.Unknown)"
        return f"Collection({ODataType.resolve_type_name(self._item_type)})"
