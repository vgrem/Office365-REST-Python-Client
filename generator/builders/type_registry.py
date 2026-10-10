"""Single registry for OData <-> Python type mapping and code-generation metadata.

Consolidates what used to be three modules — annotation formatting
(``type_mapping``), return/parameter descriptors (``type_descriptor``) and class
resolution (``type_resolver``). A :class:`TypeRegistry` owns the static source
index, so resolution, module lookup and member lookup never import a module
(cycle-safe and deterministic).
"""

from __future__ import annotations

import datetime
import importlib
import inspect
import pkgutil
import uuid
from enum import Enum
from functools import lru_cache
from typing import Optional, Sequence, Tuple, Type

from office365.runtime.client_value import ClientValue
from office365.runtime.odata.type import ODataType

from generator.builders.symbol_index import SymbolIndex

# --------------------------------------------------------------------------- #
# Annotation formatting (pure functions)
# --------------------------------------------------------------------------- #


def python_name(type_name: str | None, is_object_type: bool = False) -> str:
    """Format an OData type name as the Python annotation name.

    ``Edm.Int32`` -> ``int``; ``Collection(Edm.String)`` ->
    ``ClientValueCollection[str]``; ``SP.Web`` -> ``Web``;
    ``Collection(SP.Web)`` -> ``EntityCollection[Web]`` when ``is_object_type``.
    """
    if type_name is None:
        return ""
    primitive = ODataType.primitive_type_for(type_name)
    if primitive is not None:
        return primitive.__name__
    if ODataType.is_collection_name(type_name):
        child = item_name(ODataType.strip_collection(type_name), is_object_type)
        return f"EntityCollection[{child}]" if is_object_type else f"ClientValueCollection[{child}]"
    if type_name.startswith("Edm."):
        raise ValueError(f"Unmapped OData primitive '{type_name}'; add it to ODataType._PRIMITIVE_TYPES.")
    cls_name = type_name.split(".")[-1]
    if cls_name and cls_name[0].islower():
        cls_name = cls_name[0].upper() + cls_name[1:]
    return cls_name


def item_name(type_name: str | None, is_object_type: bool = False) -> str:
    """Format the item type of a collection (or the type itself) as a Python name."""
    return python_name(ODataType.strip_collection(type_name), is_object_type)


# --------------------------------------------------------------------------- #
# Descriptors
# --------------------------------------------------------------------------- #

_PRIMITIVE_DEFAULTS = {
    bool: "bool()",
    int: "int()",
    float: "float()",
    str: "str()",
    bytes: "bytes()",
    uuid.UUID: "UUID(int=0)",
    datetime.datetime: "datetime.min",
    datetime.date: "datetime.min",
    datetime.time: "time.min",
    datetime.timedelta: "datetime.timedelta(0)",
    dict: "{}",
}

_PYTHON_TYPE_NAMES = {
    str: "str",
    int: "int",
    float: "float",
    bool: "bool",
    bytes: "bytes",
    uuid.UUID: "UUID",
    datetime.datetime: "datetime",
    datetime.date: "date",
    datetime.time: "time",
}

_COLLECTION_WRAPPERS = {str: "StringCollection", uuid.UUID: "GuidCollection"}


class TypeKind(Enum):
    """Shape of an OData type reference."""

    VOID = "void"
    PRIMITIVE = "primitive"
    CLIENT_VALUE = "client_value"
    ENTITY = "entity"
    PRIMITIVE_COLLECTION = "primitive_collection"
    CLIENT_VALUE_COLLECTION = "client_value_collection"
    ENTITY_COLLECTION = "entity_collection"


