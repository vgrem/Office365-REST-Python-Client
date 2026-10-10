import ast
import copy
import importlib.util
import inspect
import keyword
import os
from _ast import Module
from enum import Enum
from os.path import abspath
from typing import Dict, List, Optional

from office365.runtime.client_object import ClientObject
from office365.runtime.client_value import ClientValue
from office365.runtime.odata.type import ODataType
from typing_extensions import Self

from generator.builders.collector import TypeReferenceCollector
from generator.builders.member import MemberBuilder
from generator.builders.method import MethodBuilder
from generator.builders.naming import to_snake_case
from generator.builders.property import PropertyBuilder
from generator.builders.render import normalize_quotes, ruff_normalize
from generator.builders.template_context import TemplateContext
from generator.builders.type_registry import TypeRegistry, python_name
from generator.documentation.base import DocumentationProvider
from generator.odata.type_information import TypeInformation
from generator.routing import Router
from generator.validation import ValidationError

# Base model members that generated operation methods must not shadow.
_RESERVED_METHOD_NAMES = (
    {name for name in dir(ClientObject)} | {name for name in dir(ClientValue)} | {"update", "delete_object", "id"}
)

# Base model members that generated properties must not shadow (e.g. ``ResourcePath`` -> ``resource_path``).
_RESERVED_PROPERTY_NAMES = {name for name in dir(ClientObject)} | {name for name in dir(ClientValue)}

#: Bound operations with more parameters than this are skipped (unusable, and
#: they exceed the linter's ``max-args``).
_MAX_METHOD_PARAMS = 50


#: Line length enforced by ruff; long import lines get an explicit ``# noqa``.
_MAX_LINE = 121


def _suppress_long_imports(source: str) -> str:
    """Append ``# noqa: E501`` to import lines longer than the limit (applied last)."""
    lines = [
        line + "  # noqa: E501"
        if len(line) > _MAX_LINE and line.lstrip().startswith(("from ", "import ")) and "noqa" not in line
        else line
        for line in source.splitlines()
    ]
    return "\n".join(lines) + ("\n" if source.endswith("\n") else "")


def _is_type_checking(node: ast.If) -> bool:
    test = node.test
    return (isinstance(test, ast.Name) and test.id == "TYPE_CHECKING") or (
        isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING"
    )


def _has_future_annotations(tree: ast.Module) -> bool:
    """Whether the module already imports ``from __future__ import annotations``."""
    return any(
        isinstance(node, ast.ImportFrom)
        and node.module == "__future__"
        and any(alias.name == "annotations" for alias in node.names)
        for node in tree.body
    )


def _is_datetime_class_import(imp: ast.stmt) -> bool:
    return (
        isinstance(imp, ast.ImportFrom)
        and imp.module == "datetime"
        and any(alias.name == "datetime" for alias in imp.names)
    )


def _is_datetime_class_import(imp: ast.stmt) -> bool:
    return (
        isinstance(imp, ast.ImportFrom)
        and imp.module == "datetime"
        and any(alias.name == "datetime" for alias in imp.names)
    )


#: Annotation names that may also be bound as a module in the target file.
_MODULE_QUALIFIED = ("datetime", "date", "time")


def _module_bound_names(tree: ast.Module) -> set[str]:
    """Names in ``{datetime, date, time}`` that the file imports as a module."""
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                base = alias.name.split(".")[0]
                if base in _MODULE_QUALIFIED:
                    names.add(base)
    return names


def _strip_module_names(imports: list[ast.stmt], names: set[str]) -> list[ast.stmt]:
    """Drop ``from datetime import X`` names the file already binds as a module."""
    result: list[ast.stmt] = []
    for node in imports:
        stripped = node
        if isinstance(node, ast.ImportFrom) and node.module == "datetime":
            kept = [alias for alias in node.names if alias.name not in names]
            if not kept:
                continue
            stripped = ast.ImportFrom(module=node.module, names=kept, level=0)
        result.append(stripped)
    return result


class _ModuleQualifier(ast.NodeTransformer):
    """Qualify generated primitive references as ``<qualifier>.<name>``."""

    def __init__(self, names: set[str], qualifier: str) -> None:
        self._names = names
        self._qualifier = qualifier

    def visit_Name(self, node: ast.Name):
        if isinstance(node.ctx, ast.Load) and node.id in self._names:
            return ast.copy_location(
                ast.Attribute(
                    value=ast.Name(id=self._qualifier, ctx=ast.Load()),
                    attr=node.id,
                    ctx=ast.Load(),
                ),
                node,
            )
        return node


