"""Offline tests for the generator's OData type grammar."""

from __future__ import annotations

from generator.odata.type_system import (
    TypeRef,
    is_collection_name,
    is_primitive_name,
    normalize_class_name,
    normalize_type_name,
    primitive_type_for,
    strip_collection,
)


def test_collection_grammar() -> None:
    assert is_collection_name("Collection(microsoft.graph.User)")
    assert not is_collection_name("microsoft.graph.User")
    assert strip_collection("Collection(microsoft.graph.User)") == "microsoft.graph.User"
    assert strip_collection("microsoft.graph.User") == "microsoft.graph.User"


def test_normalize_type_name_pascal_cases_last_segment() -> None:
    assert normalize_type_name("microsoft.graph.user") == "microsoft.graph.User"
    assert normalize_type_name("Collection(microsoft.graph.user)") == "microsoft.graph.User"
    assert normalize_type_name("Edm.String") == "Edm.String"
    assert normalize_type_name(None) is None
    assert normalize_class_name("") == ""


def test_is_primitive_name_includes_primitive_collections() -> None:
    assert is_primitive_name("Edm.String")
    assert is_primitive_name("Collection(Edm.String)")
    assert not is_primitive_name("microsoft.graph.User")


def test_primitive_type_for() -> None:
    assert primitive_type_for("Edm.String") is str
    assert primitive_type_for("microsoft.graph.User") is None


def test_type_ref_properties() -> None:
    ref = TypeRef.of("Collection(microsoft.graph.user)")

    assert ref.is_collection
    assert ref.text == "microsoft.graph.user"
    assert ref.element.raw == "microsoft.graph.user"
    assert ref.namespace == "microsoft.graph"
    assert ref.short_name == "User"
    assert ref.normalized == "microsoft.graph.User"
    assert not ref.is_primitive


def test_type_ref_primitive_and_non_collection() -> None:
    ref = TypeRef.of("Edm.Int32")

    assert ref.is_primitive
    assert ref.python_type is int
    assert not ref.is_collection
    assert ref.element.raw == "Edm.Int32"
