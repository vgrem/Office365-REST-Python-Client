"""Tests for the Office Open XML content fallback in post-migration verification.

SharePoint re-serializes Office documents on upload (document property
promotion/demotion rewrites ``docProps/``, ``customXml/`` and ``[trash]/``), so a
raw md5 of a client-side REST round-trip is not stable. Verification falls back to
a canonical package comparison for those files; a difference outside the
server-owned parts is still a real mismatch.
"""

from __future__ import annotations

import io
import zipfile

from office365.migration.base import MigrationItem
from office365.migration.manifest import Manifest
from office365.migration.validators import verify


def _office_bytes(parts: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, content in parts.items():
            archive.writestr(name, content)
    return buffer.getvalue()


class _Adapter:
    """Minimal adapter pair exposing ``read`` + ``checksum`` for the fallback."""

    def __init__(self, items, payloads, checksums):
        self._items = list(items)
        self._payloads = payloads
        self._checksums = checksums

    def list_items(self, progress=None):
        return list(self._items)

    def read(self, item):
        return self._payloads[item.dest_path]

    def checksum(self, item):
        return self._checksums.get(item.dest_path, "")

    def close(self):
        pass


class _Target(_Adapter):
    def list_paths(self):
        return sorted(self._payloads)

    def exists(self, item):
        return item.dest_path in self._payloads

    def write(self, item, payload):
        self._payloads[item.dest_path] = payload


def _run(source_payload, target_payload, dest_path="report.xlsx"):
    item = MigrationItem(source_path=f"/src/{dest_path}", dest_path=dest_path)
    manifest = Manifest([item])
    source = _Adapter([item], {dest_path: source_payload}, {dest_path: "src-sum"})
    target = _Target([item], {dest_path: target_payload}, {dest_path: "tgt-sum"})
    return verify(source, target, manifest)


def test_office_reserialization_is_a_caveat_not_a_mismatch():
    source = _office_bytes({"xl/workbook.xml": b"book", "docProps/core.xml": b"v1"})
    target = _office_bytes(
        {
            "xl/workbook.xml": b"book",
            "docProps/core.xml": b"v2",
            "[trash]/0000.dat": b"moved",
        }
    )

    report = _run(source, target)

    assert report.mismatches == []
    assert report.ok
    assert not report.complete
    assert any("Office" in entry for entry in report.unverifiable)


def test_non_office_mismatch_has_no_fallback():
    report = _run(b"hello", b"hellp", dest_path="notes.txt")

    assert report.mismatches == ["content mismatch: notes.txt"]


def test_office_named_garbage_is_a_mismatch():
    report = _run(b"not-a-zip", b"also-not-a-zip")

    assert report.mismatches == ["content mismatch: report.xlsx"]