def _qualify_modules(node: ast.stmt, names: set[str], qualifier: str) -> ast.stmt:
    return _ModuleQualifier(names, qualifier).visit(copy.deepcopy(node))


def _qualify_datetime(node: ast.stmt) -> ast.stmt:
    return _qualify_modules(node, {"datetime"}, "datetime")


class TypeBuilder(ast.NodeTransformer):
    """Type builder"""

    def __init__(
        self,
        type_schema: TypeInformation,
        options: Optional[Dict[str, str]] = None,
        docs_service: Optional[DocumentationProvider] = None,
        resolver: Optional[TypeRegistry] = None,
    ):
        self._schema = type_schema
        self._options = options
        self._docs_service = docs_service
        self._template: Optional[TemplateContext] = None
        self._type_info: Optional[Dict] = None
        self._source_tree: Optional[Module] = None
        self._status: Optional[str] = None
        self._properties: List[PropertyBuilder] = []
        self._members: List[MemberBuilder] = []
        self._methods: List[MethodBuilder] = []
        self._changes: List[str] = []
        self._docstring: Optional[str] = None
        self._entity_type_name_exists: bool = False
        self._known_types: set[str] = set((options or {}).get("known_types", ()))
        self._original_text: Optional[str] = None
        self._added_members: List[ast.stmt] = []
        self._added_imports: List[ast.stmt] = []
        self._rendered: Optional[str] = None
        self._uses_field = False
        self._added_props: List[PropertyBuilder] = []
        self._cyclic_types: set[str] = set((options or {}).get("cyclic_types", ()))
        self._resolver = resolver or TypeRegistry(
            (options or {}).get("modules", "").split(","),
            namespace=(options or {}).get("namespace", ""),
            type_modules=(options or {}).get("type_modules"),
        )

    def _process(self, module: ast.Module) -> None:
        """Process the single target class of the module (fail on ambiguity)."""
        classes = [node for node in module.body if isinstance(node, ast.ClassDef)]
        if not classes:
            return
        if self.state == "attached":
            targets = [node for node in classes if node.name == self.client_type_name]
            if len(targets) != 1:
                raise ValidationError(
                    f"{self.client_type_name}: expected exactly one top-level class, found {len(targets)}"
                )
        else:
            targets = classes[:1]
        node = targets[0]
        if any(isinstance(base, ast.Name) and base.id == self.client_type_name for base in node.bases):
            # e.g. a type named ``Entity`` inheriting the ``Entity`` base — invalid.
            print(f"  Skipping {self.client_type_name}: class name collides with its base")
            self._status = None
            return
        node.name = self.client_type_name
        self._collect_schema_members()
        self._process_class(node)

    def _process_class(self, node: ast.ClassDef) -> None:
        self.generic_visit(node)

        kind = self._effective_kind(node)
        if kind == "ComplexType":
            self._build_value_properties(node)
        elif kind == "EnumType":
            self._build_members(node)
        else:
            self._build_object_properties(node)

        self._build_post(node)
        self._build_methods(node)

    def _effective_kind(self, node: ast.ClassDef) -> str:
        """The kind to build from, honouring the on-disk class's actual base.

        SharePoint metadata sometimes marks a type ``EntityType`` while the model
        (correctly) implements it as a ``ClientValue`` dataclass. Building entity
        getters (``self.properties``) into a value type is invalid, so the class
        base wins over the metadata kind.
        """
        bases = {base.id for base in node.bases if isinstance(base, ast.Name)}
        if "ClientValue" in bases:
            return "ComplexType"
        if "Enum" in bases:
            return "EnumType"
        return self._schema.BaseTypeFullName

    def _collect_schema_members(self) -> None:
        """Collect the schema members that are missing from the class (once).

        Names are de-duplicated by their Python (snake_case) form: an OData type
        can expose both a property and a bound function with the same name (e.g.
        ``Settings``), which would otherwise generate two identical members.
        """
        options = self._options or {}
        reserved_props = self._reserved_names(_RESERVED_PROPERTY_NAMES)
        ignored_properties = set(options.get("ignored_properties", []))
        self._properties = []
        seen_props: set[str] = set()
        for name, prop_schema in self._schema.Properties.items():
            snake = to_snake_case(name)
            if name in ignored_properties or snake in reserved_props or snake in seen_props:
                continue
            if not self._is_resolvable(prop_schema.TypeName):
                continue
            self._properties.append(PropertyBuilder(prop_schema, resolver=self._resolver))
            self._properties[-1].cyclic = ODataType.strip_collection(prop_schema.TypeName or "") in self._cyclic_types
            seen_props.add(snake)

        self._members = [MemberBuilder(member_schema) for _, member_schema in self._schema.Members.items()]

        ignored_methods = set(options.get("ignored_methods", []))
        reserved_methods = self._reserved_names(_RESERVED_METHOD_NAMES) | seen_props
        self._methods = []
        seen_methods: set[str] = set()
        for method_name, method_schema in self._schema.Methods.items():
            snake = to_snake_case(method_name, avoid_builtins=True)
            if method_name in ignored_methods or snake in reserved_methods or snake in seen_methods:
                continue
            if len(method_schema.Parameters or []) > _MAX_METHOD_PARAMS:
                continue
            if not self._method_is_resolvable(method_schema):
                continue
            self._methods.append(MethodBuilder(method_schema, resolver=self._resolver))
            seen_methods.add(snake)

    def _is_resolvable(self, type_name: Optional[str]) -> bool:
        """Whether a referenced OData type can be imported.

        A member is only generated when every type it names is a primitive, an
        existing class, or a type this run will create. Otherwise the annotation
        would reference an undefined name (e.g. an ``ignored_types`` namespace).
        """
        if not type_name:
            return True
        if ODataType.is_collection_name(type_name):
            return self._is_resolvable(ODataType.strip_collection(type_name))
        if ODataType.is_primitive_name(type_name):
            return True
        module = self._resolver.module_for(type_name)
        return module is not None and not self._is_shadowed(module)

    @staticmethod
    def _is_shadowed(module_name: str) -> bool:
        """Whether ``module_name`` is shadowed by a same-named package.

        ``a/b.py`` and ``a/b/__init__.py`` cannot coexist: imports resolve to the
        package, so a class defined in the module is unreachable.
        """
        spec = importlib.util.find_spec(module_name)
        return spec is not None and spec.submodule_search_locations is not None

    def _method_is_resolvable(self, method_schema) -> bool:
        if method_schema.ReturnTypeFullName and not self._is_resolvable(method_schema.ReturnTypeFullName):
            return False
        return all(self._is_resolvable(param.get("Type")) for param in method_schema.Parameters or [])

        if self._docs_service:
            self._docs_service.build_documentation(self)

    def _reserved_names(self, base: set[str]) -> set[str]:
        """Base names plus every member the generated class already declares (incl. inherited)."""
        return set(base) | self._resolver.members_of(self._schema.FullName)

    def visit_FunctionDef(self, node):
        if node.name == "__init__":
            return self.generic_visit(node)

        is_property = False
        for decorator in node.decorator_list:
            if (isinstance(decorator, ast.Name) and decorator.id == "property") or (
                isinstance(decorator, ast.Attribute) and decorator.attr == "property"
            ):
                is_property = True
                break

        if is_property:
            # Track entity_type_name property
            if node.name == "entity_type_name":
                self._entity_type_name_exists = True

            matching_prop = next((prop for prop in self._properties if prop.name == node.name), None)
            if matching_prop:
                matching_prop.status = "attached"
        else:
            matching_method = next((m for m in self._methods if m.name == node.name), None)
            if matching_method:
                matching_method.status = "attached"

        return self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute):
        if (
            isinstance(node.ctx, ast.Store)
            and isinstance(node.value, ast.Name)
            and node.value.id == "self"
            and isinstance(node.attr, str)
        ):
            prop_name = node.attr
            matching_prop = next((prop for prop in self._properties if prop.name == prop_name), None)
            if matching_prop:
                matching_prop.status = "attached"

        return node

    def build(self) -> Self:
        assert self._options is not None
        self._template = TemplateContext(
            self._options.get("template_path", self._options.get("templatepath", "")),
            self._schema,
        )

        if self.state == "attached":
            with open(self.file, encoding="utf-8") as f:
                self._original_text = f.read()
            self._source_tree = ast.parse(self._original_text)
            self._status = "updated"
        else:
            self._source_tree = self._template.load()
            self._status = "created"
        self._process(self._source_tree)
        self._build_imports(self._source_tree)

        if self._status in {"created", "updated"} and self._class_name_collides_with_import(self._source_tree):
            print(f"  Skipping {self.client_type_name}: name collides with an imported type")
            self._status = None

        if self._status == "updated" and len(self._changes) == 0:
            self._status = None
        return self

    def _class_name_collides_with_import(self, module: ast.Module) -> bool:
        """True when the class name shadows an imported name (e.g. ``StringCollection``)."""
        for node in module.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    if alias.asname is None and alias.name == self.client_type_name:
                        return True
        return False

    def _build_imports(self, module: ast.Module):
        """Build missing imports using TypeReferenceCollector (deduplicated)."""
        assert self._template is not None
        assert self._options is not None
        collector = TypeReferenceCollector(self._resolver)
        collector.needs_dataclass = self._schema.BaseTypeFullName == "ComplexType" and bool(self._added_props)
        collector.needs_field = self._uses_field

        for prop in self._added_props:
            prop_type = prop.client_type_name
            if prop_type in TypeReferenceCollector.OPTIONAL_TYPES and not collector.needs_dataclass:
                # Getters use ``Optional[X]``; dataclass fields use ``X | None``.
                collector.add("Optional")
            collector.add(prop_type)
            collector.add_custom(prop)
            if prop.is_object_type:
                collector.add_object_type(prop)

        context_type = self._options.get("context_type", "ClientContext")
        if self._generate_methods_enabled():
            for method in self._methods:
                if method.status != "attached":
                    collector.add_method(method, context_type)

        existing = self._existing_import_names(module)
        insert_index = len([n for n in module.body if isinstance(n, (ast.Import, ast.ImportFrom))])
        for imp in self._template.build_references(collector):
            if self._insert_import(module, imp, existing, insert_index):
                insert_index += 1
                self._added_imports.append(imp)
        self._drop_unused_type_checking(module)

    def _drop_unused_type_checking(self, module: ast.Module) -> None:
        """Drop a ``TYPE_CHECKING`` import when its block was deduplicated away."""
        if any(isinstance(n, ast.If) and _is_type_checking(n) for n in module.body):
            return
        for node in module.body:
            if isinstance(node, ast.ImportFrom) and node.module == "typing":
                node.names = [alias for alias in node.names if alias.name != "TYPE_CHECKING"]
        module.body = [
            n for n in module.body if not (isinstance(n, ast.ImportFrom) and n.module == "typing" and not n.names)
        ]
        kept = {id(n) for n in module.body}
        self._added_imports = [imp for imp in self._added_imports if id(imp) in kept]

    def _insert_import(self, module: ast.Module, imp: ast.stmt, existing: set, index: int) -> bool:
        """Insert an import (or ``TYPE_CHECKING`` block) with only the missing names."""
        if isinstance(imp, ast.If):
            body = []
            for child in imp.body:
                kept = [alias.name for alias in child.names if (child.module, alias.name) not in existing]
                if kept:
                    body.append(self._make_import(child.module, kept))
                    existing.update((child.module, name) for name in kept)
            if not body:
                return False
            imp.body = body
        else:
            kept = [alias.name for alias in imp.names if (imp.module, alias.name) not in existing]
            if not kept:
                return False
            imp.names = [ast.alias(name=name, asname=None) for name in kept]
            existing.update((imp.module, name) for name in kept)
        module.body.insert(index, imp)
        return True

    @staticmethod
    def _make_import(module_name: str, names: list) -> ast.ImportFrom:
        return ast.ImportFrom(
            module=module_name, names=[ast.alias(name=name, asname=None) for name in sorted(names)], level=0
        )

    @staticmethod
    def _existing_import_names(module: ast.Module) -> set:
        names: set = set()
        for node in module.body:
            if isinstance(node, ast.ImportFrom):
                names.update((node.module, alias.name) for alias in node.names)
            elif isinstance(node, ast.Import):
                names.update((alias.name, None) for alias in node.names)
            elif isinstance(node, ast.If) and isinstance(node.test, ast.Name) and node.test.id == "TYPE_CHECKING":
                for child in node.body:
                    if isinstance(child, ast.ImportFrom):
                        names.update((child.module, alias.name) for alias in child.names)
        return names

    def _build_members(self, class_node: ast.ClassDef):
        if not self._members:
            return

        assert self._template is not None
        existing_members = self._template.get_existing_members(class_node)

        insert_pos = self._last_stmt_index(class_node.body, (ast.Assign,))

        for member_builder in self._members:
            if member_builder.name not in existing_members:
                assert self._template is not None
                member_nodes = member_builder.build(self._template)
                for node in member_nodes:
                    class_node.body.insert(insert_pos, node)
                    insert_pos += 1
                self._added_members.extend(member_nodes)
                self._changes.append(f"member: {member_builder.name}")
                existing_members.add(member_builder.name)

    def _build_value_properties(self, class_node: ast.ClassDef):
        if not self._properties:
            return

        if not any(isinstance(d, ast.Name) and d.id == "dataclass" for d in class_node.decorator_list):
            class_node.decorator_list.insert(0, ast.Name(id="dataclass", ctx=ast.Load()))

        # Remove any existing __init__ (dataclass generates it)
        class_node.body = [n for n in class_node.body if not (isinstance(n, ast.FunctionDef) and n.name == "__init__")]

        existing_anns = {
            n.target.id if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name) else None
            for n in class_node.body
        }

        insert_pos = self._last_stmt_index(class_node.body, (ast.AnnAssign,))
        if insert_pos == 0:
            insert_pos = len(class_node.body) - 1

        for prop in self._properties:
            if self._safe_member_name(prop.schema.Name) in existing_anns:
                continue
            if prop.docstring:
                doc = prop.docstring.replace("\\n", "\n")
                doc_node = ast.Expr(value=ast.Constant(value=doc))
                class_node.body.insert(len(class_node.body) - 1, doc_node)
                insert_pos += 1
                self._added_members.append(doc_node)
            ann = self._build_value_annotation(prop)
            class_node.body.insert(insert_pos, ann)
            insert_pos += 1
            self._added_members.append(ann)
            self._added_props.append(prop)
            self._changes.append(f"property annotation: {prop.schema.Name}")

    def _build_value_annotation(self, prop: PropertyBuilder) -> ast.AnnAssign:
        """Build a class-level type annotation for a ClientValue property.

        Uses the original OData property name (e.g. taskScope) rather than
        the snake_case Python name, matching the JSON serialization contract.
        """
        prop_type = prop.client_type_name
        if prop_type in TypeReferenceCollector.OPTIONAL_TYPES:
            annotation = ast.BinOp(
                left=ast.Name(id=prop_type, ctx=ast.Load()),
                op=ast.BitOr(),
                right=ast.Constant(value=None),
            )
        else:
            annotation = ast.Name(id=prop_type, ctx=ast.Load())

        if prop.is_object_type:
            # Navigation properties on ClientValue can't be instantiated
            # without context — use None as safe default
            default = ast.Constant(value=None)
            if "Optional" not in str(annotation) and prop_type not in TypeReferenceCollector.OPTIONAL_TYPES:
                # Make annotation Optional so None is valid
                annotation = ast.BinOp(
                    left=ast.Name(id=prop_type, ctx=ast.Load()),
                    op=ast.BitOr(),
                    right=ast.Constant(value=None),
                )
        else:
            default = prop.build_default_value()

            if prop.cyclic:
                # Cyclic reference: default to None (import under TYPE_CHECKING).
                default = ast.Constant(value=None)
                annotation = ast.BinOp(
                    left=ast.Name(id=prop_type, ctx=ast.Load()),
                    op=ast.BitOr(),
                    right=ast.Constant(value=None),
                )
            elif self._options and not prop.is_collection_type:
                # Resolve enum types to use first member as default instead of EnumType()
                resolved = prop.resolve_client_type()
                if resolved is not None and inspect.isclass(resolved):
                    if issubclass(resolved, Enum):
                        members = list(resolved)
                        if members:
                            default = ast.Attribute(
                                value=ast.Name(id=prop_type, ctx=ast.Load()),
                                attr=members[0].name,
                                ctx=ast.Load(),
                            )
                    elif not issubclass(resolved, ClientValue):
                        # An entity needs a context, so it cannot be a zero-arg
                        # default_factory; default to None and make it optional.
                        default = ast.Constant(value=None)
                        annotation = ast.BinOp(
                            left=ast.Name(id=prop_type, ctx=ast.Load()),
                            op=ast.BitOr(),
                            right=ast.Constant(value=None),
                        )

        if isinstance(default, ast.Call) and isinstance(default.func, ast.Name) and default.func.id == "field":
            self._uses_field = True

        return ast.AnnAssign(
            target=ast.Name(id=self._safe_member_name(prop.schema.Name), ctx=ast.Store()),
            annotation=annotation,
            value=default,
            simple=1,
        )

    @staticmethod
    def _safe_member_name(name: str) -> str:
        """A valid Python identifier for an OData field name (``class`` -> ``class_``)."""
        return f"{name}_" if keyword.iskeyword(name) else name

    def _build_object_properties(self, class_node: ast.ClassDef):
        """Build missing properties"""
        insert_pos = len(class_node.body)
        for i, node in enumerate(class_node.body):
            if isinstance(node, ast.FunctionDef) and any(
                isinstance(d, ast.Name) and d.id == "property" for d in node.decorator_list
            ):
                insert_pos = i + 1

        for prop in self._properties:
            if prop.status == "detached":
                assert self._template is not None
                property_methods = prop.build(self._template)

                for method in property_methods:
                    class_node.body.insert(insert_pos, method)
                    insert_pos += 1
                self._added_members.extend(property_methods)
                self._added_props.append(prop)
                self._changes.append(f"property: {prop.name}")

    def _generate_methods_enabled(self) -> bool:
        """Whether operation method generation is enabled via config."""
        if self._options is None:
            return False
        value = self._options.get("generate_methods", "")
        return str(value).strip().lower() in {"true", "1", "yes"}

    def _build_methods(self, class_node: ast.ClassDef) -> None:
        """Insert generated operation methods (functions/actions) that are missing."""
        if not self._methods or not self._generate_methods_enabled():
            return
        assert self._options is not None
        context_type = self._options.get("context_type", "ClientContext")
        for method in self._methods:
            if method.status == "attached":
                continue
            method_nodes = method.build(context_type)
            for node in method_nodes:
                class_node.body.append(node)
            self._added_members.extend(method_nodes)
            self._changes.append(f"method: {method.name}")

    def _build_post(self, class_node: ast.ClassDef):
        """Remove pass, insert/replace type-level description, ensure entity_type_name."""
        if self._docstring:
            doc = self._docstring.replace("\\n", "\n")
            new_stmt = ast.Expr(value=ast.Constant(value=doc))
            first = class_node.body[0] if class_node.body else None
            if (
                isinstance(first, ast.Expr)
                and isinstance(first.value, ast.Constant)
                and isinstance(first.value.value, str)
            ):
                class_node.body[0] = new_stmt
            else:
                class_node.body.insert(0, new_stmt)

        if not (self._properties or self._members or self._methods):
            return
        class_node.body = [stmt for stmt in class_node.body if not isinstance(stmt, ast.Pass)]

        self._ensure_entity_type_name(class_node)

    def render(self) -> str:
        """Return the generated module source without writing it.

        Created files are emitted from the built tree. Existing files keep their
        original source verbatim and only receive the newly added members and
        imports, so comments, ``# type: ignore`` and formatting survive.
        """
        assert self._source_tree is not None
        if self._rendered is None:
            if self._original_text is not None:
                source = self._render_update()
            else:
                ast.fix_missing_locations(self._source_tree)
                source = normalize_quotes(ast.unparse(self._source_tree))
            self._rendered = _suppress_long_imports(ruff_normalize(source, self.file))
        return self._rendered

    def _render_update(self) -> str:
        """Splice the newly built members/imports into the original source text."""
        assert self._original_text is not None
        original_tree = ast.parse(self._original_text)
        members = list(self._added_members)
        imports = list(self._added_imports)

        module_names = _module_bound_names(original_tree)
        if module_names:
            # The file binds these names as modules (``import time``); drop the
            # clashing ``from datetime import X`` and qualify generated refs.
            imports = _strip_module_names(imports, module_names)
            if "datetime" in module_names:
                qualifier = "datetime"
            else:
                qualifier = "_dt"
                imports = [*imports, ast.Import(names=[ast.alias(name="datetime", asname="_dt")])]
            members = [_qualify_modules(node, module_names, qualifier) for node in members]

        runtime_lines: list[str] = []
        type_checking_lines: list[str] = []
        for imp in imports:
            if isinstance(imp, ast.If) and _is_type_checking(imp):
                type_checking_lines.extend(ast.unparse(stmt) for stmt in imp.body)
            else:
                runtime_lines.append(ast.unparse(imp))

        lines = self._original_text.splitlines()
        class_end = self._class_body_end_line(original_tree, self.client_type_name)
        runtime_insert = self._last_runtime_import_line(original_tree)
        tc_block = self._find_type_checking_block(original_tree)

        # Insert from the bottom up so earlier line numbers stay valid.
        if members:
            pass_line = self._sole_pass_line(original_tree, self.client_type_name)
            if pass_line is not None:
                del lines[pass_line - 1]
                class_end -= 1
            body = "\n\n".join(self._render_member(node) for node in members)
            lines[class_end:class_end] = ["", *body.splitlines()]
            if self._schema.BaseTypeFullName == "ComplexType":
                class_line = self._class_line(original_tree, self.client_type_name)
                if class_line is not None and not self._has_dataclass_decorator(original_tree, self.client_type_name):
                    lines.insert(class_line, "@dataclass")

        if type_checking_lines:
            if tc_block is not None:
                lines[tc_block.end_lineno : tc_block.end_lineno] = ["    " + line for line in type_checking_lines]
            else:
                block = ["if TYPE_CHECKING:", *("    " + line for line in type_checking_lines)]
                lines[runtime_insert:runtime_insert] = block

        if runtime_lines:
            lines[runtime_insert:runtime_insert] = runtime_lines

        if members and not _has_future_annotations(original_tree):
            # PEP 585 annotations (list[X]) need the future import on the py38 target.
            lines[0:0] = ["from __future__ import annotations", ""]

        return "\n".join(lines) + ("\n" if self._original_text.endswith("\n") else "")

    @staticmethod
    def _render_member(node: ast.stmt) -> str:
        module = ast.Module(body=[node], type_ignores=[])
        ast.fix_missing_locations(module)
        code = normalize_quotes(ast.unparse(module))
        return "\n".join("    " + line if line.strip() else line for line in code.splitlines())

    @staticmethod
    def _class_line(tree: ast.Module, class_name: str) -> Optional[int]:
        """0-based line index of the ``class <name>`` statement."""
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                return node.lineno - 1
        return None

    @staticmethod
    def _has_dataclass_decorator(tree: ast.Module, class_name: str) -> bool:
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                return any(isinstance(d, ast.Name) and d.id == "dataclass" for d in node.decorator_list)
        return False

    @staticmethod
    def _sole_pass_line(tree: ast.Module, class_name: str) -> Optional[int]:
        """Line of a ``pass`` that is the only statement in the target class body."""
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                    return node.body[0].lineno
        return None

    @staticmethod
    def _class_body_end_line(tree: ast.Module, class_name: str) -> int:
        """End line of the target class body (a module may hold several classes)."""
        first: Optional[ast.ClassDef] = None
        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            if first is None:
                first = node
            if node.name == class_name:
                last = node.body[-1]
                return last.end_lineno or last.lineno
        if first is not None:
            last = first.body[-1]
            return last.end_lineno or last.lineno
        return len(tree.body)

    @staticmethod
    def _last_runtime_import_line(tree: ast.Module) -> int:
        line = 0
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                line = node.end_lineno or line
        return line

    @staticmethod
    def _find_type_checking_block(tree: ast.Module) -> Optional[ast.If]:
        for node in tree.body:
            if isinstance(node, ast.If) and _is_type_checking(node):
                return node
        return None

    @staticmethod
    def _uses_module_datetime(tree: ast.Module) -> bool:
        return bool(_module_bound_names(tree))

    def save(self):
        code = self.render()

        os.makedirs(os.path.dirname(self.file) or ".", exist_ok=True)
        with open(self.file, "w", encoding="utf-8") as f:
            f.write(code)

    @staticmethod
    def _build_type_name_property(full_name: str) -> ast.FunctionDef:
        """Build the entity_type_name @property method."""
        return ast.FunctionDef(
            name="entity_type_name",
            args=ast.arguments(
                posonlyargs=[],
                args=[ast.arg(arg="self")],
                vararg=None,
                kwonlyargs=[],
                kw_defaults=[],
                kwarg=None,
                defaults=[],
            ),
            body=[ast.Return(value=ast.Constant(value=full_name))],
            decorator_list=[ast.Name(id="property", ctx=ast.Load())],
            returns=ast.Name(id="str", ctx=ast.Load()),
        )

    def _ensure_entity_type_name(self, class_node: ast.ClassDef):
        """Ensure the class has an entity_type_name property that returns the correct type name"""

        if self._schema.BaseTypeFullName not in [
            "ComplexType",
            "EntityType",
            "EnumType",
        ]:
            return

        parts = self._schema.FullName.split(".")
        MIN_NAME_PARTS = 2
        if len(parts) <= MIN_NAME_PARTS:
            return

        if not self._entity_type_name_exists:
            entity_type_name_method = self._build_type_name_property(self._schema.FullName)
            class_node.body.insert(self._type_name_property_index(class_node), entity_type_name_method)
            self._added_members.append(entity_type_name_method)
            self._changes.append("entity_type_name property")

    @staticmethod
    def _type_name_property_index(class_node: ast.ClassDef) -> int:
        """Where to put ``entity_type_name`` — before a member named ``property``.

        A dataclass field named ``property`` shadows the builtin decorator, so the
        ``@property`` method must be defined first (kept after any docstring).
        """
        shadows = any(
            (isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name) and stmt.target.id == "property")
            or (
                isinstance(stmt, ast.Assign)
                and any(isinstance(target, ast.Name) and target.id == "property" for target in stmt.targets)
            )
            for stmt in class_node.body
        )
        if not shadows:
            return len(class_node.body)
        first = class_node.body[0] if class_node.body else None
        if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
            return 1
        return 0

    @staticmethod
    def _last_stmt_index(nodes: list, types: tuple) -> int:
        """Return index after the last node matching one of the given types."""
        pos = 0
        for i, node in enumerate(nodes):
            if isinstance(node, types):
                pos = i + 1
        return pos

    @staticmethod
    def _to_snake_case(name: str) -> str:
        """Convert PascalCase or UpperCamelCase to snake_case."""
        return to_snake_case(name, avoid_keywords=False)

    @staticmethod
    def _module_file(module_name: str) -> Optional[str]:
        """The source file for a module, resolved without executing it."""
        try:
            spec = importlib.util.find_spec(module_name)
        except (ImportError, ValueError):
            return None
        origin = getattr(spec, "origin", None)
        return origin if origin and origin.endswith(".py") else None

    def _resolve_type(self) -> Dict[str, str]:
        type_info: Dict[str, str] = {}

        assert self._options is not None
        module_name = self._resolver.strict_module_for(self._schema.FullName)
        origin = self._module_file(module_name) if module_name else None
        if origin is not None:
            type_info["state"] = "attached"
            type_info["file"] = origin
            type_info["routed"] = "1"
        else:
            namespace = ".".join(self._schema.FullName.split(".")[:-1])
            module_path = Router.from_options(self._options).module_for(self._schema.FullName)
            output_base = self._options.get("output_path", self._options.get("outputpath", ""))
            if module_path:
                if module_path.startswith("office365."):
                    relative_path = module_path[len("office365.") :]
                else:
                    relative_path = module_path
                sub_dir = relative_path.replace(".", "/")
                parts = [output_base]
                if sub_dir not in ("", "."):
                    base_suffix = output_base.rstrip("/").rsplit("/", 1)[-1]
                    if sub_dir != base_suffix:
                        parts.append(sub_dir)
                parts.append(self._to_snake_case(self.client_type_name) + ".py")
                file_path = abspath(os.path.join(*parts))
            else:
                file_path = abspath(os.path.join(output_base, self._to_snake_case(self.client_type_name) + ".py"))
            type_info["file"] = file_path
            type_info["routed"] = "1" if module_path else ""
            if not module_path:
                type_info["state"] = "detached"
                type_info["reason"] = f"no routing entry for namespace '{namespace}'"
            elif os.path.exists(file_path):
                # The routed file already exists but strict name resolution missed it
                # (metadata/model name drift). Update it in place when the class matches;
                # never overwrite a foreign file.
                if self._file_defines_class(file_path, self.client_type_name):
                    type_info["state"] = "attached"
                else:
                    type_info["state"] = "detached"
                    type_info["routed"] = ""
                    type_info["reason"] = f"target file exists without class '{self.client_type_name}'"
            else:
                type_info["state"] = "detached"
        return type_info

    @staticmethod
    def _file_defines_class(path: str, class_name: str) -> bool:
        try:
            with open(path, encoding="utf-8") as f:
                tree = ast.parse(f.read())
        except (OSError, SyntaxError):
            return False
        return any(isinstance(node, ast.ClassDef) and node.name == class_name for node in tree.body)

    @property
    def skip_reason(self) -> str:
        """Why this type cannot be generated, or ``""`` when it can."""
        return self._ensure_type_info().get("reason", "")

    def _ensure_type_info(self):
        if self._type_info is None:
            self._type_info = self._resolve_type()
        assert self._type_info is not None
        return self._type_info

    @property
    def state(self):
        return self._ensure_type_info()["state"]

    @property
    def routed(self) -> bool:
        """Whether a new (detached) type maps to a routed package (not the output root)."""
        return bool(self._ensure_type_info().get("routed"))

    @property
    def file(self):
        return self._ensure_type_info()["file"]

    @property
    def status(self):
        return self._status

    @property
    def client_type_name(self):
        return python_name(self._schema.FullName, self._schema.IsValueObject or False)

    @property
    def properties(self) -> List[PropertyBuilder]:
        return self._properties

    @property
    def members(self) -> List[MemberBuilder]:
        return self._members

    @property
    def entity_type_name(self) -> str:
        return self._schema.FullName
