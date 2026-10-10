"""Offline tests for OData type-name formatting and class resolution (codegen side)."""

from __future__ import annotations

import datetime

import pytest
from generator.builders.collector import TypeReferenceCollector
from generator.builders.naming import item_name, python_name
from generator.builders.property import PropertyBuilder
from generator.builders.resolution import TypeRegistry
from generator.odata.property import PropertyInformation
from office365.runtime.odata.type import ODataType


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


def test_primitive_and_collection_lookups():
    assert ODataType.is_primitive_name("Edm.Int32") is True
    assert ODataType.is_primitive_name("SP.Web") is False
    assert ODataType.primitive_type_for("Edm.Int32") is int
    assert ODataType.primitive_type_for("Edm.Stream") is bytes
    assert ODataType.primitive_type_for("SP.Web") is None
    assert ODataType.is_collection_name("Collection(SP.Web)") is True
    assert ODataType.is_collection_name("SP.Web") is False


def test_odata_v3_time_primitive():
    # Edm.Time is the OData v3 name for a time-of-day (v4: Edm.TimeOfDay)
    assert python_name("Edm.Time") == "time"
    assert ODataType.is_primitive_name("Edm.Time") is True
    assert ODataType.primitive_type_for("Edm.Time") is datetime.time
    # reverse lookup keeps returning the v4 name
    assert ODataType.resolve_type_name(datetime.time) == "Edm.TimeOfDay"


def test_odata_v3_numeric_primitives():
    assert python_name("Edm.Byte") == "int"
    assert python_name("Edm.Int16") == "int"
    assert python_name("Edm.Decimal") == "float"
    assert ODataType.primitive_type_for("Edm.Byte") is int
    assert ODataType.primitive_type_for("Edm.Decimal") is float


def test_unmapped_edm_primitive_raises():
    with pytest.raises(ValueError):
        python_name("Edm.Unknown")
    with pytest.raises(ValueError):
        python_name("Collection(Edm.Unknown)")


def test_runtime_type_utility_is_pure():
    for removed in ("client_type_name", "is_collection", "is_primitive_type"):
        assert not hasattr(ODataType, removed)
    assert ODataType.normalize_type_name("microsoft.graph.user") == "microsoft.graph.User"
    assert ODataType.resolve_type_name(str) == "Edm.String"


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
