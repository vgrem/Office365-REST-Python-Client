"""Offline tests for the generator's OData type grammar.

The grammar is read once, at the boundary: :meth:`TypeRef.parse` turns a reference
string into an element name plus a collection flag, and every other question is
asked of that value. These tests are the specification of that reading, including
the cases where a wrapper is *not* a wrapper.
"""

from __future__ import annotations

from generator.odata.type_system import TypeRef, normalize_class_name
from office365.runtime.client_value_collection import ClientValueCollection


def test_a_reference_is_read_once_into_a_name_and_a_collection_flag() -> None:
    ref = TypeRef.parse("Collection(microsoft.graph.User)")

    assert ref.is_collection is True
    assert ref.name == "microsoft.graph.User"
    assert ref.text == "Collection(microsoft.graph.User)"


def test_a_plain_reference_is_its_own_element() -> None:
    ref = TypeRef.parse("microsoft.graph.User")

    assert ref.is_collection is False
    assert ref.name == "microsoft.graph.User"
    assert ref.element is ref
    assert ref.text == "microsoft.graph.User"


def test_no_type_reads_as_no_type() -> None:
    ref = TypeRef.parse(None)

    assert ref.name is None
    assert ref.is_collection is False
    assert ref.text is None
    assert ref.normalized is None
    assert ref.python_type is None
    assert ref.is_primitive is False


def test_an_incomplete_or_empty_wrapper_is_not_a_collection() -> None:
    for raw in ("Collection", "Collection(", "Collection()", "Collection(User"):
        assert TypeRef.parse(raw).is_collection is False, raw


def test_normalize_pascal_cases_the_last_segment() -> None:
    assert TypeRef.parse("microsoft.graph.user").normalized == "microsoft.graph.User"
    assert TypeRef.parse("Collection(microsoft.graph.user)").normalized == "microsoft.graph.User"
    assert TypeRef.parse("Edm.String").normalized == "Edm.String"
    assert normalize_class_name("") == ""


def test_namespace_and_short_name_describe_the_element() -> None:
    ref = TypeRef.parse("Collection(microsoft.graph.user)")

    assert ref.namespace == "microsoft.graph"
    assert ref.short_name == "User"


def test_is_primitive_includes_primitive_collections() -> None:
    assert TypeRef.parse("Edm.String").is_primitive
    assert TypeRef.parse("Collection(Edm.String)").is_primitive
    assert not TypeRef.parse("microsoft.graph.User").is_primitive


def test_python_type_covers_primitives_their_collections_and_nothing_else() -> None:
    assert TypeRef.parse("Edm.String").python_type is str
    assert TypeRef.parse("Edm.Int32").python_type is int
    assert TypeRef.parse("Collection(Edm.Int32)").python_type == ClientValueCollection[int]
    assert TypeRef.parse("Collection(Edm.Guid)").python_type is not None
    assert TypeRef.parse("microsoft.graph.User").python_type is None
    assert TypeRef.parse("Collection(microsoft.graph.User)").python_type is None


def test_a_reference_compares_by_what_it_means() -> None:
    assert TypeRef.parse("Collection(SP.Web)") == TypeRef("SP.Web", is_collection=True)
    assert TypeRef.parse("SP.Web") != TypeRef.parse("Collection(SP.Web)")
    assert len({TypeRef.parse("SP.Web"), TypeRef("SP.Web")}) == 1
