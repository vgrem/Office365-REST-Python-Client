"""End-to-end test: synthetic CSDL -> reader -> pipeline -> generated files.

Exercises the whole flow (v3 and v4) for **every** kind (complex, entity, enum)
plus generated operation methods, idempotency on unchanged metadata, and
additions-only behaviour when a type gains a member.
"""

from __future__ import annotations

import ast
from pathlib import Path

from generator.config import GeneratorOptions
from generator.odata.v3.metadata_reader import ODataV3Reader
from generator.odata.v4.metadata_reader import ODataV4Reader
from generator.pipeline import GeneratorPipeline

_GENERATOR = Path(__file__).resolve().parents[2] / "generator"

_V3_CSDL = """<?xml version="1.0" encoding="utf-8"?>
<edmx:Edmx Version="1.0" xmlns:edmx="http://schemas.microsoft.com/ado/2007/06/edmx">
  <edmx:DataServices>
    <Schema Namespace="SP" xmlns="http://schemas.microsoft.com/ado/2009/11/edm">
      <EnumType Name="WidgetKind">
        <Member Name="alpha" Value="0" />
        <Member Name="beta" Value="1" />
      </EnumType>
      <ComplexType Name="WidgetSettings">
        <Property Name="name" Type="Edm.String" />
        <Property Name="kind" Type="SP.WidgetKind" />
      </ComplexType>
      <EntityType Name="Widget">
        <Key><PropertyRef Name="Id" /></Key>
        <Property Name="Id" Type="Edm.String" Nullable="false" />
        <Property Name="Title" Type="Edm.String" />
      </EntityType>
      <FunctionImport Name="DoThing" ReturnType="Edm.String" IsBindable="true" IsComposable="true">
        <Parameter Name="this" Type="SP.Widget" />
        <Parameter Name="count" Type="Edm.Int32" />
      </FunctionImport>
    </Schema>
  </edmx:DataServices>
</edmx:Edmx>
"""

_V4_CSDL = """<?xml version="1.0" encoding="utf-8"?>
<edmx:Edmx Version="4.0" xmlns:edmx="http://docs.oasis-open.org/odata/ns/edmx">
  <edmx:DataServices>
    <Schema Namespace="microsoft.graph" xmlns="http://docs.oasis-open.org/odata/ns/edm">
      <EnumType Name="WidgetKind">
        <Member Name="alpha" Value="0" />
        <Member Name="beta" Value="1" />
      </EnumType>
      <ComplexType Name="WidgetSettings">
        <Property Name="kind" Type="microsoft.graph.WidgetKind" />
      </ComplexType>
      <EntityType Name="Widget">
        <Key><PropertyRef Name="id" /></Key>
        <Property Name="id" Type="Edm.String" Nullable="false" />
        <NavigationProperty Name="widgets" Type="Collection(microsoft.graph.Widget)" ContainsTarget="true" />
      </EntityType>
      <Action Name="reset" IsBound="true">
        <Parameter Name="bindingParameter" Type="microsoft.graph.Widget" />
        <Parameter Name="reason" Type="Edm.String" />
      </Action>
    </Schema>
  </edmx:DataServices>
</edmx:Edmx>
"""


def _options(tmp_path: Path, *, template: str, namespace: str, kinds: list[str], prefix: str) -> GeneratorOptions:
    return GeneratorOptions(
        metadata_path=str(tmp_path / "metadata.xml"),
        output_path=str(tmp_path / "office365"),
        template_path=str(_GENERATOR / "templates" / template),
        modules="office365.runtime.types",
        namespace=namespace,
        context_type="GraphClient" if template == "graph" else "ClientContext",
        include_base_types=kinds,
        generate_methods="true",
        routing={prefix: "office365"},
    )


def _run(options: GeneratorOptions, reader: type, tmp_path: Path, *, force: bool = False) -> None:
    model = reader(options.metadata_path).read()
    GeneratorPipeline(model, options, base_dir=tmp_path, force=force, smoke=False).run()


