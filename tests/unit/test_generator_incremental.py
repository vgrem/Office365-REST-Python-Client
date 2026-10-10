"""Offline tests for incremental/idempotent generation and class invariants."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest
from generator.builders.type import TypeBuilder, _qualify_datetime
from generator.builders.type_registry import TypeRegistry
from generator.odata.method import MethodInformation
from generator.odata.property import PropertyInformation
from generator.odata.type_information import TypeInformation
from generator.validation import ValidationError

_TEMPLATES = Path(__file__).resolve().parents[2] / "generator" / "templates" / "sharepoint"


class _StubResolver:
    """Marks the type attached and reports its existing members (no real index)."""

    def __init__(self, module: str = "stub.module", members: set[str] | None = None) -> None:
        self._module = module
        self._members = members or set()

    def resolve(self, type_name):
        return None

    def module_for(self, type_name):
        return self._module

    def strict_module_for(self, type_name):
        return self._module

    def members_of(self, type_name):
        return set(self._members)


def _schema() -> TypeInformation:
    schema = TypeInformation(BaseTypeFullName="EntityType", FullName="SP.TestThing", IsValueObject=False)
    schema.add_property(PropertyInformation(Name="Title", TypeName="Edm.String"))
    return schema


def _options(tmp_path: Path) -> dict:
    return {"template_path": str(_TEMPLATES), "output_path": str(tmp_path), "modules": "office365.sharepoint"}


def test_build_is_idempotent(tmp_path: Path, monkeypatch):
    """A second run over an already-generated class produces no change."""
    target = tmp_path / "test_thing.py"
    target.write_text("class TestThing:\n    pass\n", encoding="utf8")
    monkeypatch.setattr(TypeBuilder, "_module_file", staticmethod(lambda name: str(target)))

    first = TypeBuilder(_schema(), _options(tmp_path), resolver=_StubResolver())
    first.build()
    first.save()
    assert "def title" in target.read_text(encoding="utf8")

    second = TypeBuilder(_schema(), _options(tmp_path), resolver=_StubResolver())
    second.build()
    assert second.status is None  # nothing left to add
    assert second.render() == target.read_text(encoding="utf8")


def test_inherited_members_are_not_redeclared(tmp_path: Path, monkeypatch):
    """A property already present on the base class is skipped."""
    target = tmp_path / "test_thing.py"
    target.write_text("class TestThing:\n    pass\n", encoding="utf8")
    monkeypatch.setattr(TypeBuilder, "_module_file", staticmethod(lambda name: str(target)))

    # ``title`` is reported as already existing (e.g. inherited) -> not generated
    builder = TypeBuilder(_schema(), _options(tmp_path), resolver=_StubResolver(members={"title"}))
    builder.build()
    assert builder.status is None


def test_rejects_duplicate_top_level_class():
    builder = TypeBuilder(_schema(), {"modules": "office365.sharepoint"}, resolver=_StubResolver())
    builder._type_info = {"state": "attached", "file": "x.py"}
    module = ast.parse("class TestThing:\n    pass\n\n\nclass TestThing:\n    pass\n")
    with pytest.raises(ValidationError):
        builder._process(module)


def test_static_members_include_inherited_members():
    resolver = TypeRegistry(["office365.sharepoint"])
    members = resolver.members_of("SP.File")
    assert {"name", "server_relative_url", "length", "versions"} <= members


def test_strict_module_resolution_ignores_same_named_types():
    """Two OData types sharing a short name must not resolve to each other's file."""
    resolver = TypeRegistry(["office365.sharepoint"])
    portal = resolver.strict_module_for("Microsoft.SharePoint.Portal.GroupCreationParams")
    tenant = resolver.strict_module_for("Microsoft.Online.SharePoint.TenantManagement.GroupCreationParams")
    assert portal == "office365.sharepoint.portal.groups.creation_params"
    assert tenant != portal  # a same-named type must not resolve to the portal file


def test_property_and_method_with_same_name_are_deduplicated(tmp_path: Path):
    """An OData property and bound function sharing a name generate one member."""
    schema = TypeInformation(BaseTypeFullName="EntityType", FullName="SP.TestThing", IsValueObject=False)
    schema.add_property(PropertyInformation(Name="Settings", TypeName="Edm.String"))
    schema.add_method(
        MethodInformation(
            Name="Settings",
            ReturnTypeFullName="Edm.String",
            IsBound=True,
            IsStatic=False,
            Kind="function",
        )
    )
    options = {**_options(tmp_path), "generate_methods": "true"}
    builder = TypeBuilder(schema, options, resolver=_StubResolver())
    builder.build()
    source = builder.render()
    ast.parse(source)
    assert source.count("def settings") == 1


