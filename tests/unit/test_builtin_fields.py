"""Tests for the canonical built-in SharePoint field names."""

from __future__ import annotations

from office365.migration.sharepoint import SharePointAssessmentOptions
from office365.sharepoint.fields.builtin_field_name import (
    SYSTEM_FIELD_NAMES,
    SPBuiltInFieldName,
)


def test_builtin_field_name_lookup():
    assert SPBuiltInFieldName.FileLeafRef == "FileLeafRef"
    assert SPBuiltInFieldName.FSObjType == "FSObjType"
    assert SPBuiltInFieldName.is_builtin("ContentTypeId")
    assert not SPBuiltInFieldName.is_builtin("MyColumn")


def test_system_field_names_are_the_canonical_set_plus_the_extras():
    # The union is what keeps ``AppAuthor`` in the reported system columns.
    assert SPBuiltInFieldName.ALL <= SYSTEM_FIELD_NAMES
    assert "AppAuthor" in SYSTEM_FIELD_NAMES
    assert "MyColumn" not in SYSTEM_FIELD_NAMES


def test_assessment_options_default_from_canonical_set():
    assert SharePointAssessmentOptions().system_field_names == set(SYSTEM_FIELD_NAMES)
