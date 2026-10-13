"""Offline tests for the CSDL document wrapper (namespaces, aliases, traversal)."""

from __future__ import annotations

from xml.etree import ElementTree as ET

from generator.odata.csdl import CsdlDocument

_NAMESPACES = {
    "xmlns": "http://docs.oasis-open.org/odata/ns/edm",
    "edmx": "http://docs.oasis-open.org/odata/ns/edmx",
}

_XML = """<?xml version="1.0"?>
<edmx:Edmx xmlns:edmx="http://docs.oasis-open.org/odata/ns/edmx" Version="4.0">
  <edmx:DataServices>
    <Schema Namespace="microsoft.graph" Alias="graph" xmlns="http://docs.oasis-open.org/odata/ns/edm">
      <ComplexType Name="Thing">
        <Property Name="owner" Type="graph.user" />
      </ComplexType>
      <EntityContainer Name="GraphService">
        <EntitySet Name="users" EntityType="graph.user" />
        <Singleton Name="reports" Type="graph.reportRoot" />
      </EntityContainer>
    </Schema>
  </edmx:DataServices>
</edmx:Edmx>
"""


def _document() -> CsdlDocument:
    return CsdlDocument(ET.fromstring(_XML), _NAMESPACES)


def test_schemas_and_find() -> None:
    document = _document()

    assert len(document.schemas()) == 1
    assert document.find("edmx:DataServices/xmlns:Schema").get("Namespace") == "microsoft.graph"
    assert document.namespaces == _NAMESPACES


def test_qualified_type_name_expands_aliases() -> None:
    document = _document()

    assert document.qualified_type_name("graph.user") == "microsoft.graph.User"
    assert document.qualified_type_name("Edm.String") == "Edm.String"
    assert document.qualified_type_name(None) is None


def test_qualified_type_name_collection() -> None:
    assert _document().qualified_type_name("Collection(graph.user)") == "Collection(microsoft.graph.User)"


def test_parse_parameters_qualifies_types() -> None:
    function_node = ET.fromstring(
        '<Function Name="f" xmlns="http://docs.oasis-open.org/odata/ns/edm">'
        '<Parameter Name="p" Type="graph.user" /></Function>'
    )

    assert _document().parse_parameters(function_node) == [
        {"Name": "p", "Type": "microsoft.graph.User", "Nullable": True}
    ]


def test_parse_alternate_keys() -> None:
    node = ET.fromstring(
        '<EntityType Name="application" xmlns="http://docs.oasis-open.org/odata/ns/edm">'
        '<Annotation Term="Org.OData.Core.V1.AlternateKeys"><Collection>'
        '<Record Type="Org.OData.Core.V1.AlternateKey"><PropertyValue Property="Key"><Collection>'
        '<Record Type="Org.OData.Core.V1.PropertyRef">'
        '<PropertyValue Property="Alias" String="appId" />'
        '<PropertyValue Property="Name" PropertyPath="appId" />'
        "</Record></Collection></PropertyValue></Record>"
        '<Record Type="Org.OData.Core.V1.AlternateKey"><PropertyValue Property="Key"><Collection>'
        '<Record Type="Org.OData.Core.V1.PropertyRef">'
        '<PropertyValue Property="Alias" String="uniqueName" />'
        '<PropertyValue Property="Name" PropertyPath="uniqueName" />'
        "</Record></Collection></PropertyValue></Record>"
        "</Collection></Annotation></EntityType>"
    )

    assert _document().parse_alternate_keys(node) == [("appId",), ("uniqueName",)]


def test_parse_alternate_keys_absent_returns_empty() -> None:
    node = ET.fromstring('<EntityType Name="thing" xmlns="http://docs.oasis-open.org/odata/ns/edm" />')

    assert _document().parse_alternate_keys(node) == []


def test_entity_anchors_map_root_types_to_container_names() -> None:
    assert _document().entity_anchors() == {
        "microsoft.graph.User": "users",
        "microsoft.graph.ReportRoot": "reports",
    }
