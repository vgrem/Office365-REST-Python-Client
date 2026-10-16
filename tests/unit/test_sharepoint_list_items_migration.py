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
from office365.migration.map import ContentTypeMap
from office365.migration.sharepoint.adapters import (
    DEFAULT_LIST_IDENTITY_FIELD,
    SharePointListSource,
    SharePointListTarget,
    _content_checksum,
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


class _SourceFields:
    def __init__(self, fields=None):
        self._fields = fields or []

    def get(self):
        return self

    def execute_query(self):
        return self._fields


class _SourceSiteUser:
    def __init__(self, login_name):
        self.login_name = login_name
        self.title = login_name
        self.properties = {}


class _SourceUserLookup:
    def __init__(self, user):
        self._user = user

    def get(self):
        return self

    def execute_query(self):
        return self._user


class _SourceSiteUsers:
    def __init__(self, users):
        self._users = users

    def get_by_id(self, user_id):
        return _SourceUserLookup(_SourceSiteUser(self._users[int(user_id)]))


class _SourceWeb:
    def __init__(self, users):
        self.site_users = _SourceSiteUsers(users)


class _SourceContext:
    def __init__(self, users):
        self.web = _SourceWeb(users)


class _SourceList:
    def __init__(self, items, fields=None, users=None):
        self.title = "Docs"
        self.items = _SourceItems(items)
        self.fields = _SourceFields(fields)
        if users is not None:
            self.context = _SourceContext(users)


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


def test_list_source_annotates_person_columns_with_the_login():
    # A site-user id is meaningless on the target, so the source replaces the
    # Person column's companion id with the portable login for the target to resolve.
    items = [_Item(1, {"Id": 1, "Title": "A", "OwnerId": 7, "OwnerStringId": "7"})]
    source = SharePointListSource(
        cast("SPList", _SourceList(items, fields=[_Field("Owner", "User")], users={7: _LOGIN}))
    )
    planned = source.list_items()

    record = source.read(planned[0])
    assert record["OwnerId"] == _LOGIN
    # the read-only companion must not ride along, or REST keeps the source id
    assert "OwnerStringId" not in record


def test_list_source_ignores_builtin_author_editor_as_person_columns():
    fields = [_Field("Author", "User"), _Field("Editor", "User"), _Field("Owner", "User")]
    source = SharePointListSource(cast("SPList", _SourceList([], fields=fields)))

    assert source._user_columns() == {"Owner"}


def test_list_source_drops_a_person_value_it_cannot_resolve():
    items = [_Item(1, {"Id": 1, "Title": "A", "OwnerId": 42})]
    source = SharePointListSource(
        cast("SPList", _SourceList(items, fields=[_Field("Owner", "User")], users={7: _LOGIN}))
    )
    planned = source.list_items()

    record = source.read(planned[0])
    assert "OwnerId" not in record
    assert any("Owner" in w for w in source.warnings)


def test_list_source_drops_non_scalar_values_and_warns():
    # A full read also returns navigation properties (``ParentList``) and typed
    # values (``PredecessorsId``) whose JSON objects carry no type name; the REST
    # create batch rejects them, so the projection drops them and says so.
    items = [
        _Item(1, {"Id": 1, "Title": "A", "ParentList": object(), "PredecessorsId": {}}),
    ]
    source = SharePointListSource(cast("SPList", _SourceList(items)))
    planned = source.list_items()

    record = source.read(planned[0])
    assert record["Title"] == "A"
    assert "ParentList" not in record
    assert "PredecessorsId" not in record
    assert any("non-scalar" in w for w in source.warnings)


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
    def __init__(self, web=None):
        self.has_pending_request = False
        self.batches = 0
        self.web = web

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
    def __init__(self, target_id, identity, attachments=(), properties=None):
        self.id = target_id
        entries = list(attachments)
        self.properties = {
            "Id": target_id,
            DEFAULT_LIST_IDENTITY_FIELD: identity,
            "AttachmentFiles": entries,
        }
        if properties:
            self.properties.update(properties)
        self.attachment_files = _TargetAttachments(entries=entries)
        self.get_calls = 0

    def get(self):
        self.get_calls += 1
        return _Executable()


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


class _Field:
    """A target column as returned by a ``fields`` projection."""

    def __init__(self, internal_name, type_as_string, lookup_list=None):
        self.properties = {"InternalName": internal_name, "TypeAsString": type_as_string}
        if lookup_list is not None:
            self.properties["LookupList"] = lookup_list

    @property
    def internal_name(self):
        return self.properties.get("InternalName")

    @property
    def type_as_string(self):
        return self.properties.get("TypeAsString")


class _TargetFields:
    """The target list's ``fields`` collection (projection + ``ensure``)."""

    def __init__(self, owner, fields=None):
        self._owner = owner
        self._fields = fields or []

    def select(self, columns):
        return self

    def get(self):
        return self

    def execute_query(self):
        return self._fields

    def ensure(self, parameters):
        self._owner.identity_fields.append(parameters)
        return _Executable()


class _ReferencedItems:
    def __init__(self, items):
        self._items = items

    def select(self, columns):
        return self

    def get_all(self):
        return self

    def execute_query(self):
        return self._items


class _ReferencedList:
    def __init__(self, items):
        self.items = _ReferencedItems(items)


class _SiteUser:
    def __init__(self, user_id, login_name):
        self.id = user_id
        self.login_name = login_name


class _EnsureUserResult:
    def __init__(self, user):
        self._user = user

    def execute_query(self):
        return self._user


class _Web:
    """Just enough of a web for ``lists.get_by_id`` and ``site_users`` (typed values)."""

    def __init__(self, lists_by_id=None, users=None):
        self._lists_by_id = lists_by_id or {}
        self._users_by_id = users or {}
        self.ensured = []

    @property
    def lists(self):
        return self

    def get_by_id(self, list_id):
        return _ReferencedList(self._lists_by_id.get(list_id, []))

    @property
    def site_users(self):
        return self

    def get(self):
        return self

    def execute_query(self):
        return [_SiteUser(user_id, login) for user_id, login in self._users_by_id.items()]

    def ensure_user(self, login):
        self.ensured.append(login)
        for user_id, user_login in self._users_by_id.items():
            if user_login == login:
                return _EnsureUserResult(_SiteUser(user_id, login))
        raise ValueError(f"unknown user {login!r}")


class _TargetList:
    def __init__(self, rows=None, fields=None, web=None):
        self.title = "TargetList"
        self.context = _FakeContext(web=web)
        self.rows = rows or []
        self.queued = []
        self.identity_fields = []
        self.items = _TargetItems(self)
        self.fields = _TargetFields(self, fields)

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


def test_list_target_remaps_content_type_id_from_the_map():
    # A recreated list content type gets a fresh server-assigned id, so the source
    # item's ``ContentTypeId`` must be rewritten before it is written.
    target_list = _TargetList()
    mapping = ContentTypeMap({"0x0100SOURCE": "0x0100TARGET"})
    target = SharePointListTarget(cast("SPList", target_list), content_type_map=mapping)

    payload = {"Title": "A", "ContentTypeId": "0x0100SOURCE"}
    target.write(MigrationItem("Docs/1", "1", item_type="record"), payload)

    assert target_list.queued == [{"Title": "A", "ContentTypeId": "0x0100TARGET", DEFAULT_LIST_IDENTITY_FIELD: "1"}]
    # the caller's payload is left untouched
    assert payload == {"Title": "A", "ContentTypeId": "0x0100SOURCE"}


def test_list_target_leaves_unmapped_content_type_id_alone():
    target_list = _TargetList()
    mapping = ContentTypeMap({"0x0100SOURCE": "0x0100TARGET"})
    target = SharePointListTarget(cast("SPList", target_list), content_type_map=mapping)

    target.write(MigrationItem("Docs/1", "1", item_type="record"), {"ContentTypeId": "0x0101"})

    assert target_list.queued == [{"ContentTypeId": "0x0101", DEFAULT_LIST_IDENTITY_FIELD: "1"}]


def test_list_target_content_checksum_matches_source_for_equal_content():
    # Server-assigned, remapped and separately-verified columns must not make the
    # read-back disagree with the source's content projection.
    row = _TargetRow(
        10,
        "1",
        properties={
            "Title": "Alpha",
            "Quantity": 3,
            "GUID": "target-guid",
            "ContentTypeId": "0x0100TARGET",
            "Created": "2020-01-01T00:00:00Z",
            "Modified": "2026-01-01T00:00:00Z",
            "AuthorId": 99,
            "EditorId": 99,
            "OData__UIVersionString": "7.0",
        },
    )
    target = SharePointListTarget(cast("SPList", _TargetList(rows=[row])))

    checksum = target.checksum(MigrationItem("Docs/1", "1", item_type="record"))

    assert checksum == _content_checksum({"Title": "Alpha", "Quantity": 3})
    assert row.get_calls == 1


def test_list_target_content_checksum_detects_a_content_difference():
    row = _TargetRow(10, "1", properties={"Title": "Alpha"})
    target = SharePointListTarget(cast("SPList", _TargetList(rows=[row])))

    checksum = target.checksum(MigrationItem("Docs/1", "1", item_type="record"))

    assert checksum != _content_checksum({"Title": "Beta"})


def test_content_checksum_is_order_independent_and_excludes_bookkeeping():
    first = {"Title": "A", "Id": 1, "GUID": "x", "Quantity": 2}
    second = {"Quantity": 2, "Title": "A", "GUID": "y", "Id": 99}

    assert _content_checksum(first) == _content_checksum(second)
    assert _content_checksum(first) != _content_checksum({"Title": "A", "Quantity": 3})


# ── Typed values: lookup column value remapping ───────────────────────────────

_LOOKUP_LIST_ID = "ed0abd71-7d64-429a-9de7-7dfabbac6aa7"
_LOOKUP_SCHEMA_LIST_ID = "{" + _LOOKUP_LIST_ID + "}"


def _lookup_target(rows=None, referenced=None, fields=None):
    web = _Web({_LOOKUP_LIST_ID: referenced if referenced is not None else []})
    target_list = _TargetList(rows=rows, fields=fields, web=web)
    return target_list, SharePointListTarget(cast("SPList", target_list))


def test_list_target_ignores_non_lookup_columns():
    # A User column has a ``LookupList`` too (UserInfo), but only genuine Lookup
    # columns carry an item id we must remap; the person id is left for stage 2.
    fields = [_Field("Owner", "User", "{0c574566-cae0-4e81-a454-616804f55a5a}")]
    target_list, target = _lookup_target(fields=fields)

    target.write(MigrationItem("Docs/1", "1", item_type="record"), {"Title": "A", "OwnerId": 12})

    assert target_list.queued == [{"Title": "A", "OwnerId": 12, DEFAULT_LIST_IDENTITY_FIELD: "1"}]


def test_list_target_remaps_lookup_value_to_the_target_item_id():
    # Source item 2 ("Marketing") was migrated as target id 1, so the raw source
    # id (2) must be rewritten; leaving it would point at the wrong row.
    referenced = [
        _Item(1, {DEFAULT_LIST_IDENTITY_FIELD: "2"}),
        _Item(2, {DEFAULT_LIST_IDENTITY_FIELD: "3"}),
    ]
    fields = [_Field("Dept", "Lookup", _LOOKUP_SCHEMA_LIST_ID)]
    target_list, target = _lookup_target(referenced=referenced, fields=fields)

    target.write(MigrationItem("Docs/1", "1", item_type="record"), {"Title": "Alpha", "DeptId": 2})

    assert target_list.queued == [{"Title": "Alpha", "DeptId": 1, DEFAULT_LIST_IDENTITY_FIELD: "1"}]


def test_list_target_drops_unresolved_lookup_and_warns_once():
    # The referenced item was not migrated (no source id 2 on the target), so the
    # value is dropped rather than written as a wrong/empty id; the gap is reported
    # once even when several items share the same unresolved value.
    referenced = [_Item(5, {DEFAULT_LIST_IDENTITY_FIELD: "9"})]
    fields = [_Field("Dept", "Lookup", _LOOKUP_SCHEMA_LIST_ID)]
    target_list, target = _lookup_target(referenced=referenced, fields=fields)

    target.write(MigrationItem("Docs/1", "1", item_type="record"), {"Title": "A", "DeptId": 2})
    target.write(MigrationItem("Docs/2", "2", item_type="record"), {"Title": "B", "DeptId": 2})

    assert target_list.queued == [
        {"Title": "A", DEFAULT_LIST_IDENTITY_FIELD: "1"},
        {"Title": "B", DEFAULT_LIST_IDENTITY_FIELD: "2"},
    ]
    assert sum("'Dept'" in w for w in target.warnings) == 1


def test_list_target_reports_an_unreadable_lookup_list():
    # A missing referenced list must degrade gracefully (no crash) and be surfaced.
    fields = [_Field("Dept", "Lookup", _LOOKUP_SCHEMA_LIST_ID)]
    target_list, target = _lookup_target(fields=fields)

    target.write(MigrationItem("Docs/1", "1", item_type="record"), {"Title": "A", "DeptId": 2})

    assert target_list.queued == [{"Title": "A", DEFAULT_LIST_IDENTITY_FIELD: "1"}]
    assert any("lookup" in w for w in target.warnings)


def test_list_target_content_checksum_canonicalizes_lookup_id():
    # Verification must compare like for like: the target's fresh item holds the
    # target id (1), so it is mapped back to the source id (2) before hashing.
    referenced = [_Item(1, {DEFAULT_LIST_IDENTITY_FIELD: "2"})]
    fields = [_Field("Dept", "Lookup", _LOOKUP_SCHEMA_LIST_ID)]
    row = _TargetRow(10, "1", properties={"Title": "Alpha", "DeptId": 1})
    _, target = _lookup_target(rows=[row], referenced=referenced, fields=fields)

    checksum = target.checksum(MigrationItem("Docs/1", "1", item_type="record"))

    assert checksum == _content_checksum({"Title": "Alpha", "DeptId": 2})


# ── Typed values: person column value remapping ──────────────────────────────

_USERINFO_LIST_ID = "{0c574566-cae0-4e81-a454-616804f55a5a}"
_LOGIN = "vgrem@mediadev8.onmicrosoft.com"


def test_list_target_ignores_builtin_author_editor_as_person_columns():
    fields = [_Field("Author", "User"), _Field("Editor", "User"), _Field("Owner", "User")]
    target = SharePointListTarget(cast("SPList", _TargetList(fields=fields, web=_Web())))

    assert target._user_columns() == {"Owner"}


def test_list_target_remaps_person_login_to_target_site_user_id():
    # The source annotates the Person column with the portable login; the target
    # resolves it to its *own* site-user id via EnsureUser (ids are per site).
    web = _Web(users={7: _LOGIN})
    target_list = _TargetList(fields=[_Field("Owner", "User", _USERINFO_LIST_ID)], web=web)
    target = SharePointListTarget(cast("SPList", target_list))

    target.write(MigrationItem("Docs/1", "1", item_type="record"), {"Title": "A", "OwnerId": _LOGIN})

    assert target_list.queued == [{"Title": "A", "OwnerId": 7, DEFAULT_LIST_IDENTITY_FIELD: "1"}]
    assert web.ensured == [_LOGIN]


def test_list_target_drops_unresolvable_person_login():
    web = _Web(users={7: _LOGIN})
    target_list = _TargetList(fields=[_Field("Owner", "User", _USERINFO_LIST_ID)], web=web)
    target = SharePointListTarget(cast("SPList", target_list))

    target.write(MigrationItem("Docs/1", "1", item_type="record"), {"Title": "A", "OwnerId": "ghost@example.com"})

    assert target_list.queued == [{"Title": "A", DEFAULT_LIST_IDENTITY_FIELD: "1"}]
    assert any("ghost@example.com" in w for w in target.warnings)


def test_list_target_content_checksum_canonicalizes_person_id_to_login():
    web = _Web(users={7: _LOGIN})
    row = _TargetRow(10, "1", properties={"Title": "Alpha", "OwnerId": 7, "OwnerStringId": "7"})
    target_list = _TargetList(rows=[row], fields=[_Field("Owner", "User", _USERINFO_LIST_ID)], web=web)
    target = SharePointListTarget(cast("SPList", target_list))

    checksum = target.checksum(MigrationItem("Docs/1", "1", item_type="record"))

    assert checksum == _content_checksum({"Title": "Alpha", "OwnerId": _LOGIN})
