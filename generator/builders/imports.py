"""Import collection and insertion for generated/updated modules.

Pure functions over an ``ast.Module``, isolated from
:class:`~generator.builders.type.TypeBuilder` so the deduplication and
``TYPE_CHECKING`` handling can be tested directly.
"""

from __future__ import annotations

import ast

from generator.builders.source_editor import is_type_checking


def class_name_collides_with_import(module: ast.Module, class_name: str) -> bool:
    """True when the class name shadows an imported name (e.g. ``StringCollection``)."""
    for node in module.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                if alias.asname is None and alias.name == class_name:
                    return True
    return False


def existing_import_names(module: ast.Module) -> set:
    """The set of ``(module, bound_name)`` pairs already imported in ``module``."""
    names: set = set()
    for node in module.body:
        if isinstance(node, ast.ImportFrom):
            names.update((node.module, alias.asname or alias.name) for alias in node.names)
        elif isinstance(node, ast.Import):
            names.update((alias.name, None) for alias in node.names)
        elif isinstance(node, ast.If) and isinstance(node.test, ast.Name) and node.test.id == "TYPE_CHECKING":
            for child in node.body:
                if isinstance(child, ast.ImportFrom):
                    names.update((child.module, alias.asname or alias.name) for alias in child.names)
    return names


def make_import(module_name: str, names: list) -> ast.ImportFrom:
    """Build a sorted ``from <module> import <names>`` statement."""
    return ast.ImportFrom(
        module=module_name, names=[ast.alias(name=name, asname=None) for name in sorted(names)], level=0
    )


def insert_import(module: ast.Module, imp: ast.stmt, existing: set, index: int) -> bool:
    """Insert an import (or ``TYPE_CHECKING`` block) with only the missing names."""
    if isinstance(imp, ast.If):
        body = []
        for child in imp.body:
            kept = [alias.name for alias in child.names if (child.module, alias.name) not in existing]
            if kept:
                body.append(make_import(child.module, kept))
                existing.update((child.module, name) for name in kept)
        if not body:
            return False
        imp.body = body
    elif isinstance(imp, ast.Import):
        kept_imports = [alias for alias in imp.names if (alias.name, None) not in existing]
        if not kept_imports:
            return False
        imp.names = [ast.alias(name=alias.name, asname=alias.asname) for alias in kept_imports]
        existing.update((alias.name, None) for alias in kept_imports)
    else:
        kept_aliases = [alias for alias in imp.names if (imp.module, alias.asname or alias.name) not in existing]
        if not kept_aliases:
            return False
        imp.names = [ast.alias(name=alias.name, asname=alias.asname) for alias in kept_aliases]
        existing.update((imp.module, alias.asname or alias.name) for alias in kept_aliases)
    module.body.insert(index, imp)
    return True


def install_imports(module: ast.Module, references: list, existing: set, index: int) -> list[ast.stmt]:
    """Insert the missing imports from ``references``; return the inserted statements."""
    inserted: list[ast.stmt] = []
    for imp in references:
        if insert_import(module, imp, existing, index):
            index += 1
            inserted.append(imp)
    return inserted


def drop_unused_type_checking(module: ast.Module, added_imports: list[ast.stmt]) -> list[ast.stmt]:
    """Drop a ``TYPE_CHECKING`` import when its block was deduplicated away.

    Returns ``added_imports`` pruned to the statements still present in ``module``.
    """
    if any(isinstance(n, ast.If) and is_type_checking(n) for n in module.body):
        return added_imports
    for node in module.body:
        if isinstance(node, ast.ImportFrom) and node.module == "typing":
            node.names = [alias for alias in node.names if alias.name != "TYPE_CHECKING"]
    module.body = [
        n for n in module.body if not (isinstance(n, ast.ImportFrom) and n.module == "typing" and not n.names)
    ]
    kept = {id(n) for n in module.body}
    return [imp for imp in added_imports if id(imp) in kept]
