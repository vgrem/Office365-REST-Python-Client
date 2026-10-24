"""Scan the source for ``@limit`` / ``@bounded`` bindings (docs helper).

Two things the docs pages need, both derived rather than hand-kept:

- :func:`scan_bindings` — ``{limit_attr_name: ["Class", "Class.method", ...]}``, the
  attribute name of the limit expression (``Limits.LIST_VIEW`` -> ``"LIST_VIEW"``,
  the catalog tuple ``*EXCEL_QUOTAS`` -> ``"EXCEL_QUOTAS"``) mapped to the
  classes/methods that declare it. Pure ``ast`` (no imports, no side effects).
- :func:`row_attrs` — the reverse for ``@limit``-declared rows that came from a
  catalog: ``{id(row): "ATTR_NAME"}``, read off the modules already imported, so
  :func:`bound_at` can answer "which model declares this published row?".
"""

from __future__ import annotations

import ast
import pathlib
import sys
from typing import Iterator, Optional

from office365.runtime.limits import Limit

_DECORATORS = {"limit", "bounded"}


def _limit_attr_name(node: ast.expr) -> Optional[str]:
    """The ``X`` in ``Limits.X`` / ``GraphLimits.X`` / ``*EXCEL_QUOTAS`` / ``LOCAL``."""
    if isinstance(node, ast.Starred):
        return _limit_attr_name(node.value)
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _is_decorator(node: ast.expr) -> bool:
    return isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in _DECORATORS


def _decorated(tree: ast.Module) -> Iterator[tuple[str, list[ast.expr]]]:
    """Yield ``(owner, decorator_args)`` for every ``@limit``-decorated target.

    ``owner`` is the class name for a class decorator (``@limit(*EXCEL_QUOTAS)`` on
    ``Workbook``) and ``Class.method`` for a method one.
    """
    for cls in (node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)):
        for dec in cls.decorator_list:
            if _is_decorator(dec):
                yield cls.name, dec.args
        for item in cls.body:
            if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for dec in item.decorator_list:
                if _is_decorator(dec):
                    yield f"{cls.name}.{item.name}", dec.args


def scan_bindings(root: pathlib.Path) -> dict[str, list[str]]:
    """Map each declared limit (by attribute name) to where it's bound."""
    result: dict[str, list[str]] = {}
    for path in sorted(root.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for owner, args in _decorated(tree):
            for arg in args:
                name = _limit_attr_name(arg)
                if name is not None:
                    result.setdefault(name, []).append(owner)
    return result


def row_attrs() -> dict[int, str]:
    """Map every declared row to the attribute name it is declared under.

    Reads the modules already imported — importing ``office365.limits`` brings in every
    catalog — so a row shared between a catalog tuple and a class attribute keeps the
    first name found.
    """
    names: dict[int, str] = {}
    for module in list(sys.modules.values()):
        if not getattr(module, "__name__", "").startswith("office365."):
            continue
        for attr, value in vars(module).items():
            if isinstance(value, Limit):
                names.setdefault(id(value), attr)
            elif isinstance(value, type):
                for class_attr, class_value in vars(value).items():
                    if isinstance(class_value, Limit):
                        names.setdefault(id(class_value), class_attr)
            elif isinstance(value, (list, tuple)):
                for row in value:
                    if isinstance(row, Limit):
                        names.setdefault(id(row), attr)
    return names


def bound_at(row: Limit, bindings: dict[str, list[str]], names: dict[int, str]) -> str:
    """The classes/methods that declare ``row``, or ``""`` when nothing binds it."""
    attr = names.get(id(row))
    return ", ".join(sorted(set(bindings.get(attr, [])))) if attr else ""
