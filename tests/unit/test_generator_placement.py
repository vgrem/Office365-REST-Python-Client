"""Offline tests for hierarchical (subsystem) placement of new types."""

from __future__ import annotations

from pathlib import Path

from generator.routing import descend_module


def test_descend_into_matching_subsystem_and_strip_prefix(tmp_path: Path):
    package = tmp_path / "directory" / "identitygovernance" / "accessreview"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("", encoding="utf-8")

    module, stem = descend_module(
        "office365.directory.identitygovernance",
        "AccessReviewContextDataBase",
        str(tmp_path),
    )

    assert module == "office365.directory.identitygovernance.accessreview"
    assert stem == "context_data_base"


def test_no_descent_without_a_matching_package(tmp_path: Path):
    module, stem = descend_module("office365.directory", "AccessReviewError", str(tmp_path))

    assert module == "office365.directory"
    assert stem == "access_review_error"


def test_longest_matching_package_wins(tmp_path: Path):
    for name in ("access", "accessreview"):
        package = tmp_path / "directory" / name
        package.mkdir(parents=True)
        (package / "__init__.py").write_text("", encoding="utf-8")

    module, stem = descend_module("office365.directory", "AccessReviewInstance", str(tmp_path))

    assert module == "office365.directory.accessreview"
    assert stem == "instance"
