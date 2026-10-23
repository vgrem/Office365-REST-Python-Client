"""Tests for SharePoint list-structure verification."""

from __future__ import annotations

from office365.migration.sharepoint.structure import (
    ContentTypeDefinition,
    FieldDefinition,
    ListStructure,
    ViewDefinition,
)
from office365.migration.sharepoint.verify import (
    StructureReport,
    compare_list_structures,
    verify_list_structure,
)


def _structure(*, columns=(), content_types=(), views=()):
    return ListStructure(
        title="Projects",
        fields=[FieldDefinition(internal_name=name) for name in columns],
        content_types=[
            ContentTypeDefinition(string_id=f"0x0100{name}", name=name, field_internal_names=list(links))
            for name, links in content_types
        ],
        views=[ViewDefinition(title=title) for title in views],
    )


def test_identical_structure_is_ok():
    source = _structure(columns=["Status"], content_types=[("Task", ["Status"])], views=["All Items"])
    target = _structure(columns=["Status"], content_types=[("Task", ["Status"])], views=["All Items"])

    report = compare_list_structures(source, target)

    assert report.ok
    assert report.summary().startswith("OK")


def test_missing_content_type_reported_without_requiring_its_field_links():
    source = _structure(content_types=[("Task", ["Status"])])
    target = _structure()

    report = compare_list_structures(source, target)

    assert report.missing_content_types == ["Task"]
    # the whole CT is missing, so its field links are not double-reported
    assert report.missing_field_links == []


def _column_structure(name, schema_xml, title="Projects"):
    return ListStructure(title=title, fields=[FieldDefinition(internal_name=name, schema_xml=schema_xml)])


def test_column_policy_difference_is_reported():
    source = _column_structure("Code", '<Field Type="Text" Name="Code" Required="TRUE" MaxLength="50"/>')
    target = _column_structure("Code", '<Field Type="Text" Name="Code" Required="FALSE" MaxLength="50"/>')

    report = compare_list_structures(source, target)

    assert report.missing_columns == []
    assert report.column_mismatches == ["Code: attribute Required source='TRUE', target='FALSE'"]
    assert not report.ok
    assert "column attributes: 1" in report.summary()


def test_column_choices_and_default_are_compared():
    source = _column_structure(
        "Category",
        '<Field Type="Choice" Name="Category"><Default>B</Default>'
        "<CHOICES><CHOICE>A</CHOICE><CHOICE>B</CHOICE></CHOICES></Field>",
    )
    target = _column_structure(
        "Category",
        '<Field Type="Choice" Name="Category"><Default>B</Default><CHOICES><CHOICE>A</CHOICE></CHOICES></Field>',
    )

    report = compare_list_structures(source, target)

    assert report.column_mismatches == ["Category: choices source=('A', 'B'), target=('A',)"]


def test_unparsable_column_schema_is_not_a_finding():
    source = _column_structure("Broken", "not xml")
    target = _column_structure("Broken", '<Field Type="Text" Name="Broken"/>')

    report = compare_list_structures(source, target)

    assert report.column_mismatches == []
    assert report.ok


def test_to_dict_is_serializable():
    report = StructureReport(
        list_title="Projects",
        missing_columns=["Owner"],
        column_mismatches=["Code: attribute Required source='TRUE', target='FALSE'"],
        missing_content_types=["Task"],
        missing_views=["By Owner"],
        missing_field_links=["Task: Owner"],
    )

    data = report.to_dict()

    assert data["list_title"] == "Projects"
    assert data["missing_columns"] == ["Owner"]
    assert data["column_mismatches"] == ["Code: attribute Required source='TRUE', target='FALSE'"]
    assert data["missing_field_links"] == ["Task: Owner"]
    assert data["ok"] is False


def test_verify_list_structure_captures_both_lists(monkeypatch):
    source = _structure(columns=["Status"])
    target = _structure(columns=["Status", "Extra"])
    captured = []

    def fake_capture(sp_list):
        captured.append(sp_list)
        return source if sp_list == "source" else target

    monkeypatch.setattr("office365.migration.sharepoint.verify.capture_list_structure", fake_capture)

    report = verify_list_structure("source", "target")

    assert captured == ["source", "target"]
    # capture order: source first (title from source), then target
    assert report.list_title == "Projects"
    assert report.ok


# --- container settings -------------------------------------------------------


def test_differing_setting_is_reported():
    source = ListStructure(title="Projects", settings={"EnableModeration": True, "ReadSecurity": 2})
    target = ListStructure(title="Projects", settings={"EnableModeration": False, "ReadSecurity": 2})

    report = compare_list_structures(source, target)

    assert report.settings_mismatches == ["EnableModeration: source=True, target=False"]
    assert not report.ok
    assert "settings: 1" in report.summary()


def test_different_validation_formula_is_reported():
    source = ListStructure(title="Projects", settings={"ValidationFormula": '=IF([Title]="",TRUE,FALSE)'})
    target = ListStructure(title="Projects", settings={"ValidationFormula": '=IF(Title="",FALSE,TRUE)'})

    report = compare_list_structures(source, target)

    assert len(report.settings_mismatches) == 1
    assert "ValidationFormula" in report.settings_mismatches[0]


def test_settings_are_reported_in_the_json_form():
    source = ListStructure(title="Projects", settings={"EnableModeration": True})
    target = ListStructure(title="Projects")

    payload = compare_list_structures(source, target).to_dict()

    assert payload["ok"] is False
    assert payload["settings_mismatches"] == ["EnableModeration: source=True, target=None"]


def test_column_and_view_formatting_are_verified():
    source = ListStructure(
        title="Projects",
        fields=[FieldDefinition(internal_name="Status", custom_formatter='{"elmType": "div"}')],
        views=[ViewDefinition(title="All Items", custom_formatter='{"additionalRowClass": "x"}')],
    )
    target = ListStructure(
        title="Projects",
        fields=[FieldDefinition(internal_name="Status")],
        views=[ViewDefinition(title="All Items")],
    )

    report = compare_list_structures(source, target)

    assert not report.ok
    assert report.formatting_mismatches == [
        "column Status: its formatting JSON differs",
        "view All Items: its formatting JSON differs",
    ]
    assert "formatting: 2" in report.summary()
    assert report.to_dict()["formatting_mismatches"] == report.formatting_mismatches
