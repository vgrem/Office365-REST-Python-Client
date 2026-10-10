"""Decide where a type's file lives: an existing module, or a routed new file.

Placement is the one part of :class:`~generator.builders.type.TypeBuilder` that
does not touch the AST: it maps an OData type to a target file (attached vs
detached/routed) using the static index and the routing tables.
"""

from __future__ import annotations

import ast
import importlib.util
import os
from dataclasses import dataclass
from os.path import abspath
from typing import Optional

from generator.builders.context import BuilderContext
from generator.builders.naming import python_name, to_snake_case
from generator.builders.resolution import TypeRegistry
from generator.routing import Router, descend_module, module_directory

_ATTACHED = "attached"
_DETACHED = "detached"


@dataclass(frozen=True)
class Placement:
    """Where a type is read from / written to."""

    state: str  # "attached" (existing file) or "detached" (new file)
    file: str
    routed: bool
    reason: str = ""

    @property
    def is_attached(self) -> bool:
        return self.state == _ATTACHED


def module_file(module_name: str) -> Optional[str]:
    """The source file for a module, resolved without executing it."""
    try:
        spec = importlib.util.find_spec(module_name)
    except (ImportError, ValueError):
        return None
    origin = getattr(spec, "origin", None)
    return origin if origin and origin.endswith(".py") else None


def defines_class(path: str, class_name: str) -> bool:
    """Whether ``path`` defines a top-level class named ``class_name``."""
    try:
        with open(path, encoding="utf-8") as f:
            tree = ast.parse(f.read())
    except (OSError, SyntaxError):
        return False
    return any(isinstance(node, ast.ClassDef) and node.name == class_name for node in tree.body)


class TypePlanner:
    """Resolves a type's target file: an existing module, or a routed new file."""

    def __init__(self, context: BuilderContext, resolver: TypeRegistry) -> None:
        self._context = context
        self._resolver = resolver
        self._router = Router.from_options(context)

    def plan(self, full_name: str, is_value_object: bool) -> Placement:
        """The placement for an OData type name."""
        class_name = python_name(full_name, is_value_object or False)

        module_name = self._resolver.strict_module_for(full_name)
        origin = module_file(module_name) if module_name else None
        if origin is not None:
            return Placement(_ATTACHED, origin, True)

        namespace = full_name.rpartition(".")[0]
        module_path = self._router.module_for(full_name)
        output_base = self._context.output_path
        file_stem = to_snake_case(class_name, avoid_keywords=False)
        if module_path:
            module_path, file_stem = descend_module(module_path, class_name, output_base)
            file_dir = module_directory(module_path, output_base)
        else:
            file_dir = output_base
        file_path = abspath(os.path.join(file_dir, file_stem + ".py"))

        if not module_path:
            return Placement(_DETACHED, file_path, False, f"no routing entry for namespace '{namespace}'")
        if os.path.exists(file_path):
            if defines_class(file_path, class_name):
                return Placement(_ATTACHED, file_path, True)
            # The routed file already exists but strict name resolution missed it
            # (metadata/model name drift). Update it in place only when the class
            # matches; never overwrite a foreign file.
            return Placement(_DETACHED, file_path, False, f"target file exists without class '{class_name}'")
        return Placement(_DETACHED, file_path, True)
