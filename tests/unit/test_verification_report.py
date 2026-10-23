"""Tests for the shared VerificationReport buckets and properties."""

from __future__ import annotations

from office365.runtime.verification import VerificationReport


def test_empty_report_is_ok_and_complete():
    report = VerificationReport()

    assert report.ok
    assert report.complete
    assert report.summary().startswith("OK")


def test_to_dict_is_serializable_and_mirrors_properties():
    report = VerificationReport(
        source_count=2,
        target_count=2,
        checked=1,
        missing=["a.txt"],
        extra=["c.txt"],
        mismatches=["content mismatch: b.txt"],
        unverifiable=["versions: not supported"],
    )

    data = report.to_dict()

    assert data["missing"] == ["a.txt"]
    assert data["extra"] == ["c.txt"]
    assert data["mismatches"] == ["content mismatch: b.txt"]
    assert data["unverifiable"] == ["versions: not supported"]
    assert data["ok"] is False
    assert data["complete"] is False
    # lists are copied, not aliased
    report.missing.append("z.txt")
    assert data["missing"] == ["a.txt"]
