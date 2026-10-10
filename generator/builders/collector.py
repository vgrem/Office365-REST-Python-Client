from __future__ import annotations

import ast
import inspect
from typing import TYPE_CHECKING, ClassVar

from generator.builders.type_registry import ParameterType

if TYPE_CHECKING:
    from generator.builders.property import PropertyBuilder
    from generator.builders.type_registry import TypeRegistry


class TypeReferenceCollector:
    """Collects Python type references required by a generated OData type.

    Runtime imports (builtins, wrappers, query classes) are emitted at module
    top level; entity/client-value types used only in annotations are emitted
    under ``if TYPE_CHECKING:`` so they don't create import cycles. Navigation
    types are imported lazily inside the generated getter (see
    ``PropertyBuilder.runtime_import``).
    """

    KNOWN: ClassVar[dict[str, str]] = {
        "UUID": "uuid",
        "datetime": "datetime",
        "date": "datetime",
        "time": "datetime",
        "StringCollection": "office365.runtime.types.collections",
        "GuidCollection": "office365.runtime.types.collections",
        "Optional": "typing",
        "TYPE_CHECKING": "typing",
        "ResourcePath": "office365.runtime.paths.resource_path",
        "EntityCollection": "office365.entity_collection",
        "ClientValueCollection": "office365.runtime.client_value_collection",
        "ClientResult": "office365.runtime.client_result",
        "ServiceOperationQuery": "office365.runtime.queries.service_operation",
        "FunctionQuery": "office365.runtime.queries.function",
        "Self": "typing_extensions",
        "ClientContext": "office365.sharepoint.client_context",
        "GraphClient": "office365.graph_client",
    }

    OPTIONAL_TYPES: ClassVar[set[str]] = {
        "str",
        "int",
        "bool",
        "float",
        "UUID",
        "bytes",
        "date",
        "time",
        "dict",
        "datetime",
        "list",
    }

    #: Names whose module depends on the generated service (resolved via the
    #: source index first — SharePoint and Graph have different collections).
    SERVICE_TYPES: ClassVar[set[str]] = {"EntityCollection"}

    def __init__(self, resolver: "TypeRegistry") -> None:
        self._resolver = resolver
        self._entries: dict[str, str] = {}
        self._type_checking: dict[str, str] = {}
        self.needs_dataclass = False
        self.needs_field = False

    def add(self, type_name: str) -> None:
        """Track a known runtime type reference.

        Service-specific wrappers (e.g. ``EntityCollection``) resolve through the
        source index so SharePoint vs Graph use their own collection module.
        """
        if type_name in self.SERVICE_TYPES:
            module = self._resolver.module_for(type_name)
            if module:
                self._entries[type_name] = module
                return
        module = self.KNOWN.get(type_name)
        if module:
            self._entries[type_name] = module

    def add_custom(self, prop: PropertyBuilder) -> None:
        """Track annotation imports for client-value types (runtime via the getter).

        Collections contribute their wrapper (``ClientValueCollection``) plus the
        item type; scalars/custom types contribute the type itself. The item/type
        import is emitted under ``TYPE_CHECKING`` and lazily inside the getter —
        except for dataclass fields whose default factory calls the type, which
        need a real import.
        """
        if prop.is_object_type:
            return
        runtime = self.needs_dataclass and prop.needs_runtime_import()
        if prop.is_collection_type:
            if prop.client_type_name.startswith("EntityCollection"):
                self.add("EntityCollection")
            elif prop.client_type_name.startswith("ClientValueCollection"):
                self.add("ClientValueCollection")
            self._add_annotation(prop.client_item_type_name, prop, runtime=runtime)
            return
        self._add_annotation(prop.client_type_name, prop, runtime=runtime)

    def _add_annotation(self, name: str, prop: PropertyBuilder, *, runtime: bool = False) -> None:
        if not name or "[" in name or name in self.KNOWN or name in self.OPTIONAL_TYPES:
            return
        module = self._module_for(prop.schema.TypeName, name)
        if module:
            (self._entries if runtime else self._type_checking)[name] = module

    def add_object_type(self, prop: PropertyBuilder) -> None:
        """Track type references for navigation properties.

        The referenced entity/item type is imported under ``TYPE_CHECKING`` — the
        getter imports it lazily at runtime to avoid circular imports.
        """
        if not self.needs_dataclass:
            # Getters construct children with a ResourcePath; dataclass fields do not.
            self._entries["ResourcePath"] = self.KNOWN["ResourcePath"]
        prop_type = prop.client_type_name
        if prop.is_collection_type:
            if "ClientValueCollection" in prop_type or "ClientValue" in prop_type:
                self.add("ClientValueCollection")
            else:
                self.add("EntityCollection")
        item_name = prop.client_item_type_name if prop.is_collection_type else prop.client_type_name
        module = self._resolver.module_for(prop.schema.TypeName)
        if module and item_name:
            self._type_checking[item_name] = module

    def add_method(self, method, context_type: str = "ClientContext") -> None:
        """Track imports required by a generated operation method."""
        schema = method.schema
        if schema.IsStatic:
            # The context type is only used in the annotation (the body uses the
            # ``context`` parameter), so importing it must not run at module load
            # — that would create client_context <-> utilities cycles.
            module = self.KNOWN.get(context_type)
            if module:
                self._type_checking[context_type] = module
        self.add("FunctionQuery" if schema.Kind == "function" else "ServiceOperationQuery")
        if schema.ReturnTypeFullName:
            self._add_python_type(method.return_annotation)
        elif not schema.IsStatic:
            self.add("Self")
        for param in schema.Parameters or []:
            type_name = param.get("Type")
            if type_name:
                param_type = ParameterType(str(type_name))
                self._add_python_type(param_type.annotation)
                if param_type.wrapper:
                    self.add(param_type.wrapper)

    def _module_for(self, type_name: str | None, python_name: str) -> str | None:
        """Resolve the defining module for a type, statically when possible."""
        module = self._resolver.module_for(type_name)
        if module is not None:
            return module
        cls = self._resolver.resolve(python_name)
        mod = inspect.getmodule(cls) if cls is not None else None
        return mod.__name__ if mod is not None else None

    def _add_python_type(self, type_name: str) -> None:
        """Add an annotation type reference (custom types go under ``TYPE_CHECKING``)."""
        if "[" in type_name and type_name.endswith("]"):
            self._add_python_type(type_name.split("[", 1)[1][:-1])
        base_name = type_name.split("[", maxsplit=1)[0]
        self.add(base_name)
        if base_name in self.KNOWN or base_name in self.OPTIONAL_TYPES:
            return
        module = self._module_for(base_name, base_name)
        if module:
            self._type_checking[base_name] = module

    def build(self) -> list[ast.stmt]:
        """Generate sorted, deduplicated import statements (incl. ``TYPE_CHECKING``)."""
        imports: list[ast.stmt] = []

        if self.needs_dataclass:
            names = [ast.alias(name="dataclass", asname=None)]
            if self.needs_field:
                names.append(ast.alias(name="field", asname=None))
            imports.append(ast.ImportFrom(module="dataclasses", names=names, level=0))

        if self._type_checking:
            self._entries["TYPE_CHECKING"] = self.KNOWN["TYPE_CHECKING"]

        for module, names in sorted(self._group(self._entries).items()):
            imports.append(self._import_from(module, names))

        if self._type_checking:
            body = [
                self._import_from(module, names) for module, names in sorted(self._group(self._type_checking).items())
            ]
            imports.append(ast.If(test=ast.Name(id="TYPE_CHECKING", ctx=ast.Load()), body=body, orelse=[]))

        return imports

    @staticmethod
    def _group(entries: dict[str, str]) -> dict[str, list[str]]:
        modules: dict[str, list[str]] = {}
        for type_name, module in entries.items():
            modules.setdefault(module, []).append(type_name)
        return modules

    @staticmethod
    def _import_from(module: str, names: list[str]) -> ast.ImportFrom:
        return ast.ImportFrom(
            module=module,
            names=[ast.alias(name=name, asname=None) for name in sorted(names)],
            level=0,
        )
