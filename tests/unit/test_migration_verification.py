"""Tests for the deepened post-migration validator."""

from __future__ import annotations

from office365.migration.base import MigrationItem, MigrationOptions, PermissionEntry
from office365.migration.manifest import Manifest
from office365.migration.validators import verify


class _Source:
    """Source exposing the optional metadata/permission read hooks."""

    def __init__(self, items, checksums=None, metadata=None, permissions=None):
        self._items = items
        self._checksums = checksums or {}
        self._metadata = metadata
        self._permissions = permissions

    def list_items(self, progress=None):
        return list(self._items)

    def read(self, item):
        return b""

    def checksum(self, item):
        return self._checksums.get(item.dest_path, "")

    def apply_timestamps(self, item):
        """Present because the plan-time forecast probes the *apply* hooks.

        This fake is read-side only, but a pair that reports timestamps on read while
        refusing to write them is not a shape any real adapter has, and ``plan()``
        would reject the flag before the verification under test ever ran.
        """

    def read_metadata(self, item):
        return (self._metadata or {}).get(item.dest_path)

    def read_permissions(self, item):
        return (self._permissions or {}).get(item.dest_path, [])

    def close(self):
        pass


class _Target:
    """Target exposing the optional metadata/permission read hooks."""

    def __init__(self, paths, checksums=None, metadata=None, permissions=None):
        self._paths = set(paths)
        self._checksums = checksums or {}
        self._metadata = metadata
        self._permissions = permissions

    def exists(self, item):
        return item.dest_path in self._paths

    def write(self, item, payload):
        self._paths.add(item.dest_path)

    def list_paths(self):
        return sorted(self._paths)

    def checksum(self, item):
        return self._checksums.get(item.dest_path, "")

    def apply_timestamps(self, item):
        """Present because the plan-time forecast probes the *apply* hooks.

        This fake is read-side only, but a pair that reports timestamps on read while
        refusing to write them is not a shape any real adapter has, and ``plan()``
        would reject the flag before the verification under test ever ran.
        """

    def read_metadata(self, item):
        return (self._metadata or {}).get(item.dest_path)

    def read_permissions(self, item):
        return (self._permissions or {}).get(item.dest_path, [])

    def close(self):
        pass


class _PlainTarget:
    """Target with only the abstract contract (no fidelity read hooks)."""

    def __init__(self, paths, checksums=None):
        self._paths = set(paths)
        self._checksums = checksums or {}

    def exists(self, item):
        return item.dest_path in self._paths

    def write(self, item, payload):
        self._paths.add(item.dest_path)

    def list_paths(self):
        return sorted(self._paths)

    def checksum(self, item):
        return self._checksums.get(item.dest_path, "")

    def close(self):
        pass


def _manifest(*dests):
    return Manifest([MigrationItem(source_path=f"/src/{d}", dest_path=d) for d in dests])


def test_presence_splits_missing_and_extra():
    manifest = _manifest("a.txt", "b.txt")
    source = _Source(manifest.items, checksums={"a.txt": "x", "b.txt": "x"})
    target = _Target(["b.txt", "c.txt"], checksums={"b.txt": "x"})

    report = verify(source, target, manifest)

    assert report.missing == ["a.txt"]
    assert report.extra == ["c.txt"]
    assert not report.ok
    assert report.source_count == 2  # noqa: PLR2004
    assert report.target_count == 2  # noqa: PLR2004


def test_uncomparable_checksum_is_unverifiable_not_a_mismatch():
    manifest = _manifest("a.txt")
    source = _Source(manifest.items, checksums={"a.txt": "src"})
    target = _Target(["a.txt"], checksums={})  # e.g. a record target exposes no hash

    report = verify(source, target, manifest)

    assert report.ok  # no discrepancy, but
    assert not report.complete  # the content check could not run
    assert report.checked == 0
    assert any("no checksum" in entry for entry in report.unverifiable)


def test_approval_state_mismatch_reported():
    # A draft file that landed approved is a real fidelity loss (it is visible on the
    # target), so the metadata diff compares the content-approval status too.
    manifest = _manifest("a.txt")
    source = _Source(manifest.items, checksums={"a.txt": "x"}, metadata={"a.txt": {"moderation_status": "0"}})
    target = _Target(["a.txt"], checksums={"a.txt": "x"}, metadata={"a.txt": {"moderation_status": "2"}})

    report = verify(source, target, manifest, options=MigrationOptions(preserve_timestamps=True))

    assert report.mismatches == ["approval state mismatch: a.txt"]
    assert not report.ok


def test_approval_state_unverifiable_when_the_target_reports_none():
    # A target library without moderation enabled cannot report a status: the
    # difference is unknown rather than equal.
    manifest = _manifest("a.txt")
    modified = {"modified": "2020-01-01T00:00:00Z"}
    source = _Source(
        manifest.items, checksums={"a.txt": "x"}, metadata={"a.txt": {**modified, "moderation_status": "0"}}
    )
    target = _Target(["a.txt"], checksums={"a.txt": "x"}, metadata={"a.txt": modified})

    report = verify(source, target, manifest, options=MigrationOptions(preserve_timestamps=True))

    assert report.mismatches == []
    assert not report.complete
    assert any("approval state" in entry for entry in report.unverifiable)