def test_keyword_field_names_are_sanitized(tmp_path: Path):
    """OData fields that are Python keywords get a trailing underscore."""
    schema = TypeInformation(BaseTypeFullName="ComplexType", FullName="microsoft.graph.TestValue", IsValueObject=True)
    schema.add_property(PropertyInformation(Name="class", TypeName="Edm.String"))
    schema.add_property(PropertyInformation(Name="from", TypeName="Edm.String"))
    builder = TypeBuilder(schema, _options(tmp_path), resolver=_StubResolver())
    builder.build()
    source = builder.render()
    ast.parse(source)
    assert "class_: str | None" in source
    assert "from_: str | None" in source


def test_update_preserves_existing_source(tmp_path: Path, monkeypatch):
    """Updating a file only appends new members; comments and ignores survive."""
    target = tmp_path / "test_thing.py"
    target.write_text(
        "from __future__ import annotations\n"
        "\n"
        "\n"
        "class TestThing:\n"
        "    # keep me\n"
        "    def existing(self) -> None:  # type: ignore[misc]\n"
        "        pass\n",
        encoding="utf8",
    )
    monkeypatch.setattr(TypeBuilder, "_module_file", staticmethod(lambda name: str(target)))
    builder = TypeBuilder(_schema(), _options(tmp_path), resolver=_StubResolver())
    builder.build()
    source = builder.render()

    assert builder.status == "updated"
    assert "# keep me" in source
    assert "# type: ignore[misc]" in source
    assert "def title" in source
    # render() must not mutate the built nodes (it runs for validation and save)
    assert source == builder.render()


def _is_subsequence(needle: list[str], haystack: list[str]) -> bool:
    remaining = iter(haystack)
    return all(any(candidate == line for candidate in remaining) for line in needle)


def test_update_never_removes_or_reflows_existing_lines(tmp_path: Path, monkeypatch):
    """Additions-only guarantee: every original line survives verbatim, in order."""
    target = tmp_path / "test_thing.py"
    original = (
        "from __future__ import annotations\n"
        "\n"
        "\n"
        "class TestThing:\n"
        "    # custom logic below (not in metadata)\n"
        "    def custom(self) -> int:  # type: ignore[override]\n"
        "        return 42\n"
    )
    target.write_text(original, encoding="utf8")
    monkeypatch.setattr(TypeBuilder, "_module_file", staticmethod(lambda name: str(target)))
    builder = TypeBuilder(_schema(), _options(tmp_path), resolver=_StubResolver())
    builder.build()
    source = builder.render()

    assert _is_subsequence(original.splitlines(), source.splitlines())
    assert "return 42" in source
    assert "def title" in source


def test_datetime_references_use_the_module_form():
    """When a file uses ``import datetime``, generated refs become ``datetime.datetime``."""
    node = ast.parse("def f(x: datetime) -> None: ...").body[0]
    assert "datetime.datetime" in ast.unparse(_qualify_datetime(node))


def test_update_targets_the_named_class_in_a_multi_class_module(tmp_path: Path, monkeypatch):
    """A helper class declared before the target must not receive the new members."""
    target = tmp_path / "multi.py"
    target.write_text(
        "from __future__ import annotations\n"
        "\n"
        "\n"
        "class Helper:\n"
        "    pass\n"
        "\n"
        "\n"
        "class TestThing:\n"
        "    def existing(self) -> None:\n"
        "        pass\n",
        encoding="utf8",
    )
    monkeypatch.setattr(TypeBuilder, "_module_file", staticmethod(lambda name: str(target)))
    builder = TypeBuilder(_schema(), _options(tmp_path), resolver=_StubResolver())
    builder.build()
    tree = ast.parse(builder.render())
    classes = {node.name: node for node in tree.body if isinstance(node, ast.ClassDef)}
    helper_members = [m.name for m in classes["Helper"].body if isinstance(m, ast.FunctionDef)]
    target_members = [m.name for m in classes["TestThing"].body if isinstance(m, ast.FunctionDef)]
    assert "title" in target_members
    assert "title" not in helper_members
