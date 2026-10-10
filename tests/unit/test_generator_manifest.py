"""Offline tests for the run manifest and metadata-deletion tracking."""

from __future__ import annotations

from generator.manifest import Manifest, MetadataChanges, diff_members, schema_members
from generator.odata.member import MemberInformation
from generator.odata.method import MethodInformation
from generator.odata.model import ODataModel
from generator.odata.property import PropertyInformation
from generator.odata.type_information import TypeInformation


def test_diff_members_reports_removed_types_and_members():
    previous = {"microsoft.graph.Foo": ["a", "b", "c"], "microsoft.graph.Gone": ["x"]}
    current = {"microsoft.graph.Foo": ["a", "c", "d"]}

    changes = diff_members(previous, current)

    assert changes.removed_types == ["microsoft.graph.Gone"]
    assert changes.removed_members == {"microsoft.graph.Foo": ["b"]}
    assert not changes.is_empty


def test_diff_members_empty_when_nothing_removed():
    members = {"microsoft.graph.Foo": ["a"]}
    assert diff_members(members, members).is_empty
    assert MetadataChanges([], {}).is_empty


def test_schema_members_collects_properties_methods_and_enum_members():
    model = ODataModel()
    schema = TypeInformation(BaseTypeFullName="ComplexType", FullName="microsoft.graph.Thing")
    schema.add_property(PropertyInformation(Name="alpha"))
    schema.add_method(MethodInformation(Name="beta"))
    schema.add_member(MemberInformation(Name="Gamma"))
    model.add_type(schema)

    assert schema_members(model) == {"microsoft.graph.Thing": ["Gamma", "alpha", "beta"]}


def test_manifest_round_trip(tmp_path):
    manifest = Manifest(tmp_path / ".state" / "graph.json", "abc123", {"microsoft.graph.Thing": ["a", "b"]})
    manifest.save()

    loaded = Manifest.load(str(tmp_path / "graph.xml"), tmp_path)

    assert loaded is not None
    assert loaded.fingerprint == "abc123"
    assert loaded.members == {"microsoft.graph.Thing": ["a", "b"]}
