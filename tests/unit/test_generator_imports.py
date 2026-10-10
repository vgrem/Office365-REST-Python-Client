"""Offline tests for generated imports (navigation types, TYPE_CHECKING, cycles)."""

from __future__ import annotations

import ast
from pathlib import Path

from generator.builders.type import TypeBuilder
from generator.odata.method import MethodInformation
from generator.odata.property import PropertyInformation
from generator.odata.type_information import TypeInformation

_TEMPLATES = Path(__file__).resolve().parents[2] / "generator" / "templates" / "sharepoint"
_TEMPLATES_GRAPH = Path(__file__).resolve().parents[2] / "generator" / "templates" / "graph"


class _FixedResolver:
    """Resolves every type to one module (for import-placement tests)."""

    def __init__(self, module: str) -> None:
        self._module = module

    def resolve(self, type_name):
        return None

    def module_for(self, type_name):
        return self._module

    def strict_module_for(self, type_name):
        return self._module

    def members_of(self, type_name):
        return set()


def _build_navigation_type(tmp_path: Path) -> str:
    schema = TypeInformation(BaseTypeFullName="EntityType", FullName="SP.TestFile", IsValueObject=False)
    schema.add_property(PropertyInformation(Name="Web", TypeName="SP.Web", IsNavigation=True))
    schema.add_property(PropertyInformation(Name="Versions", TypeName="Collection(SP.FileVersion)", IsNavigation=True))
    options = {"template_path": str(_TEMPLATES), "output_path": str(tmp_path), "modules": "office365.sharepoint"}
    builder = TypeBuilder(schema, options)
    builder.build()
    builder.save()
    return Path(builder.file).read_text(encoding="utf8")


def test_navigation_types_are_imported_lazily_and_under_type_checking(tmp_path: Path):
    source = _build_navigation_type(tmp_path)
    ast.parse(source)  # must be valid Python

    # annotation imports live under TYPE_CHECKING
    assert "if TYPE_CHECKING:" in source
    # runtime import inside the getter (module-level would cycle)
    assert "from office365.sharepoint.webs.web import Web" in source
    assert "from office365.sharepoint.files.versions.version import FileVersion" in source
    # both the annotation (TYPE_CHECKING) and the getter (local)
    assert source.count("from office365.sharepoint.webs.web import Web") == 2  # noqa: PLR2004

    # EntityCollection resolves to the SharePoint module, not the Graph one
    assert "from office365.sharepoint.entity_collection import EntityCollection" in source
    assert "from office365.entity_collection import EntityCollection" not in source


def test_complex_value_collection_does_not_emit_bracketed_import(tmp_path: Path):
    """A ClientValue collection imports the wrapper and item type, not ``CVC[X]``."""
    schema = TypeInformation(BaseTypeFullName="EntityType", FullName="SP.TestThing", IsValueObject=False)
    schema.add_property(PropertyInformation(Name="Entries", TypeName="Collection(SP.ResourceEntry)"))
    options = {"template_path": str(_TEMPLATES), "output_path": str(tmp_path), "modules": "office365.sharepoint"}
    builder = TypeBuilder(schema, options)
    builder.build()
    source = builder.render()
    ast.parse(source)
    assert [line for line in source.splitlines() if line.startswith("from ") and "[" in line] == []


def test_client_value_field_type_is_a_runtime_import(tmp_path: Path):
    """A dataclass field's ``default_factory=X`` needs X at runtime, not only under TYPE_CHECKING."""
    schema = TypeInformation(BaseTypeFullName="ComplexType", FullName="microsoft.graph.TestValue", IsValueObject=True)
    schema.add_property(PropertyInformation(Name="Subject", TypeName="microsoft.graph.WorkflowSubject"))
    options = {"template_path": str(_TEMPLATES_GRAPH), "output_path": str(tmp_path), "modules": "office365"}
    builder = TypeBuilder(schema, options, resolver=_FixedResolver("office365.workflow_subject"))
    builder.build()
    source = builder.render()
    ast.parse(source)

    lines = source.splitlines()
    import_line = "from office365.workflow_subject import WorkflowSubject"
    runtime_index = lines.index(import_line)
    type_checking_index = next((i for i, line in enumerate(lines) if line.startswith("if TYPE_CHECKING:")), len(lines))
    assert runtime_index < type_checking_index  # module-level, before the TYPE_CHECKING block


def test_method_entity_return_is_imported_lazily(tmp_path: Path):
    """A bound function returning an entity imports it under TYPE_CHECKING + locally."""
    schema = TypeInformation(BaseTypeFullName="EntityType", FullName="SP.TestThing", IsValueObject=False)
    schema.add_method(
        MethodInformation(
            Name="GetWeb",
            ReturnTypeFullName="SP.Web",
            BindingTypeFullName="SP.TestThing",
            IsBound=True,
            IsStatic=False,
            Kind="function",
        )
    )
    options = {
        "template_path": str(_TEMPLATES),
        "output_path": str(tmp_path),
        "modules": "office365.sharepoint",
        "generate_methods": "true",
    }
    builder = TypeBuilder(schema, options)
    builder.build()
    source = builder.render()
    ast.parse(source)
    assert "def get_web" in source
    assert source.count("from office365.sharepoint.webs.web import Web") == 2  # noqa: PLR2004
