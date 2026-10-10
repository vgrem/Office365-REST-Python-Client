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


def test_entity_anchors_map_root_types_to_container_names() -> None:
    assert _document().entity_anchors() == {
        "microsoft.graph.User": "users",
        "microsoft.graph.ReportRoot": "reports",
    }
