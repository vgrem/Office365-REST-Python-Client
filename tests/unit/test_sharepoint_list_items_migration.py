"""Offline tests for list-item migration: field projection, attachments and identity.

These reproduce the defects a live probe found:

* the source projected the collection's literal ``select`` (``["*", ...]``) instead
  of the loaded fields, so migrated items carried no field values at all;
* attachments were dropped silently;
* verification could not pair source and target list items.

The target now stamps every migrated item with a source-id marker so a re-run skips
what is already there (idempotent ``SKIP``) and ``list_paths()`` reconciles both
records and attachments against the source.
"""

from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from office365.sharepoint.lists.list import List as SPList

from office365.migration.base import MigrationItem
from office365.migration.sharepoint.adapters import (
    DEFAULT_LIST_IDENTITY_FIELD,
    SharePointListSource,
    SharePointListTarget,
)


class _QueryOptions:
    def __init__(self, select):
        self.select = list(select)
        self.expand: list[str] = []


class _Loaded(list):
    """A loaded page exposing the query options the projection used to read."""

    def __init__(self, items, select):
        super().__init__(items)
        self.query_options = _QueryOptions(select)


class _Item:
    def __init__(self, item_id, properties):
        self.id = item_id
        self.properties = properties


class _Result:
    def __init__(self, value):
        self.value = value

    def execute_query(self):
        return self


class _Attachment:
    """A source attachment (``AttachmentFiles`` entry)."""

    def __init__(self, name, content):
        self.file_name = name
        self._content = content

    def get_content(self):
        return _Result(self._content)


class _SourceItems:
    def __init__(self, items):
        self._items = items
        self._select = None

    def select(self, columns):
        self._select = list(columns)
        return self

    def expand(self, _expands):
        return self

    def get_all(self):
        return self

    def execute_query(self):
        return _Loaded(self._items, self._select or [])


class _SourceList:
    def __init__(self, items):
        self.title = "Docs"
        self.items = _SourceItems(items)


# ── Source projection ────────────────────────────────────────────────────────


def test_list_source_projects_all_field_values():
    items = [
        _Item(1, {"Id": 1, "Title": "A", "Notes": "alpha", "Modified": "2026-01-01", "AttachmentFiles": []}),
        _Item(2, {"Id": 2, "Title": "B", "Notes": "bravo", "Modified": "2026-01-02", "AttachmentFiles": []}),
    ]
    source = SharePointListSource(cast("SPList", _SourceList(items)))
    planned = source.list_items()

    assert [item.item_type for item in planned] == ["record", "record"]
    first = source.read(planned[0])
    assert first["Title"] == "A"
    assert first["Notes"] == "alpha"
    # the literal "*" placeholder must never leak into the payload
    assert first.get("*") is None


def test_list_source_captures_attachments_after_records():
    attachment = _Attachment("spec.txt", b"hello")
    items = [
        _Item(1, {"Id": 1, "Title": "A", "AttachmentFiles": [attachment]}),
        _Item(2, {"Id": 2, "Title": "B", "AttachmentFiles": []}),
    ]
    source = SharePointListSource(cast("SPList", _SourceList(items)))
    planned = source.list_items()

    # attachments are queued after every record so the target can create parents first
    assert [item.item_type for item in planned] == ["record", "record", "attachment"]
    attachment_item = planned[-1]
    assert attachment_item.dest_path == "1/spec.txt"
    assert source.read(attachment_item) == b"hello"
    assert source.checksum(attachment_item) == hashlib.md5(b"hello").hexdigest()


# ── Target: identity marker, records, attachments, verification ──────────────


class _Executable:
    def execute_query(self):
        return self


class _FakeContext:
    def __init__(self):
        self.has_pending_request = False
        self.batches = 0

    def execute_batch(self, items_per_batch=100, concurrency=1):
        self.batches += 1
        self.has_pending_request = False

    def execute_query(self):
        pass


class _TargetAttachments:
    def __init__(self, files=None, entries=None):
        self.added = []
        self._files = dict(files or {})
        self._entries = entries if entries is not None else []

    def add(self, info):
        self.added.append(info)
        self._files[info["filename"]] = info["content"]
        self._entries.append(_Attachment(info["filename"], info["content"]))
        return _Executable()

    def get_by_filename(self, filename):
        return _Attachment(filename, self._files.get(filename))