def test_attachment_system_metadata_reported_once_not_per_item():
    record = MigrationItem(source_path="/src/r", dest_path="r")
    attachment = MigrationItem(source_path="/src/r/att.txt", dest_path="r/att.txt", item_type="attachment")
    manifest = Manifest([record, attachment])
    source = _Source(
        manifest.items,
        checksums={"r": "x", "r/att.txt": "y"},
        metadata={"r": {"modified": "2020-01-01T00:00:00Z"}},
    )
    target = _Target(
        ["r", "r/att.txt"],
        checksums={"r": "x", "r/att.txt": "y"},
        metadata={"r": {"modified": "2020-01-01T00:00:00Z"}},
    )

    report = verify(source, target, manifest, options=MigrationOptions(preserve_timestamps=True))

    assert report.mismatches == []
    assert report.ok  # the record's timestamp matched; the attachment is content-only
    assert not any("no metadata" in entry for entry in report.unverifiable)
    assert any(entry.startswith("attachments:") for entry in report.unverifiable)


def test_permissions_match_is_ok():
    perms = {"a.txt": [PermissionEntry("alice@contoso.com", ["Read", "Edit"])]}
    manifest = _manifest("a.txt")
    source = _Source(manifest.items, checksums={"a.txt": "x"}, permissions=perms)
    target = _Target(["a.txt"], checksums={"a.txt": "x"}, permissions=perms)

    report = verify(source, target, manifest, options=MigrationOptions(preserve_permissions=True))

    assert report.ok
    assert report.complete


def test_permission_check_unverifiable_without_target_hook():
    manifest = _manifest("a.txt")
    source = _Source(manifest.items, checksums={"a.txt": "x"})
    target = _PlainTarget(["a.txt"], checksums={"a.txt": "x"})

    report = verify(source, target, manifest, options=MigrationOptions(preserve_permissions=True))

    assert any("read_permissions" in entry for entry in report.unverifiable)
    assert not report.complete


def _folder_manifest(*dests):
    return Manifest([MigrationItem(source_path=f"/src/{d}", dest_path=d, item_type="folder") for d in dests])


def test_a_folder_whose_values_were_migrated_is_content_checked():
    # A document library folder carries its own column values: a document set's
    # metadata is part of what was migrated, not an attribute of the container.
    manifest = _folder_manifest("Area/")
    source = _Source(manifest.items, checksums={"Area/": "src"})
    target = _Target(["Area/"], checksums={"Area/": "dst"})
    source.supports_folder_records = True
    target.supports_folder_records = True

    report = verify(source, target, manifest)

    assert report.mismatches == ["content mismatch: Area/"]
    assert not report.ok


def test_a_folders_system_metadata_mismatch_is_reported():
    manifest = _folder_manifest("Area/")
    source = _Source(
        manifest.items,
        checksums={"Area/": "x"},
        metadata={"Area/": {"created": "2021-03-04T05:06:07+00:00", "modified": "2021-03-05T06:07:08+00:00"}},
    )
    target = _Target(
        ["Area/"],
        checksums={"Area/": "x"},
        metadata={"Area/": {"created": "2021-03-04T05:06:07+00:00", "modified": "2022-01-01T00:00:00+00:00"}},
    )
    source.supports_folder_records = True
    target.supports_folder_records = True

    report = verify(source, target, manifest, options=MigrationOptions(preserve_timestamps=True))

    assert report.mismatches == ["timestamp mismatch (modified): Area/"]
    assert not report.ok


def test_versions_are_always_unverifiable():
    manifest = _manifest("a.txt")
    source = _Source(manifest.items, checksums={"a.txt": "x"})
    target = _Target(["a.txt"], checksums={"a.txt": "x"})

    report = verify(source, target, manifest, options=MigrationOptions(preserve_versions=True))

    assert any("versions" in entry for entry in report.unverifiable)
    assert report.ok  # nothing contradicted, but not fully verifiable
    assert not report.complete


def test_job_verify_uses_its_options():
    from office365.migration.job import MigrationJob

    item = MigrationItem(source_path="/src/a.txt", dest_path="a.txt")
    source = _Source(
        [item],
        checksums={"a.txt": "x"},
        metadata={"a.txt": {"modified": "2020-01-01T00:00:00Z"}},
    )
    target = _Target(
        ["a.txt"],
        checksums={"a.txt": "x"},
        metadata={"a.txt": {"modified": "2024-06-01T00:00:00Z"}},
    )
    job = MigrationJob(source, target, options=MigrationOptions(preserve_timestamps=True))
    job.plan()

    report = job.verify()

    assert not report.ok
    assert any("timestamp mismatch" in entry for entry in report.mismatches)
