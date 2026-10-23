"""Tests for SharePoint list-structure verification."""

from __future__ import annotations

from office365.migration.sharepoint.structure import (
    ContentTypeDefinition,
    FieldDefinition,
    ListStructure,
    ViewDefinition,
)
from office365.migration.sharepoint.verify import (
    compare_list_structures,
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


def test_missing_content_type_reported_without_requiring_its_field_links():
    source = _structure(content_types=[("Task", ["Status"])])
    target = _structure()

    report = compare_list_structures(source, target)

    assert report.missing_content_types == ["Task"]
    # the whole CT is missing, so its field links are not double-reported
    assert report.missing_field_links == []


def _column_structure(name, schema_xml, title="Projects"):
    return ListStructure(title=title, fields=[FieldDefinition(internal_name=name, schema_xml=schema_xml)])


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


# --- container settings -------------------------------------------------------


def test_differing_setting_is_reported():
    source = ListStructure(title="Projects", settings={"EnableModeration": True, "ReadSecurity": 2})
    target = ListStructure(title="Projects", settings={"EnableModeration": False, "ReadSecurity": 2})

    report = compare_list_structures(source, target)

    assert report.settings_mismatches == ["EnableModeration: source=True, target=False"]
    assert not report.ok
    assert "settings: 1" in report.summary()


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
