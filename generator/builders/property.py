from __future__ import annotations

import ast
import inspect
from _ast import Assign, Call, Constant
from typing import TYPE_CHECKING, List, Optional

from office365.runtime.client_value import ClientValue
from office365.runtime.odata.type import ODataType

from generator.builders.naming import to_snake_case
from generator.builders.type_registry import item_name, python_name

#: Python names that never need an import (builtins / stdlib shorthands).
_SCALAR_TYPE_NAMES = {
    "str",
    "int",
    "bool",
    "float",
    "bytes",
    "date",
    "time",
    "datetime",
    "dict",
    "list",
    "UUID",
}

if TYPE_CHECKING:
    from generator.builders.template_context import TemplateContext
    from generator.builders.type_registry import TypeRegistry
    from generator.odata.property import PropertyInformation


class PropertyBuilder:
    def __init__(self, schema: PropertyInformation, status="detached", resolver: Optional["TypeRegistry"] = None):
        self.schema = schema
        self.status = status
        self.docstring: Optional[str] = None
        self.cyclic = False
        self.field_alias = "field"
        self._resolver = resolver

    def build(self, template: TemplateContext) -> List[ast.stmt]:
        getter_node = template.build_get_property(self, runtime_import=self.runtime_import())

        # Add docstring if available
        if self.docstring and getter_node.body:
            docstring_node = ast.Expr(value=ast.Constant(value=self.docstring))
            getter_node.body.insert(0, docstring_node)

        # setter = self.build_set_property(self)

        return [getter_node]

    def runtime_import(self) -> Optional[str]:
        """Local import for the type the getter constructs at runtime.

        Entity/complex types (and collection item types) are imported lazily so a
        cyclic navigation annotation doesn't force a module-level cycle.
        """
        if self._resolver is None:
            return None
        name = self.client_item_type_name if self.is_collection_type else self.client_type_name
        if not name or name in _SCALAR_TYPE_NAMES:
            return None
        module = self._resolver.module_for(self.schema.TypeName)
        if not module:
            return None
        return f"from {module} import {name}"

    def build_param(self):
        """Build an ast.arg parameter"""
        return ast.arg(
            arg=self.name,
            annotation=(ast.Name(id=self.client_type_name, ctx=ast.Load()) if self.client_type_name else None),
        )

    def build_default_value(self) -> Constant | Call:
        """Build default value"""
        if self.is_collection_type:
            base_name = self.client_type_name.split("[")[0]
            if ODataType.is_primitive_name(self.schema.TypeName):
                return ast.Call(
                    func=ast.Name(id=self.field_alias, ctx=ast.Load()),
                    args=[],
                    keywords=[
                        ast.keyword(
                            arg="default_factory",
                            value=ast.Name(id=base_name, ctx=ast.Load()),
                        )
                    ],
                )
            else:
                item_name = self.client_item_type_name
                return ast.Call(
                    func=ast.Name(id=self.field_alias, ctx=ast.Load()),
                    args=[],
                    keywords=[
                        ast.keyword(
                            arg="default_factory",
                            value=ast.Lambda(
                                args=ast.arguments(posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]),
                                body=ast.Call(
                                    func=ast.Name(id=base_name, ctx=ast.Load()),
                                    args=[ast.Name(id=item_name, ctx=ast.Load())],
                                    keywords=[],
                                ),
                            ),
                        )
                    ],
                )
        elif ODataType.is_primitive_name(self.schema.TypeName):
            if self.client_type_name == "datetime":
                return ast.Call(
                    func=ast.Name(id=self.field_alias, ctx=ast.Load()),
                    args=[],
                    keywords=[
                        ast.keyword(
                            arg="default_factory",
                            value=ast.Lambda(
                                args=ast.arguments(posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]),
                                body=ast.Attribute(
                                    value=ast.Name(id="datetime", ctx=ast.Load()),
                                    attr="min",
                                    ctx=ast.Load(),
                                ),
                            ),
                        )
                    ],
                )
            return ast.Constant(value=None)
        else:
            return ast.Call(
                func=ast.Name(id=self.field_alias, ctx=ast.Load()),
                args=[],
                keywords=[
                    ast.keyword(
                        arg="default_factory",
                        value=ast.Name(id=self.client_type_name, ctx=ast.Load()),
                    )
                ],
            )

    def build_assign(self) -> Assign:
        """Build assignment statement"""
        return ast.Assign(
            targets=[
                ast.Attribute(
                    value=ast.Name(id="self", ctx=ast.Load()),
                    attr=self.schema.Name,
                    ctx=ast.Store(),
                )
            ],
            value=ast.Name(id=self.name, ctx=ast.Load()),
        )

    def resolve_client_type(self):
        """Resolves the property's OData type to its generated Python class."""
        return self._resolver.resolve(self.schema.TypeName) if self._resolver is not None else None

    @property
    def name(self) -> str:
        """Convert CamelCase to snake_case"""
        return to_snake_case(self.schema.Name)

    @property
    def client_type_name(self) -> str:
        return python_name(self.schema.TypeName, self.is_object_type)

    @property
    def client_item_type_name(self) -> str:
        return item_name(self.schema.TypeName, self.is_object_type)

    @property
    def is_collection_type(self) -> bool:
        return ODataType.is_collection_name(self.schema.TypeName)

    @property
    def is_object_type(self) -> bool:
        return self.schema.IsNavigation or False

    def needs_runtime_import(self) -> bool:
        """Whether a dataclass field references its type at run time.

        Complex values use ``field(default_factory=X)`` and enums ``X.member``
        (both evaluated when the class is built); entities default to ``None``.
        """
        from enum import Enum

        if self.cyclic:
            # A cyclic reference must not be imported/constructed at module load.
            return False
        if self.is_collection_type:
            return not ODataType.is_primitive_name(self.schema.TypeName)
        if ODataType.is_primitive_name(self.schema.TypeName):
            return False
        resolved = self.resolve_client_type()
        if resolved is None or not inspect.isclass(resolved):
            return True  # unknown type is treated as a complex value -> factory default
        return issubclass(resolved, (ClientValue, Enum))
