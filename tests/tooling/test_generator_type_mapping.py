"""Offline tests for OData type-name formatting and class resolution (codegen side)."""

from __future__ import annotations

import datetime

import pytest
from generator.builders.collector import TypeReferenceCollector
from generator.builders.naming import item_name, python_name
from generator.builders.property import PropertyBuilder
from generator.builders.resolution import TypeRegistry
from generator.odata.property import PropertyInformation
from generator.odata.type_system import TypeRef
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.odata import edm
from office365.runtime.odata.edm import collection_type_name, edm_type_name, primitive_type_for


def test_primitive_type_name_formatting():
    assert python_name("Edm.String") == "str"
    assert python_name("Edm.Int32") == "int"
    assert python_name("Edm.Guid") == "UUID"
    assert python_name("Edm.DateTimeOffset") == "datetime"
    assert python_name("Edm.Stream") == "bytes"


def test_collection_type_name_formatting():
    assert python_name("Collection(Edm.String)") == "StringCollection"
    assert python_name("Collection(Edm.Int32)") == "ClientValueCollection"
    assert python_name("Collection(SP.Web)") == "ClientValueCollection[Web]"
    assert python_name("Collection(SP.Web)", is_object_type=True) == "EntityCollection[Web]"


def test_entity_and_complex_type_name_formatting():
    assert python_name("SP.Web") == "Web"
    assert python_name("microsoft.graph.user") == "User"
    assert python_name(None) == ""


def test_item_type_name_formatting():
    assert item_name("Collection(SP.Web)") == "Web"
    assert item_name("SP.Web") == "Web"


def test_the_wrapper_is_read_once_and_written_once():
    """A reference is parsed at the boundary; call sites ask the value, not the string."""
    ref = TypeRef.parse("Collection(SP.Web)")
    assert ref.is_collection is True
    assert ref.name == "SP.Web"
    assert ref.text == "Collection(SP.Web)"
    # A nested wrapper reads as an element *named* Collection(...), not as two wrappers.
    nested = TypeRef.parse("Collection(Collection(SP.Web))")
    assert nested.name == "Collection(SP.Web)"
    assert nested.element.is_collection is False


def test_primitive_and_collection_lookups():
    assert TypeRef.parse("Edm.Int32").is_primitive is True
    assert TypeRef.parse("Collection(Edm.Int32)").is_primitive is True
    assert TypeRef.parse("SP.Web").is_primitive is False
    assert TypeRef.parse("Edm.Int32").python_type is int
    assert TypeRef.parse("Edm.Stream").python_type is bytes
    assert TypeRef.parse("Collection(Edm.Int32)").python_type == ClientValueCollection[int]
    assert TypeRef.parse("SP.Web").python_type is None
    assert TypeRef.parse("Collection(SP.Web)").is_collection is True
    assert TypeRef.parse("SP.Web").is_collection is False


def test_odata_v3_time_primitive():
    # Edm.Time is the OData v3 name for a time-of-day (v4: Edm.TimeOfDay)
    assert python_name("Edm.Time") == "time"
    assert TypeRef.parse("Edm.Time").is_primitive is True
    assert primitive_type_for("Edm.Time") is datetime.time
    # reverse lookup keeps returning the v4 name
    assert edm_type_name(datetime.time) == "Edm.TimeOfDay"


def test_odata_v3_numeric_primitives():
    assert python_name("Edm.Byte") == "int"
    assert python_name("Edm.Int16") == "int"
    assert python_name("Edm.Decimal") == "float"
    assert primitive_type_for("Edm.Byte") is int
    assert primitive_type_for("Edm.Decimal") is float


def test_unmapped_edm_primitive_raises():
    with pytest.raises(ValueError):
        python_name("Edm.Unknown")
    with pytest.raises(ValueError):
        python_name("Collection(Edm.Unknown)")


def test_the_runtime_formats_names_it_does_not_parse_them():
    """Parsing a type *reference* is CSDL work; the runtime only answers "what is this class called?"""
    assert not hasattr(edm, "ODataType")
    assert TypeRef.parse("microsoft.graph.user").normalized == "microsoft.graph.User"
    assert edm_type_name(str) == "Edm.String"


def test_the_runtime_is_asked_about_classes_including_primitives():
    """The argument is a class, not an instance — which is why the parameter is ``type``.

    A union of the model base classes would exclude ``str``/``uuid.UUID`` (the common
    case for primitive collections) and add nothing for generated models, whose
    classes only exist after code generation.
    """
    assert collection_type_name(str) == "Collection(Edm.String)"
    assert collection_type_name(datetime.time) == "Collection(Edm.TimeOfDay)"


def test_a_declared_name_is_read_from_the_class_fact():
    """A generated model declares its name once, so resolving it never builds the model."""

    class Model:
        _odata_type_name = "microsoft.graph.Model"

        def __init__(self) -> None:  # pragma: no cover - must not run
            raise AssertionError("name resolution must not instantiate the model")

    assert edm_type_name(Model) == "microsoft.graph.Model"


def test_an_undeclared_name_is_none_rather_than_a_guess():
    class NeedsAContext:
        def __init__(self, context) -> None:
            self.context = context

    assert edm_type_name(NeedsAContext) is None
    assert collection_type_name(NeedsAContext) is None


def test_resolver_finds_generated_class_and_caches():
    resolver = TypeRegistry(["office365.sharepoint"])
    resolved = resolver.resolve("SP.Web")
    assert resolved is not None
    assert resolved.__name__ == "Web"
    assert resolver.resolve("SP.Web") is resolved
    assert resolver.resolve("SP.Unknown") is None
    TypeRegistry.cache_clear()


def test_ambiguous_short_names_resolve_by_entity_type_name():
    """``SP.User`` and ``SP.Directory.User`` are distinct classes named ``User``."""
    resolver = TypeRegistry(["office365.sharepoint"], namespace="SP")
    assert resolver.module_for("SP.User") == "office365.sharepoint.principal.users.user"
    assert resolver.module_for("SP.Directory.User") == "office365.sharepoint.directory.users.user"
    assert resolver.module_for("SP.Group") == "office365.sharepoint.principal.groups.group"
    assert resolver.module_for("SP.Directory.Group") == "office365.sharepoint.directory.groups.group"
    TypeRegistry.cache_clear()


def test_property_builder_uses_injected_resolver():
    resolver = TypeRegistry(["office365.sharepoint"])
    prop = PropertyBuilder(PropertyInformation(Name="Web", TypeName="SP.Web"), resolver=resolver)
    assert prop.client_type_name == "Web"
    assert prop.resolve_client_type() is not None


def test_collector_resolves_property_imports():
    resolver = TypeRegistry(["office365.sharepoint"])
    prop = PropertyBuilder(PropertyInformation(Name="Web", TypeName="SP.Web"), resolver=resolver)
    collector = TypeReferenceCollector(resolver)
    collector.add(prop.client_type_name)
    collector.add_custom(prop)
    # annotation-only imports live under TYPE_CHECKING (runtime via the getter)
    assert collector._type_checking["Web"] == "office365.sharepoint.webs.web"
