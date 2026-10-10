"""End-to-end test: synthetic CSDL -> reader -> pipeline -> generated files.

Exercises the whole flow (v3 and v4), including idempotency on an unchanged
metadata and additions-only behaviour when a type gains a member.
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
      <EntityType Name="Widget">
        <Key><PropertyRef Name="Id" /></Key>
        <Property Name="Id" Type="Edm.String" Nullable="false" />
        <Property Name="Title" Type="Edm.String" />
      </EntityType>
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
      <ComplexType Name="Widget">
        <Property Name="name" Type="Edm.String" />
        <Property Name="kind" Type="microsoft.graph.WidgetKind" />
      </ComplexType>
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
        include_base_types=kinds,
        routing={prefix: "office365"},
    )


def _run(options: GeneratorOptions, reader: type, tmp_path: Path, *, force: bool = False) -> None:
    model = reader(options.metadata_path).read()
    GeneratorPipeline(model, options, base_dir=tmp_path, force=force, smoke=False).run()


def test_sharepoint_entity_end_to_end(tmp_path: Path) -> None:
    (tmp_path / "metadata.xml").write_text(_V3_CSDL, encoding="utf-8")
    options = _options(tmp_path, template="sharepoint", namespace="SP", kinds=["EntityType"], prefix="SP")

    _run(options, ODataV3Reader, tmp_path)
    widget = tmp_path / "office365" / "widget.py"
    assert widget.is_file()
    source = widget.read_text(encoding="utf-8")
    ast.parse(source)
    assert "class Widget(Entity):" in source
    assert '"Title"' in source and '"Id"' in source

    # Re-running an unchanged metadata (bypassing the fast path) is a no-op.
    _run(options, ODataV3Reader, tmp_path, force=True)
    assert widget.read_text(encoding="utf-8") == source


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
        if line.strip() and not line.startswith("from __future__"):
            assert line in after  # nothing existing was dropped


def test_graph_complex_and_enum_end_to_end(tmp_path: Path) -> None:
    (tmp_path / "metadata.xml").write_text(_V4_CSDL, encoding="utf-8")
    options = _options(
        tmp_path, template="graph", namespace="", kinds=["ComplexType", "EnumType"], prefix="microsoft.graph"
    )

    _run(options, ODataV4Reader, tmp_path)

    widget = tmp_path / "office365" / "widget.py"
    enum = tmp_path / "office365" / "widget_kind.py"
    assert widget.is_file() and enum.is_file()
    widget_source = widget.read_text(encoding="utf-8")
    enum_source = enum.read_text(encoding="utf-8")
    ast.parse(widget_source)
    ast.parse(enum_source)

    assert "class Widget(ClientValue):" in widget_source
    # an enum field planned in the same run defaults to its first member
    assert "kind: WidgetKind = WidgetKind.alpha" in widget_source
    assert "class WidgetKind(Enum):" in enum_source
    assert 'alpha = "0"' in enum_source

    # Idempotent on an unchanged metadata.
    _run(options, ODataV4Reader, tmp_path, force=True)
    assert widget.read_text(encoding="utf-8") == widget_source
    assert enum.read_text(encoding="utf-8") == enum_source
