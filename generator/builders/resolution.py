"""Resolve OData type references to Python classes and modules.

A :class:`TypeRegistry` owns the static source index, so resolution, module
lookup and member lookup never import a module (cycle-safe and deterministic).
"""

from __future__ import annotations

import importlib
import inspect
import pkgutil
from functools import lru_cache
from typing import Optional, Sequence, Tuple, Type

from generator.builders.naming import python_name
from generator.builders.references import ReturnType
from generator.builders.symbol_index import SymbolIndex
from generator.odata.type_system import normalize_type_name, strip_collection


class TypeRegistry:
    """Maps OData type references to Python classes, modules and member names."""

    def __init__(self, modules: Sequence[str], namespace: str = "", type_modules: Optional[dict] = None) -> None:
        self.modules = tuple(sorted(m.strip() for m in modules if m and m.strip()))
        self.namespace = namespace
        self._index = _get_index(self.modules, namespace)
        #: Planned module for types this run will generate (attached or routed).
        self._type_modules = dict(type_modules or {})

    def resolve(self, type_name: str | None) -> Optional[Type]:
        """Resolve an OData type name (``SP.Directory.User``) to its Python class."""
        if not type_name:
            return None
        short = python_name(strip_collection(type_name))
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
        key = normalize_type_name(type_name) or type_name
        planned = self._type_modules.get(key)
        if planned is not None:
            return planned
        module = self._index.resolve_module(type_name)
        if module is not None:
            return module
        cls = self.resolve(type_name)
        mod = inspect.getmodule(cls) if cls is not None else None
        return mod.__name__ if mod is not None else None

    def strict_module_for(self, type_name: str | None) -> Optional[str]:
        """Like :meth:`module_for`, but without any bare-class-name fallback.

        Used for update decisions: a wrong match makes the generator write into a
        file it does not own (e.g. a same-named OData type of a different kind,
        or a hand-written runtime module).
        """
        if not type_name:
            return None
        return self._index.resolve_module(type_name, strict=True)

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
        except Exception:  # a broken/cyclic module must not block resolution
            pass
        return None

    for module_name in modules:
        result = _search_module(module_name)
        if result:
            return result
    return None
