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


def test_missing_columns_reported():
    source = _structure(columns=["Status", "Owner"])
    target = _structure(columns=["Status"])

    report = compare_list_structures(source, target)

    assert report.missing_columns == ["Owner"]
    assert not report.ok


def test_missing_content_type_reported_without_requiring_its_field_links():
    source = _structure(content_types=[("Task", ["Status"])])
    target = _structure()

    report = compare_list_structures(source, target)

    assert report.missing_content_types == ["Task"]
    # the whole CT is missing, so its field links are not double-reported
    assert report.missing_field_links == []


def test_missing_field_link_reported():
    source = _structure(content_types=[("Task", ["Status", "Owner"])])
    target = _structure(content_types=[("Task", ["Status"])])

    report = compare_list_structures(source, target)

    assert report.missing_field_links == ["Task: Owner"]
    assert not report.ok


def test_missing_views_reported():
    source = _structure(views=["All Items", "By Owner"])
    target = _structure(views=["All Items"])

    report = compare_list_structures(source, target)

    assert report.missing_views == ["By Owner"]


def test_extra_target_structure_is_not_a_finding():
    source = _structure(columns=["Status"], views=["All Items"])
    target = _structure(columns=["Status", "BuiltIn"], views=["All Items", "Default"])

    report = compare_list_structures(source, target)

    assert report.ok


def test_to_dict_is_serializable():
    report = StructureReport(
        list_title="Projects",
        missing_columns=["Owner"],
        missing_content_types=["Task"],
        missing_views=["By Owner"],
        missing_field_links=["Task: Owner"],
    )

    data = report.to_dict()

    assert data["list_title"] == "Projects"
    assert data["missing_columns"] == ["Owner"]
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


def test_verify_list_structure_reports_snapshot_differences():
    source = _structure(columns=["Status"])
    target = _structure(columns=[])

    report = compare_list_structures(source, target, list_title="Source Projects")

    assert report.list_title == "Source Projects"
    assert report.missing_columns == ["Status"]


# --- container settings -------------------------------------------------------


def test_identical_settings_are_ok():
    source = ListStructure(title="Projects", settings={"EnableModeration": True, "MajorVersionLimit": 12})
    target = ListStructure(title="Projects", settings={"EnableModeration": True, "MajorVersionLimit": 12})

    report = compare_list_structures(source, target)

    assert report.ok
    assert report.settings_mismatches == []


def test_differing_setting_is_reported():
    source = ListStructure(title="Projects", settings={"EnableModeration": True, "ReadSecurity": 2})
    target = ListStructure(title="Projects", settings={"EnableModeration": False, "ReadSecurity": 2})

    report = compare_list_structures(source, target)

    assert report.settings_mismatches == ["EnableModeration: source=True, target=False"]
    assert not report.ok
    assert "settings: 1" in report.summary()


def test_setting_absent_on_the_target_is_reported():
    source = ListStructure(title="Projects", settings={"EnableAttachments": False})

    report = compare_list_structures(source, ListStructure(title="Projects"))

    assert report.settings_mismatches == ["EnableAttachments: source=False, target=None"]


def test_validation_formula_is_compared_without_its_decoration():
    # SharePoint stores "=IF([Title]="",TRUE,FALSE)" as "=IF(Title="",TRUE,FALSE)"
    source = ListStructure(title="Projects", settings={"ValidationFormula": '=IF([Title]="",TRUE,FALSE)'})
    target = ListStructure(title="Projects", settings={"ValidationFormula": '=IF(Title="", TRUE, FALSE)'})

    report = compare_list_structures(source, target)

    assert report.settings_mismatches == []
    assert report.ok


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
