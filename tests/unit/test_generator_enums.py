"""Offline tests for enum generation (member names, aliases, field defaults)."""

from __future__ import annotations

import ast
from pathlib import Path

from generator.builders.member import sanitize_member_name
from generator.builders.type import TypeBuilder
from generator.odata.member import MemberInformation
from generator.odata.property import PropertyInformation
from generator.odata.type_information import TypeInformation

_TEMPLATES = Path(__file__).resolve().parents[2] / "generator" / "templates" / "graph"


class _NullResolver:
    def resolve(self, type_name):
        return None

    def module_for(self, type_name):
        return None

    def strict_module_for(self, type_name, kind=None):
        return None

    def members_of(self, type_name):
        return set()


class _PlannedEnumResolver(_NullResolver):
    """Resolves the planned enum to a module (as the pipeline's plan does)."""

    def module_for(self, type_name):
        return "office365.test_enum" if type_name == "microsoft.graph.TestEnum" else None


def _enum_schema(*members: tuple[str, str]) -> TypeInformation:
    schema = TypeInformation(BaseTypeFullName="EnumType", FullName="microsoft.graph.TestEnum")
    for name, value in members:
        schema.add_member(MemberInformation(Name=name, Value=value))
    return schema


def _build_enum(tmp_path: Path, schema: TypeInformation) -> str:
    options = {"template_path": str(_TEMPLATES), "output_path": str(tmp_path), "modules": "office365"}
    builder = TypeBuilder(schema, options, resolver=_NullResolver())
    builder.build()
    source = builder.render()
    ast.parse(source)
    return source


def test_sanitize_member_name_avoids_keywords_and_ambiguous_letters() -> None:
    assert sanitize_member_name("active") == "active"
    assert sanitize_member_name("class") == "class_"
    assert sanitize_member_name("l") == "l_"
    assert sanitize_member_name("I") == "I_"


def test_duplicate_enum_value_is_skipped(tmp_path: Path) -> None:
    source = _build_enum(tmp_path, _enum_schema(("a", "1"), ("b", "1"), ("c", "2")))

    assert 'a = "1"' in source
    assert 'c = "2"' in source
    assert "b = " not in source  # duplicate value -> Python alias, trips PIE796


def test_ambiguous_enum_member_is_renamed(tmp_path: Path) -> None:
    source = _build_enum(tmp_path, _enum_schema(("l", "1"), ("m", "2")))

    assert 'l_ = "1"' in source
    assert "\n    l = " not in source


def test_planned_enum_field_defaults_to_first_member(tmp_path: Path) -> None:
    schema = TypeInformation(BaseTypeFullName="ComplexType", FullName="microsoft.graph.TestValue", IsValueObject=True)
    schema.add_property(PropertyInformation(Name="status", TypeName="microsoft.graph.TestEnum"))
    options = {
        "template_path": str(_TEMPLATES),
        "output_path": str(tmp_path),
        "modules": "office365",
        # The enum is planned in this run (not importable yet): default from metadata.
        "enum_defaults": {"microsoft.graph.TestEnum": "active"},
    }
    builder = TypeBuilder(schema, options, resolver=_PlannedEnumResolver())
    builder.build()
    source = builder.render()
    ast.parse(source)

    assert "status: TestEnum = TestEnum.active" in source
    assert "default_factory=TestEnum" not in source
