import ast
import importlib.util
import inspect
import keyword
import os
from _ast import Module
from enum import Enum
from typing import Dict, List, Optional

from office365.runtime.client_object import ClientObject
from office365.runtime.client_value import ClientValue
from typing_extensions import Self

from generator.builders.collector import TypeReferenceCollector
from generator.builders.context import BuilderContext
from generator.builders.imports import (
    class_name_collides_with_import,
    drop_unused_type_checking,
    existing_import_names,
    install_imports,
)
from generator.builders.member import MemberBuilder
from generator.builders.method import MethodBuilder
from generator.builders.naming import python_name, to_snake_case
from generator.builders.placement import Placement, TypePlanner
from generator.builders.property import PropertyBuilder
from generator.builders.render import normalize_quotes, ruff_normalize
from generator.builders.resolution import TypeRegistry
from generator.builders.source_editor import SourceEditor, suppress_long_lines
from generator.builders.template_context import TemplateContext
from generator.documentation.base import DocumentationProvider
from generator.odata.type_information import TypeInformation
from generator.odata.type_system import TypeRef
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
        self._context = BuilderContext.from_options(options)
        self._docs_service = docs_service
        self._template: Optional[TemplateContext] = None
        self._placement: Optional[Placement] = None
        self._source_tree: Optional[Module] = None
        self._status: Optional[str] = None
        self._properties: List[PropertyBuilder] = []
        self._members: List[MemberBuilder] = []
        self._methods: List[MethodBuilder] = []
        self._changes: List[str] = []
        self._docstring: Optional[str] = None
        self._entity_type_name_exists: bool = False
        self._known_types: set[str] = set(self._context.known_types)
        self._original_text: Optional[str] = None
        self._added_members: List[ast.stmt] = []
        self._added_imports: List[ast.stmt] = []
        self._rendered: Optional[str] = None
        self._uses_field = False
        self._field_alias = "field"
        self._added_props: List[PropertyBuilder] = []
        self._cyclic_types: set[str] = set(self._context.cyclic_types)
        #: OData enum name -> first member name (for defaults on planned enums).
        self._enum_defaults: dict[str, str] = dict(self._context.enum_defaults)
        self._resolver = resolver or TypeRegistry(
            self._context.modules.split(","),
            namespace=self._context.namespace,
            type_modules=self._context.type_modules,
        )
        self._planner = TypePlanner(self._context, self._resolver)

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
        if self._docs_service:
            self._docs_service.build_documentation(self)
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
        reserved_props = self._reserved_names(_RESERVED_PROPERTY_NAMES)
        ignored_properties = set(self._context.ignored_properties)
        self._properties = []
        seen_props: set[str] = set()
        if any(name == "field" for name in self._schema.Properties):
            # A dataclass field named ``field`` would shadow ``dataclasses.field``
            # used by later fields, so import it under an alias instead.
            self._field_alias = "field_"
        for name, prop_schema in self._schema.Properties.items():
            snake = to_snake_case(name)
            if name in ignored_properties or snake in reserved_props or snake in seen_props:
                continue
            if not self._is_resolvable(prop_schema.TypeName):
                continue
            self._properties.append(PropertyBuilder(prop_schema, resolver=self._resolver))
            self._properties[-1].cyclic = prop_schema.type_ref.text in self._cyclic_types
            self._properties[-1].field_alias = self._field_alias
            seen_props.add(snake)

        self._members = [MemberBuilder(member_schema) for _, member_schema in self._schema.Members.items()]

        ignored_methods = set(self._context.ignored_methods)
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
        ref = TypeRef.of(type_name)
        if ref.is_collection:
            return self._is_resolvable(ref.text)
        if ref.is_primitive:
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

    def _reserved_names(self, base: set[str]) -> set[str]:
        """Base names plus every member the existing class already declares (incl. inherited).

        Only for **attached** types: a new type has no existing class, and
        resolving its members by bare name could pick a same-named unrelated
        class and wrongly reserve its member names (a one-run convergence bug).
        """
        if not self._ensure_placement().is_attached:
            return set(base)
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
        self._template = TemplateContext(self._context.template_path, self._schema)

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

        if self._status in {"created", "updated"} and class_name_collides_with_import(
            self._source_tree, self.client_type_name
        ):
            print(f"  Skipping {self.client_type_name}: name collides with an imported type")
            self._status = None

        if self._status == "updated" and len(self._changes) == 0:
            self._status = None
        return self

    def _build_imports(self, module: ast.Module) -> None:
        """Insert the imports the added members need (deduplicated)."""
        assert self._template is not None
        collector = TypeReferenceCollector(self._resolver)
        collector.needs_dataclass = self._schema.BaseTypeFullName == "ComplexType" and bool(self._added_props)
        collector.needs_field = self._uses_field
        collector.field_alias = self._field_alias

        for prop in self._added_props:
            prop_type = prop.client_type_name
            if (
                prop_type in TypeReferenceCollector.OPTIONAL_TYPES or prop.has_optional_getter()
            ) and not collector.needs_dataclass:
                # Getters use ``Optional[X]``; dataclass fields use ``X | None``.
                collector.add("Optional")
            collector.add(prop_type)
            collector.add_custom(prop)
            if prop.is_object_type:
                collector.add_object_type(prop)

        if self._generate_methods_enabled():
            for method in self._methods:
                if method.status != "attached":
                    collector.add_method(method, self._context.context_type)

        existing = existing_import_names(module)
        insert_index = len([n for n in module.body if isinstance(n, (ast.Import, ast.ImportFrom))])
        self._added_imports.extend(
            install_imports(module, self._template.build_references(collector), existing, insert_index)
        )
        self._added_imports = drop_unused_type_checking(module, self._added_imports)

    def _build_members(self, class_node: ast.ClassDef):
        if not self._members:
            return

        assert self._template is not None
        existing_members = self._template.get_existing_members(class_node)

        insert_pos = self._last_stmt_index(class_node.body, (ast.Assign,))
        existing_values = self._existing_member_values(class_node)

        for member_builder in self._members:
            if member_builder.name in existing_members:
                continue
            value_key = str(member_builder.value)
            if value_key in existing_values:
                # A distinct name with an already-used value is a Python Enum alias;
                # emitting it trips ruff PIE796, so keep the canonical member only.
                existing_members.add(member_builder.name)
                continue
            assert self._template is not None
            member_nodes = member_builder.build(self._template)
            for node in member_nodes:
                class_node.body.insert(insert_pos, node)
                insert_pos += 1
            self._added_members.extend(member_nodes)
            self._changes.append(f"member: {member_builder.name}")
            existing_members.add(member_builder.name)
            existing_values.add(value_key)

    @staticmethod
    def _existing_member_values(class_node: ast.ClassDef) -> set[str]:
        """String values already assigned in the class body (enum members)."""
        values: set[str] = set()
        for stmt in class_node.body:
            if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 and isinstance(stmt.value, ast.Constant):
                values.add(str(stmt.value.value))
        return values

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
        optional = prop_type in TypeReferenceCollector.OPTIONAL_TYPES
        annotation = self._optional(prop_type) if optional else ast.Name(id=prop_type, ctx=ast.Load())

        if prop.is_object_type:
            # Navigation properties on ClientValue can't be instantiated
            # without context — use None as safe default
            default = ast.Constant(value=None)
            if not optional:
                annotation = self._optional(prop_type)
        elif prop.cyclic:
            # Cyclic reference: default to None (import under TYPE_CHECKING).
            default = ast.Constant(value=None)
            annotation = self._optional(prop_type)
        else:
            default, annotation = self._value_default(prop, prop_type, annotation)

        if isinstance(default, ast.Call) and isinstance(default.func, ast.Name) and default.func.id == self._field_alias:
            self._uses_field = True

        return ast.AnnAssign(
            target=ast.Name(id=self._safe_member_name(prop.schema.Name), ctx=ast.Store()),
            annotation=annotation,
            value=default,
            simple=1,
        )

    @staticmethod
    def _optional(prop_type: str) -> ast.expr:
        """The ``prop_type | None`` annotation."""
        return ast.BinOp(
            left=ast.Name(id=prop_type, ctx=ast.Load()),
            op=ast.BitOr(),
            right=ast.Constant(value=None),
        )

    def _value_default(self, prop: PropertyBuilder, prop_type: str, annotation: ast.expr) -> tuple[ast.expr, ast.expr]:
        """The default value and annotation for a non-object ClientValue field.

        Enums default to their first member (never ``field(default_factory=Enum)``),
        entities to ``None``; an enum planned in this run is not importable yet, so
        its first member is read from the metadata.
        """
        default: ast.expr = prop.build_default_value()
        make_optional = False
        if not prop.is_collection_type:
            resolved = prop.resolve_client_type()
            if resolved is not None and inspect.isclass(resolved):
                if issubclass(resolved, Enum):
                    members = list(resolved)
                    if members:
                        default = self._member_attr(prop_type, members[0].name)
                    else:
                        default, make_optional = ast.Constant(value=None), True
                elif not issubclass(resolved, ClientValue):
                    # An entity needs a context, so it cannot be a zero-arg default.
                    default, make_optional = ast.Constant(value=None), True
            else:
                enum_name = prop.type_ref.text
                member = self._enum_defaults.get(enum_name)
                if member:
                    default = self._member_attr(prop_type, member)
                elif enum_name in self._enum_defaults:
                    default, make_optional = ast.Constant(value=None), True
        return default, (self._optional(prop_type) if make_optional else annotation)

    @staticmethod
    def _member_attr(prop_type: str, member: str) -> ast.expr:
        """The ``EnumType.member`` expression used as an enum default."""
        return ast.Attribute(
            value=ast.Name(id=prop_type, ctx=ast.Load()),
            attr=member,
            ctx=ast.Load(),
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
        return self._context.methods_enabled

    def _build_methods(self, class_node: ast.ClassDef) -> None:
        """Insert generated operation methods (functions/actions) that are missing."""
        if not self._methods or not self._generate_methods_enabled():
            return
        context_type = self._context.context_type
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
            self._rendered = suppress_long_lines(ruff_normalize(source, self.file))
        return self._rendered

    def _render_update(self) -> str:
        """Splice the newly built members/imports into the original source text."""
        assert self._original_text is not None
        editor = SourceEditor(self._original_text, self.client_type_name)
        add_dataclass = self._schema.BaseTypeFullName == "ComplexType"
        return editor.splice(self._added_members, self._added_imports, add_dataclass=add_dataclass)

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

    @property
    def skip_reason(self) -> str:
        """Why this type cannot be generated, or ``""`` when it can."""
        return self._ensure_placement().reason

    def _ensure_placement(self) -> Placement:
        if self._placement is None:
            self._placement = self._planner.plan(self._schema.FullName, self._schema.IsValueObject or False)
        return self._placement

    @property
    def state(self):
        return self._ensure_placement().state

    @property
    def routed(self) -> bool:
        """Whether a new (detached) type maps to a routed package (not the output root)."""
        return self._ensure_placement().routed

    @property
    def file(self):
        return self._ensure_placement().file

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
