"""Verify that a target list reproduces a source list's structure.

Content verification (:func:`office365.migration.validators.verify`) confirms
that items landed; it cannot confirm that the *container* was recreated, because
it never looks at columns, content types or views. This module closes that gap:
:func:`verify_list_structure` captures both lists' structures (read-only, via
:func:`capture_list_structure`) and reports what the source has that the target
does not.

Only *missing* structure is reported — a freshly created target list is
expected to carry additional built-in columns, content types and views, so
"extra" entries are not findings. Field links are compared per content type
(the REST API cannot attach a fresh column as a field link; see
:func:`provision_list_structure`).

The comparison is offline-testable: :func:`capture_list_structure` performs the
reads, so this module never talks to the server itself.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from office365.migration.sharepoint.structure import (
    FieldDefinition,
    ListStructure,
    capture_list_structure,
    comparable_schema,
    comparable_setting,
)

if TYPE_CHECKING:
    from office365.sharepoint.lists.list import List as SPList

__all__ = ["StructureReport", "compare_list_structures", "verify_list_structure"]


def _column_mismatches(source: FieldDefinition, target: FieldDefinition) -> list[str]:
    """Attribute-level differences between a source column and its target twin.

    A column present on both lists can still differ in policy — a required flag
    dropped, a choice list truncated, a validation formula lost — and comparing
    columns by name alone would report that list as ``OK``.
    """
    expected = comparable_schema(source.schema_xml)
    actual = comparable_schema(target.schema_xml)
    if not expected or not actual:
        return []  # unreadable schema on either side: reported as missing/unknown, not as a difference
    return [
        f"{source.internal_name}: {name} source={expected.get(name)!r}, target={actual.get(name)!r}"
        for name in sorted(set(expected) | set(actual))
        if expected.get(name) != actual.get(name)
    ]


@dataclass
class StructureReport:
    """What a source list has that its target counterpart is missing."""

    list_title: str = ""
    missing_columns: list[str] = field(default_factory=list)
    column_mismatches: list[str] = field(default_factory=list)
    missing_content_types: list[str] = field(default_factory=list)
    missing_views: list[str] = field(default_factory=list)
    missing_field_links: list[str] = field(default_factory=list)
    settings_mismatches: list[str] = field(default_factory=list)
    formatting_mismatches: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """Whether every captured source element is present on the target."""
        return not (
            self.missing_columns
            or self.column_mismatches
            or self.missing_content_types
            or self.missing_views
            or self.missing_field_links
            or self.settings_mismatches
            or self.formatting_mismatches
        )

    def summary(self) -> str:
        status = "OK" if self.ok else "MISMATCH"
        return (
            f"{status} | {self.list_title or 'list'} | columns: {len(self.missing_columns)}, "
            f"content types: {len(self.missing_content_types)}, views: {len(self.missing_views)}, "
            f"field links: {len(self.missing_field_links)}, settings: {len(self.settings_mismatches)}, "
            f"column attributes: {len(self.column_mismatches)}, formatting: {len(self.formatting_mismatches)}"
        )

    def to_dict(self) -> dict[str, Any]:
        """A JSON-serializable form (for reports/evidence packs)."""
        return {
            "list_title": self.list_title,
            "missing_columns": list(self.missing_columns),
            "column_mismatches": list(self.column_mismatches),
            "missing_content_types": list(self.missing_content_types),
            "missing_views": list(self.missing_views),
            "missing_field_links": list(self.missing_field_links),
            "settings_mismatches": list(self.settings_mismatches),
            "formatting_mismatches": list(self.formatting_mismatches),
            "notes": list(self.notes),
            "ok": self.ok,
        }


def verify_list_structure(source_list: SPList, target_list: SPList) -> StructureReport:
    """Capture both lists and report source structure missing on the target.

    Args:
        source_list: The source ``List`` (loaded/queried in place, GETs only).
        target_list: The target ``List``.

    Returns:
        A :class:`StructureReport`; never raises on absent structure (it reports
        what is missing instead).
    """
    source = capture_list_structure(source_list)
    target = capture_list_structure(target_list)
    return compare_list_structures(source, target, list_title=source.title)


def compare_list_structures(
    source: ListStructure,
    target: ListStructure,
    list_title: str | None = None,
) -> StructureReport:
    """Compare two already-captured :class:`ListStructure` snapshots."""
    report = StructureReport(list_title=list_title or source.title or "")

    target_by_name = {column.internal_name: column for column in target.fields}
    report.missing_columns = sorted(
        name for name in {column.internal_name for column in source.fields} if name not in target_by_name
    )
    for column in source.fields:
        counterpart = target_by_name.get(column.internal_name)
        if counterpart is not None:
            report.column_mismatches.extend(_column_mismatches(column, counterpart))
    report.column_mismatches.sort()

    target_content_types = {content_type.name for content_type in target.content_types if content_type.name}
    report.missing_content_types = sorted(
        content_type.name
        for content_type in source.content_types
        if content_type.name and content_type.name not in target_content_types
    )

    target_views = {view.title for view in target.views}
    report.missing_views = sorted(view.title for view in source.views if view.title not in target_views)

    target_links = {
        content_type.name: set(content_type.field_internal_names)
        for content_type in target.content_types
        if content_type.name
    }
    for content_type in source.content_types:
        if not content_type.name:
            continue
        existing = target_links.get(content_type.name)
        if existing is None:
            continue  # the whole content type is already reported as missing
        for internal_name in content_type.field_internal_names:
            if internal_name not in existing:
                report.missing_field_links.append(f"{content_type.name}: {internal_name}")
    report.missing_field_links.sort()

    for column in source.fields:
        counterpart = target_by_name.get(column.internal_name)
        if counterpart is not None and column.custom_formatter != counterpart.custom_formatter:
            report.formatting_mismatches.append(f"column {column.internal_name}: its formatting JSON differs")
    target_views_by_title = {view.title: view for view in target.views if view.title}
    for view in source.views:
        counterpart = target_views_by_title.get(view.title)
        if counterpart is not None and view.custom_formatter != counterpart.custom_formatter:
            report.formatting_mismatches.append(f"view {view.title}: its formatting JSON differs")
    report.formatting_mismatches.sort()

    for name, value in source.settings.items():
        target_value = target.settings.get(name)
        if comparable_setting(name, target_value) != comparable_setting(name, value):
            report.settings_mismatches.append(f"{name}: source={value!r}, target={target_value!r}")
    report.settings_mismatches.sort()

    return report
