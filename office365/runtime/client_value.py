from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Iterator, List, Optional, Tuple

from typing_extensions import Self

from office365.runtime.converters.value import _add_type_metadata, declared_type, deserialize_value, serialize_value
from office365.runtime.odata.json_format import ODataJsonFormat


def _render(self: "ClientValue") -> str:
    """Bounded, side-effect-free rendering shared by ``str`` and ``repr``."""
    from office365.runtime.display import describe

    return describe(self)


class ClientValue:
    """Represent complex type.
    Complex types consist of a list of properties with no key, and can therefore only exist as properties of a
    containing entity or as a temporary value
    """

    _is_client_value: bool = True

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        # ``@dataclass`` generates a ``__repr__`` unless one is already present
        # in the class ``__dict__``, which would shadow the bounded rendering.
        # Subclasses run ``__init_subclass__`` before the decorator is applied,
        # so seeding the method here keeps dataclass-backed values consistent
        # with every other ClientValue (and with domain overrides that define
        # their own ``__repr__``).
        if "__repr__" not in cls.__dict__:
            cls.__repr__ = _render

    def __str__(self) -> str:
        return _render(self)

    def __repr__(self) -> str:
        return _render(self)

    def __format__(self, format_spec: str) -> str:
        return format(str(self), format_spec)

    def set_property(self, k: str | int, v: Any, persist_changes: bool = True) -> Self:
        k = str(k)
        if v is None:
            setattr(self, k, None)
            return self
        setattr(self, k, deserialize_value(declared_type(type(self), k), v, getattr(self, k, None), persist_changes))
        return self

    def get_property(self, name: str, default_value: Any = None) -> Any:
        """Gets a property value, or ``default_value`` when the property is unset.

        Mirrors :meth:`ClientObject.get_property` so the same call works on a
        ClientValue (e.g. ``draft.body.get_property("content", "")``).

        Args:
            name: Name of the property to retrieve
            default_value: Value to return when the property is missing
        """
        return getattr(self, name, default_value)

    def __iter__(self) -> Iterator[Tuple[str, Any]]:
        for n, v in vars(self).items():
            yield n, v

    def to_json(self, json_format: Optional[ODataJsonFormat] = None) -> Dict[str, Any] | List[Any]:
        """Serializes the ClientValue to JSON format.

        Args:
            json_format: Optional OData JSON formatting options

        Returns:
            Dictionary (or list, for collection values) representing the
            JSON-serialized object
        """

        def _is_valid_value(val):
            from office365.runtime.client_value_collection import ClientValueCollection

            if val is None:
                return False
            elif isinstance(val, datetime) and val == datetime.min:
                return False
            elif isinstance(val, ClientValueCollection) and len(val) == 0:
                return False
            elif isinstance(val, ClientValue):
                if not any(v is not None for v in vars(val).values()):
                    return False
            return True

        result = {k: serialize_value(v, json_format) for k, v in self if _is_valid_value(v)}
        _add_type_metadata(result, json_format, self.entity_type_name)
        return result

    @property
    def entity_type_name(self) -> Optional[str]:
        """The server-side type name for client value.

        Returns:
            Defaults to the class name
        """
        return None
