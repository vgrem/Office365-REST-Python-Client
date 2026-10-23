"""Tests for the per-format report record IO."""

from __future__ import annotations

from pathlib import Path

import pytest
from office365.migration.report_io import write_dataset, write_formats

_RECORDS = [{"name": "a", "value": 1}, {"name": "b", "value": 2}]


def test_write_formats_returns_each_path(tmp_path):
    paths = write_formats(_RECORDS, tmp_path, "rows")

    assert {Path(p).suffix for p in paths} == {".csv", ".json"}


def test_write_dataset_unknown_format(tmp_path):
    with pytest.raises(KeyError, match="format"):
        write_dataset(_RECORDS, tmp_path, "rows", fmt="parquet")