class ReturnType:
    """Classifies a type name once and renders its annotation and default value."""

    def __init__(self, type_name: str | None, registry: Optional[TypeRegistry] = None) -> None:
        self._name = type_name or ""
        self._registry = registry
        self.kind = self._classify()

    @property
    def is_void(self) -> bool:
        return self.kind is TypeKind.VOID

    @property
    def is_stream(self) -> bool:
        return self._name == "Edm.Stream"

    @property
    def annotation(self) -> str:
        """The Python type annotation (without ``ClientResult`` for voids)."""
        name = self._name
        if self.kind in (TypeKind.PRIMITIVE, TypeKind.CLIENT_VALUE):
            return f"ClientResult[{python_name(name)}]"
        if self.kind is TypeKind.ENTITY:
            return python_name(name)
        if self.kind is TypeKind.PRIMITIVE_COLLECTION:
            return f"ClientResult[{self._collection_name(name)}]"
        if self.kind is TypeKind.CLIENT_VALUE_COLLECTION:
            return f"ClientResult[ClientValueCollection[{item_name(name)}]]"
        return f"EntityCollection[{item_name(name)}]"

    def default(self, context: str) -> str:
        """The expression that constructs the return value for ``context``."""
        name = self._name
        if self.kind is TypeKind.PRIMITIVE:
            return f"ClientResult({context}, {_primitive_default(name)})"
        if self.kind is TypeKind.CLIENT_VALUE:
            return f"ClientResult({context}, {python_name(name)}())"
        if self.kind is TypeKind.ENTITY:
            return f"{python_name(name)}({context})"
        if self.kind is TypeKind.PRIMITIVE_COLLECTION:
            return f"ClientResult({context}, {self._collection_default(name)})"
        if self.kind is TypeKind.CLIENT_VALUE_COLLECTION:
            return f"ClientResult({context}, ClientValueCollection[{item_name(name)}]())"
        return f"EntityCollection({context}, {item_name(name)})"

    def _classify(self) -> TypeKind:
        name = self._name
        if not name:
            return TypeKind.VOID
        if ODataType.is_collection_name(name):
            return self._classify_collection(name)
        if ODataType.is_primitive_name(name):
            return TypeKind.PRIMITIVE
        if self._is_client_value(name):
            return TypeKind.CLIENT_VALUE
        return TypeKind.ENTITY

    def _classify_collection(self, name: str) -> TypeKind:
        item_type = ODataType.strip_collection(name)
        if ODataType.is_primitive_name(name) or ODataType.is_primitive_name(item_type):
            return TypeKind.PRIMITIVE_COLLECTION
        if self._is_client_value(item_type):
            return TypeKind.CLIENT_VALUE_COLLECTION
        return TypeKind.ENTITY_COLLECTION

    def _is_client_value(self, type_name: str | None) -> bool:
        if self._registry is None:
            return False
        cls = self._registry.resolve(type_name)
        return cls is not None and issubclass(cls, ClientValue)

    @staticmethod
    def _collection_name(type_name: str) -> str:
        """Python annotation for a collection whose item type is primitive."""
        mapped = ODataType.primitive_type_for(type_name) if ODataType.is_primitive_name(type_name) else None
        if mapped is None:
            return python_name(type_name)
        item_types = getattr(mapped, "__args__", None)
        if item_types:
            return f"{mapped.__name__}[{item_types[0].__name__}]"
        return mapped.__name__

    @staticmethod
    def _collection_default(type_name: str) -> str:
        """Python default expression for a collection whose item type is primitive."""
        if ODataType.is_primitive_name(type_name):
            mapped = ODataType.primitive_type_for(type_name)
            assert mapped is not None
            item_types = getattr(mapped, "__args__", None)
            if item_types:
                return f"ClientValueCollection({item_types[0].__name__})"
            return f"{mapped.__name__}()"
        item_type = ODataType.strip_collection(type_name)
        primitive = ODataType.primitive_type_for(item_type)
        if primitive is not None:
            return f"ClientValueCollection({primitive.__name__})"
        return f"{python_name(type_name)}()"


def _primitive_default(type_name: str | None) -> str:
    """Default expression for a primitive OData type (``Edm.Int32`` -> ``int()``)."""
    return _PRIMITIVE_DEFAULTS.get(ODataType.primitive_type_for(type_name), "None")