def _source(tmp_path: Path, name: str) -> str:
    source = (tmp_path / "office365" / name).read_text(encoding="utf-8")
    ast.parse(source)
    return source


def test_sharepoint_generates_all_kinds_and_methods(tmp_path: Path) -> None:
    (tmp_path / "metadata.xml").write_text(_V3_CSDL, encoding="utf-8")
    kinds = ["EntityType", "ComplexType", "EnumType"]
    options = _options(tmp_path, template="sharepoint", namespace="SP", kinds=kinds, prefix="SP")

    _run(options, ODataV3Reader, tmp_path)

    entity = _source(tmp_path, "widget.py")
    complex_type = _source(tmp_path, "widget_settings.py")
    enum = _source(tmp_path, "widget_kind.py")

    assert "class Widget(Entity):" in entity
    assert "def do_thing" in entity  # bound FunctionImport -> generated method
    # Every generated getter carries its wire name, so no caller spells it again.
    assert '@odata(name="Title")' in entity
    assert "from office365.runtime.types.odata_property import odata" in entity
    assert "class WidgetSettings(ClientValue):" in complex_type
    assert "kind: WidgetKind = WidgetKind.alpha" in complex_type  # planned enum default
    assert "class WidgetKind(Enum):" in enum

    # Re-running an unchanged metadata (bypassing the fast path) is a no-op.
    _run(options, ODataV3Reader, tmp_path, force=True)
    assert _source(tmp_path, "widget.py") == entity
    assert _source(tmp_path, "widget_settings.py") == complex_type


def test_sharepoint_end_to_end_is_additions_only(tmp_path: Path) -> None:
    metadata = tmp_path / "metadata.xml"
    metadata.write_text(_V3_CSDL, encoding="utf-8")
    options = _options(tmp_path, template="sharepoint", namespace="SP", kinds=["EntityType"], prefix="SP")
    _run(options, ODataV3Reader, tmp_path)
    widget = tmp_path / "office365" / "widget.py"
    before = widget.read_text(encoding="utf-8")

    # The metadata gains a property: the existing content must be preserved.
    metadata.write_text(
        _V3_CSDL.replace(
            '<Property Name="Title"', '<Property Name="Note" Type="Edm.String" />\n        <Property Name="Title"'
        ),
        encoding="utf-8",
    )
    _run(options, ODataV3Reader, tmp_path, force=True)
    after = widget.read_text(encoding="utf-8")
    ast.parse(after)

    assert '"Note"' in after  # new member added
    for line in before.splitlines():
        if line.strip():
            assert line in after  # nothing existing was dropped


def test_graph_generates_all_kinds_and_methods(tmp_path: Path) -> None:
    (tmp_path / "metadata.xml").write_text(_V4_CSDL, encoding="utf-8")
    kinds = ["ComplexType", "EnumType", "EntityType"]
    options = _options(tmp_path, template="graph", namespace="", kinds=kinds, prefix="microsoft.graph")

    _run(options, ODataV4Reader, tmp_path)

    entity = _source(tmp_path, "widget.py")
    complex_type = _source(tmp_path, "widget_settings.py")
    enum = _source(tmp_path, "widget_kind.py")

    assert "class Widget(Entity):" in entity
    assert "def reset" in entity  # bound Action -> generated method
    # A navigation property is declared as such: $expand reaches it, $select cannot.
    assert '@odata(name="widgets", navigation=True)' in entity
    assert '@odata(name="id")' in entity
    assert "class WidgetSettings(ClientValue):" in complex_type
    assert "kind: WidgetKind = WidgetKind.alpha" in complex_type
    assert "class WidgetKind(Enum):" in enum

    # Idempotent on an unchanged metadata.
    _run(options, ODataV4Reader, tmp_path, force=True)
    assert _source(tmp_path, "widget.py") == entity