class _TargetRow:
    def __init__(self, target_id, identity, attachments=()):
        self.id = target_id
        entries = list(attachments)
        self.properties = {
            "Id": target_id,
            DEFAULT_LIST_IDENTITY_FIELD: identity,
            "AttachmentFiles": entries,
        }
        self.attachment_files = _TargetAttachments(entries=entries)


class _TargetItems:
    def __init__(self, owner):
        self._owner = owner
        self._select = None
        self._expand = None

    def select(self, columns):
        self._select = list(columns)
        return self

    def expand(self, expands):
        self._expand = list(expands)
        return self

    def get_all(self):
        return self

    def get(self):
        return self

    def execute_query(self):
        return self._owner.rows

    def queue_records(self, records, progress=None):
        self._owner.queued.extend(records)
        self._owner.context.has_pending_request = True

    def clear(self):
        self._owner.queued.clear()


class _TargetList:
    def __init__(self, rows=None):
        self.title = "TargetList"
        self.context = _FakeContext()
        self.rows = rows or []
        self.queued = []
        self.identity_fields = []
        self.items = _TargetItems(self)
        self.fields = self  # ``fields.ensure(...)`` returns self, which is executable

    def ensure(self, parameters):
        self.identity_fields.append(parameters)
        return self

    def execute_query(self):
        return self


def test_list_target_marks_records_and_lists_paths():
    attachment = _Attachment("spec.txt", b"hello")
    target_list = _TargetList(rows=[_TargetRow(10, "1", attachments=[attachment])])
    target = SharePointListTarget(cast("SPList", target_list))

    item = MigrationItem(source_path="Docs/1", dest_path="1", item_type="record")
    target.write(item, {"Title": "A"})

    assert [field.Title for field in target_list.identity_fields] == [DEFAULT_LIST_IDENTITY_FIELD]
    assert target_list.queued == [{"Title": "A", DEFAULT_LIST_IDENTITY_FIELD: "1"}]

    paths = target.list_paths()
    assert "1" in paths
    assert "1/spec.txt" in paths


def test_list_target_writes_attachment_via_identity():
    parent = _TargetRow(10, "1")
    target_list = _TargetList(rows=[parent])
    target = SharePointListTarget(cast("SPList", target_list))

    item = MigrationItem(source_path="Docs/1/spec.txt", dest_path="1/spec.txt", item_type="attachment")
    target.write(item, b"hello")

    assert parent.attachment_files.added == [{"filename": "spec.txt", "content": b"hello"}]
    assert target.checksum(item) == hashlib.md5(b"hello").hexdigest()
    assert target.exists(item) is True
    assert target.exists(MigrationItem("Docs/1/x.txt", "1/x.txt", item_type="attachment")) is False


def test_list_target_exists_recognizes_records_by_identity():
    target_list = _TargetList(rows=[_TargetRow(10, "1")])
    target = SharePointListTarget(cast("SPList", target_list))

    assert target.exists(MigrationItem("Docs/1", "1", item_type="record")) is True
    assert target.exists(MigrationItem("Docs/2", "2", item_type="record")) is False


def test_list_target_flushes_records_before_attachments():
    parent = _TargetRow(10, "1")
    target_list = _TargetList(rows=[parent])
    target = SharePointListTarget(cast("SPList", target_list))

    records = [MigrationItem("Docs/1", "1", item_type="record")]
    attachments = [MigrationItem("Docs/1/spec.txt", "1/spec.txt", item_type="attachment")]
    target.write_many(records + attachments, [{"Title": "A"}, b"data"])

    assert target_list.context.batches == 1
    assert target_list.queued == []
    assert parent.attachment_files.added == [{"filename": "spec.txt", "content": b"data"}]


def test_list_target_identity_can_be_opted_out():
    target_list = _TargetList(rows=[_TargetRow(10, "1")])
    target = SharePointListTarget(cast("SPList", target_list), identity_field=None)

    item = MigrationItem("Docs/1", "1", item_type="record")
    target.write(item, {"Title": "A"})

    assert target_list.identity_fields == []
    assert target_list.queued == [{"Title": "A"}]
    assert target.list_paths() == ["10"]