class ParameterType:
    """Python annotation and runtime wrapping for an operation parameter.

    Primitive collections are exposed as plain Python lists (``list[str]``,
    ``list[UUID]``) and wrapped into the matching runtime collection when the
    query payload is built.
    """

    def __init__(self, type_name: str | None) -> None:
        self._type_name = type_name
        self._item_type = ODataType.strip_collection(type_name)
        self._python_item = self._resolve_python_item()

    def _resolve_python_item(self) -> Optional[type]:
        if self._type_name is None or not ODataType.is_collection_name(self._type_name):
            return None
        if not ODataType.is_primitive_name(self._item_type):
            return None
        return ODataType.primitive_type_for(self._item_type)

    @property
    def is_primitive_collection(self) -> bool:
        return self._python_item in _PYTHON_TYPE_NAMES

    @property
    def annotation(self) -> str:
        if self.is_primitive_collection:
            return f"list[{_PYTHON_TYPE_NAMES[self._python_item]}]"
        return python_name(self._type_name)

    @property
    def wrapper(self) -> Optional[str]:
        """Runtime collection class used to wrap the argument, if any."""
        if not self.is_primitive_collection:
            return None
        return _COLLECTION_WRAPPERS.get(self._python_item, "ClientValueCollection")

    def wrap(self, expression: str) -> str:
        """Wrap a plain Python list argument into its runtime collection."""
        wrapper = self.wrapper
        if wrapper is None:
            return expression
        if wrapper == "ClientValueCollection":
            return f"ClientValueCollection({_PYTHON_TYPE_NAMES[self._python_item]}, {expression})"
        return f"{wrapper}({expression})"


# --------------------------------------------------------------------------- #
# Class resolution (static index + lazy import)
# --------------------------------------------------------------------------- #


class TypeRegistry:
    """Maps OData type references to Python classes, modules and member names."""

    def __init__(self, modules: Sequence[str], namespace: str = "") -> None:
        self.modules = tuple(sorted(m.strip() for m in modules if m and m.strip()))
        self.namespace = namespace
        self._index = _get_index(self.modules, namespace)

    def resolve(self, type_name: str | None) -> Optional[Type]:
        """Resolve an OData type name (``SP.Directory.User``) to its Python class."""
        if not type_name:
            return None
        short = python_name(ODataType.strip_collection(type_name))
        module_name = self._index.resolve_module(type_name)
        if module_name is not None:
            cls = _class_from_module(module_name, short)
            if cls is not None:
                return cls
        return _resolve_cached(short, self.modules)

    def module_for(self, type_name: str | None) -> Optional[str]:
        """The module defining the referenced class, resolved statically."""
        if not type_name:
            return None
        module = self._index.resolve_module(type_name)
        if module is not None:
            return module
        cls = self.resolve(type_name)
        mod = inspect.getmodule(cls) if cls is not None else None
        return mod.__name__ if mod is not None else None

    def strict_module_for(self, type_name: str | None) -> Optional[str]:
        """Like :meth:`module_for`, but without the import-based bare-name fallback.

        Used for update decisions: a wrong match makes the generator write into a
        file it does not own (e.g. an OData ``StringCollection`` resolving to a
        hand-written runtime module).
        """
        if not type_name:
            return None
        return self._index.resolve_module(type_name)

    def members_of(self, type_name: str | None) -> set[str]:
        """Member names a class already has (incl. inherited), purely from AST."""
        if not type_name:
            return set()
        return self._index.class_members(type_name)

    def return_type(self, type_name: str | None) -> ReturnType:
        return ReturnType(type_name, self)

    @staticmethod
    def cache_clear() -> None:
        _resolve_cached.cache_clear()
        _get_index.cache_clear()


@lru_cache(maxsize=8)
def _get_index(modules: Tuple[str, ...], namespace: str) -> SymbolIndex:
    return SymbolIndex(modules, namespace)


def _class_from_module(module_name: str, class_name: str) -> Optional[Type]:
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        return None
    cls = getattr(module, class_name, None)
    return cls if inspect.isclass(cls) else None


@lru_cache(maxsize=1024)
def _resolve_cached(target_name: str, modules: Tuple[str, ...]) -> Optional[Type]:
    """Searches the configured module roots for a class named ``target_name``."""

    def _search_module(module_name: str) -> Optional[Type]:
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, target_name):
                cls = getattr(module, target_name)
                if inspect.isclass(cls):
                    return cls
            if hasattr(module, "__path__"):
                for _, name, _ in pkgutil.iter_modules(module.__path__):
                    found = _search_module(module_name + "." + name)
                    if found:
                        return found
        except (ImportError, AttributeError):
            pass
        return None

    for module_name in modules:
        result = _search_module(module_name)
        if result:
            return result
    return None
