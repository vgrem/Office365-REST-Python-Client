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

from office365.migration.base import MigrationItem, MigrationOptions
from office365.migration.map import ContentTypeMap
from office365.migration.sharepoint import adapters
from office365.migration.sharepoint.adapters import (
    DEFAULT_LIST_IDENTITY_FIELD,
    SharePointListSource,
    SharePointListTarget,
    _content_checksum,
    _MultiValueCreateTarget,
)
from office365.migration.sharepoint.structure import ListStructure


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
        self._filter = None

    def select(self, columns):
        self._select = list(columns)
        return self

    def expand(self, _expands):
        return self

    def filter(self, expression):
        self._filter = expression
        return self

    def get_all(self):
        return self

    def execute_query(self):
        return _Loaded(self._items, self._select or [])


class _SourceFields:
    def __init__(self, fields=None):
        self._fields = fields or []
        self._select = None

    def select(self, columns):
        self._select = list(columns)
        return self

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


def test_list_source_drops_a_person_value_it_cannot_resolve():
    items = [_Item(1, {"Id": 1, "Title": "A", "OwnerId": 42})]
    source = SharePointListSource(
        cast("SPList", _SourceList(items, fields=[_Field("Owner", "User")], users={7: _LOGIN}))
    )
    planned = source.list_items()

    record = source.read(planned[0])
    assert "OwnerId" not in record
    assert any("Owner" in w for w in source.warnings)


def test_list_source_drops_a_multi_person_value_it_cannot_resolve():
    items = [_Item(1, {"Id": 1, "Title": "A", "MultiOwnerId": {0: 42}})]
    source = SharePointListSource(
        cast("SPList", _SourceList(items, fields=[_Field("MultiOwner", "UserMulti")], users={7: _LOGIN}))
    )

    record = source.read(source.list_items()[0])
    assert "MultiOwnerId" not in record
    assert any("MultiOwner" in w for w in source.warnings)


# ── Folder column values (document libraries) ───────────────────────────────


def test_folder_records_are_read_with_a_folder_filter_and_keyed_by_url():
    # A document library folder is a list item too: its own column values (a document
    # set's metadata, a managed folder's department) must travel with the folder.
    fields = [_Field("Region", "Choice"), _Field("Title", "Text")]
    items = [
        _Item(11, {"FileRef": "/sites/x/Docs/North", "FSObjType": 1, "Region": "North", "Title": ""}),
        _Item(12, {"FileRef": "/sites/x/Docs/South", "FSObjType": 1, "Region": "South", "Title": "t"}),
    ]
    lst = _SourceList(items, fields=fields)
    source = SharePointListSource(cast("SPList", lst))

    records = source.folder_records()

    assert lst.items._filter == "FSObjType eq 1"
    assert records == {
        "/sites/x/Docs/North": {"Region": "North"},
        "/sites/x/Docs/South": {"Region": "South", "Title": "t"},
    }
    # the projection is the folder's writable columns, not a ``*`` read
    assert "FSObjType" not in lst.items._select
    assert {"ContentTypeId", "FileRef", "Region", "Title"} <= set(lst.items._select)


def test_folder_records_skip_computed_and_read_only_columns():
    fields = [
        _Field("Region", "Choice"),
        _Field("LinkFilename", "Computed"),
        _Field("Author", "User", read_only=True),
        _Field("Created", "DateTime", read_only=True),
        _Field("Secret", "Note", hidden=True),
    ]
    items = [_Item(11, {"FileRef": "/sites/x/Docs/North", "Region": "North"})]
    lst = _SourceList(items, fields=fields)

    SharePointListSource(cast("SPList", lst)).folder_records()

    projection = set(lst.items._select)
    assert "LinkFilename" not in projection
    assert "AuthorId" not in projection  # a read-only person column cannot be written
    assert "Created" not in projection
    assert "Secret" not in projection


def test_folder_records_degrade_to_no_values_when_the_read_fails():
    class _Failing(list):
        def execute_query(self):
            raise ValueError("Access denied")

    lst = _SourceList([])
    lst.items = _Failing()  # a collection whose read raises
    source = SharePointListSource(cast("SPList", lst))

    assert source.folder_records() == {}
    assert any("folder column values could not be read" in warning for warning in source.warnings)


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


def test_list_source_projects_multi_choice_values_as_a_list():
    # A live read returns a multi-choice cell as a positional mapping
    # (``{0: "red", 1: "green"}``), which the create path cannot write.
    items = [_Item(1, {"Id": 1, "Title": "A", "Tags": {0: "red", 1: "green"}})]
    fields = [_Field("Tags", "MultiChoice", allow_multiple_values=True)]
    source = SharePointListSource(cast("SPList", _SourceList(items, fields=fields)))

    planned = source.list_items()
    record = source.read(planned[0])

    assert record["Tags"] == ["red", "green"]
    assert not any("non-scalar" in w for w in source.warnings)


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
        self.update_writes = []

    def get(self):
        self.get_calls += 1
        return _Executable()

    def validate_update_list_item(self, form_values, **_kwargs):
        self.update_writes.append(dict(form_values))
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

    def __init__(
        self,
        internal_name,
        type_as_string,
        lookup_list=None,
        field_id=None,
        text_field_id=None,
        schema_xml=None,
        hidden=None,
        allow_multiple_values=None,
        read_only=None,
    ):
        self.properties = {"InternalName": internal_name, "TypeAsString": type_as_string}
        if read_only is not None:
            self.properties["ReadOnlyField"] = read_only
        if lookup_list is not None:
            self.properties["LookupList"] = lookup_list
        if field_id is not None:
            self.properties["Id"] = field_id
        if text_field_id is not None:
            self.properties["TextField"] = text_field_id
        if hidden is not None:
            self.properties["Hidden"] = hidden
        if allow_multiple_values is not None:
            self.properties["AllowMultipleValues"] = allow_multiple_values
        self._schema_xml = schema_xml

    @property
    def id(self):
        return self.properties.get("Id")

    @property
    def schema_xml(self):
        return self._schema_xml

    @property
    def internal_name(self):
        return self.properties.get("InternalName")

    @property
    def type_as_string(self):
        return self.properties.get("TypeAsString")

    @property
    def hidden(self):
        return self.properties.get("Hidden")

    @property
    def read_only_field(self):
        return self.properties.get("ReadOnlyField")


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


def test_list_target_reads_a_verified_item_once():
    row = _TargetRow(
        10,
        "1",
        properties={"Created": "2024-01-01T00:00:00Z", "Modified": "2024-01-02T00:00:00Z"},
    )
    target = SharePointListTarget(cast("SPList", _TargetList(rows=[row])))
    item = MigrationItem("Docs/1", "1", item_type="record")

    target.checksum(item)
    target.read_metadata(item)
    target.read_authorship(item)

    # One verification round asks several questions about the same unchanged item;
    # the fresh read is memoized, so it costs one request rather than one per hook.
    assert row.get_calls == 1


def test_list_target_rereads_a_verified_item_after_a_fidelity_write():
    row = _TargetRow(10, "1")
    target = SharePointListTarget(cast("SPList", _TargetList(rows=[row])))
    item = MigrationItem(
        "Docs/1", "1", item_type="record", created="2024-01-01T00:00:00Z", modified="2024-01-02T00:00:00Z"
    )

    target.checksum(item)
    target.apply_timestamps(item)
    target.checksum(item)

    # The system update changes what a read returns, so the memo is dropped.
    assert row.update_writes == [{"Created": "2024-01-01T00:00:00Z", "Modified": "2024-01-02T00:00:00Z"}]
    assert row.get_calls == 2  # noqa: PLR2004 - one read per verification pass


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


def test_list_target_content_checksum_compares_multi_choice_values():
    # The source records a bare list while the target reads a positional mapping;
    # both must project to the same content or every run reports a false mismatch.
    row = _TargetRow(10, "1", properties={"Title": "Alpha", "Tags": {0: "red", 1: "green"}})
    fields = [_Field("Tags", "MultiChoice", allow_multiple_values=True)]
    target = SharePointListTarget(cast("SPList", _TargetList(rows=[row], fields=fields)))

    checksum = target.checksum(MigrationItem("Docs/1", "1", item_type="record"))

    assert checksum == _content_checksum({"Title": "Alpha", "Tags": ["red", "green"]})


def test_list_target_content_checksum_detects_lost_multi_choice_values():
    # The defect this guards: a dropped multi-choice value was invisible to
    # verification because a positional mapping is not a checksummed scalar.
    row = _TargetRow(10, "1", properties={"Title": "Alpha"})
    fields = [_Field("Tags", "MultiChoice", allow_multiple_values=True)]
    target = SharePointListTarget(cast("SPList", _TargetList(rows=[row], fields=fields)))

    checksum = target.checksum(MigrationItem("Docs/1", "1", item_type="record"))

    assert checksum != _content_checksum({"Title": "Alpha", "Tags": ["red", "green"]})


def test_list_target_content_checksum_compares_hyperlink_values():
    # The source records the value object it read; the target reads the same shape
    # back, so both must hash identically.
    value = {"Description": "one", "Url": "https://example.com/1"}
    row = _TargetRow(10, "1", properties={"Title": "Alpha", "Link": value})
    target = SharePointListTarget(cast("SPList", _TargetList(rows=[row])))

    checksum = target.checksum(MigrationItem("Docs/1", "1", item_type="record"))

    assert checksum == _content_checksum({"Title": "Alpha", "Link": value})


def test_list_target_content_checksum_detects_a_lost_hyperlink_value():
    value = {"Description": "one", "Url": "https://example.com/1"}
    row = _TargetRow(10, "1", properties={"Title": "Alpha"})
    target = SharePointListTarget(cast("SPList", _TargetList(rows=[row])))

    checksum = target.checksum(MigrationItem("Docs/1", "1", item_type="record"))

    assert checksum != _content_checksum({"Title": "Alpha", "Link": value})


def test_list_target_content_checksum_detects_a_changed_hyperlink_description():
    row = _TargetRow(
        10, "1", properties={"Title": "Alpha", "Link": {"Description": "other", "Url": "https://example.com/1"}}
    )
    target = SharePointListTarget(cast("SPList", _TargetList(rows=[row])))

    checksum = target.checksum(MigrationItem("Docs/1", "1", item_type="record"))

    expected = {"Title": "Alpha", "Link": {"Description": "one", "Url": "https://example.com/1"}}
    assert checksum != _content_checksum(expected)


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


def test_content_checksum_treats_a_null_column_as_absent():
    # The source drops an empty multi-value column while the target reads it back
    # as ``None``; the two must reconcile as "no value", not a mismatch.
    assert _content_checksum({"Title": "A", "MultiDeptId": None}) == _content_checksum({"Title": "A"})
    # A real value on one side and null on the other is still a difference.
    assert _content_checksum({"Title": "A", "MultiDeptId": [1]}) != _content_checksum(
        {"Title": "A", "MultiDeptId": None}
    )


# ── Typed values: lookup column value remapping ───────────────────────────────

_LOOKUP_LIST_ID = "ed0abd71-7d64-429a-9de7-7dfabbac6aa7"
_LOOKUP_SCHEMA_LIST_ID = "{" + _LOOKUP_LIST_ID + "}"


def _lookup_target(rows=None, referenced=None, fields=None):
    web = _Web({_LOOKUP_LIST_ID: referenced if referenced is not None else []})
    target_list = _TargetList(rows=rows, fields=fields, web=web)
    return target_list, SharePointListTarget(cast("SPList", target_list))


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


# ── Typed values: multi-value Lookup/Person columns ──────────────────────────

_MDOE = "mdoe@mediadev8.onmicrosoft.com"


def test_list_source_treats_lookup_mult_true_as_a_multi_value_column():
    # SharePoint keeps a ``Type="Lookup" Mult="TRUE"`` schema as written and then
    # reports ``TypeAsString == "Lookup"``, so only ``AllowMultipleValues`` says the
    # column holds many values (live-verified). Reading it as single-value dropped
    # the whole collection: the ids never reached the target.
    items = [_Item(1, {"Id": 1, "Title": "A", "MultiDeptId": {0: 1, 1: 2}})]
    fields = [_Field("MultiDept", "Lookup", allow_multiple_values=True)]
    source = SharePointListSource(cast("SPList", _SourceList(items, fields=fields)))

    assert source._multi_columns() == {"MultiDept": "LookupMulti"}
    assert source.read(source.list_items()[0])["MultiDeptId"] == [1, 2]


def test_list_source_treats_user_mult_true_as_a_multi_person_column():
    items = [_Item(1, {"Id": 1, "Title": "A", "MultiOwnerId": {0: 12, 1: 7}})]
    fields = [_Field("MultiOwner", "User", allow_multiple_values=True)]
    source = SharePointListSource(cast("SPList", _SourceList(items, fields=fields, users={12: _LOGIN, 7: _MDOE})))

    assert source._multi_columns() == {"MultiOwner": "UserMulti"}
    assert source._user_columns() == set()
    assert source.read(source.list_items()[0])["MultiOwnerId"] == [_LOGIN, _MDOE]


def test_list_target_remaps_multi_lookup_ids_to_target_ids():
    # Source items 2 and 3 were migrated as target ids 1 and 2, so each id in the
    # collection is rewritten; the column is written as ``{"results": [...]}``,
    # the only shape the create batch accepts for a multi-value column.
    referenced = [
        _Item(1, {DEFAULT_LIST_IDENTITY_FIELD: "2"}),
        _Item(2, {DEFAULT_LIST_IDENTITY_FIELD: "3"}),
    ]
    fields = [_Field("MultiDept", "LookupMulti", _LOOKUP_SCHEMA_LIST_ID)]
    target_list, target = _lookup_target(referenced=referenced, fields=fields)

    target.write(MigrationItem("Docs/1", "1", item_type="record"), {"Title": "A", "MultiDeptId": [2, 3]})

    assert target_list.queued == [{"Title": "A", "MultiDeptId": {"results": [1, 2]}, DEFAULT_LIST_IDENTITY_FIELD: "1"}]


def test_list_target_remaps_multi_person_logins_to_target_ids():
    web = _Web(users={7: _LOGIN, 12: _MDOE})
    fields = [_Field("MultiOwner", "UserMulti", _USERINFO_LIST_ID)]
    target_list = _TargetList(fields=fields, web=web)
    target = SharePointListTarget(cast("SPList", target_list))

    target.write(
        MigrationItem("Docs/1", "1", item_type="record"),
        {"Title": "A", "MultiOwnerId": [_LOGIN, _MDOE]},
    )

    assert target_list.queued == [{"Title": "A", "MultiOwnerId": {"results": [7, 12]}, DEFAULT_LIST_IDENTITY_FIELD: "1"}]


def test_list_target_content_checksum_canonicalizes_multi_values():
    # Verification compares like for like: the target's multi-value ids are mapped
    # back to source ids / logins before the content hashes are compared.
    referenced = [
        _Item(1, {DEFAULT_LIST_IDENTITY_FIELD: "2"}),
        _Item(2, {DEFAULT_LIST_IDENTITY_FIELD: "3"}),
    ]
    fields = [
        _Field("MultiDept", "LookupMulti", _LOOKUP_SCHEMA_LIST_ID),
        _Field("MultiOwner", "UserMulti", _USERINFO_LIST_ID),
    ]
    row = _TargetRow(
        10,
        "1",
        properties={
            "Title": "Alpha",
            "MultiDeptId": {0: 1, 1: 2},
            "MultiOwnerId": {0: 7, 1: 12},
            "MultiOwnerStringId": "7;12",
        },
    )
    web = _Web({_LOOKUP_LIST_ID: referenced}, users={7: _LOGIN, 12: _MDOE})
    target_list = _TargetList(rows=[row], fields=fields, web=web)
    target = SharePointListTarget(cast("SPList", target_list))

    checksum = target.checksum(MigrationItem("Docs/1", "1", item_type="record"))

    assert checksum == _content_checksum({"Title": "Alpha", "MultiDeptId": [2, 3], "MultiOwnerId": [_LOGIN, _MDOE]})


class _RecordingUpsertTarget:
    """A minimal `UpsertTarget` that records what keyed_queue would send."""

    key_field = "Key"

    def __init__(self):
        self.created = []
        self.updated = []

    def ensure_key_field(self):
        pass

    def load_keys(self):
        return {}

    def create_records(self, records):
        self.created.extend(records)

    def update_record(self, item_id, record):
        self.updated.append((item_id, record))


def test_list_target_reshapes_multi_values_only_when_creating():
    # A create needs {"results": [...]} but a MERGE update rejects that shape and
    # wants the bare array, so the wrapper reshapes the create path alone.
    referenced = [
        _Item(1, {DEFAULT_LIST_IDENTITY_FIELD: "2"}),
        _Item(2, {DEFAULT_LIST_IDENTITY_FIELD: "3"}),
    ]
    fields = [_Field("MultiDept", "LookupMulti", _LOOKUP_SCHEMA_LIST_ID)]
    _, target = _lookup_target(referenced=referenced, fields=fields)

    inner = _RecordingUpsertTarget()
    wrapper = _MultiValueCreateTarget(inner, target._multi_value_create)
    record = {"Title": "A", "MultiDeptId": [2, 3]}

    wrapper.create_records([record])
    wrapper.update_record(7, record)

    assert inner.created == [{"Title": "A", "MultiDeptId": {"results": [2, 3]}}]
    assert inner.updated == [(7, {"Title": "A", "MultiDeptId": [2, 3]})]
    assert wrapper.key_field == "Key"


# ── Typed values: Managed Metadata (taxonomy) columns ────────────────────────

_TERM_A = "25983651-391e-4ac3-8e04-ae070b71cb65"
_TERM_B = "0e607563-5e38-4cfc-be32-445ad85c9aa2"
_TAX_ID = "11111111-1111-1111-1111-111111111111"
_TAX_NOTE_ID = "22222222-2222-2222-2222-222222222222"
_MULTI_ID = "33333333-3333-3333-3333-333333333333"
_MULTI_NOTE_ID = "44444444-4444-4444-4444-444444444444"


def _taxonomy_fields():
    return [
        _Field("Dept", "TaxonomyFieldType", field_id=_TAX_ID, text_field_id=_TAX_NOTE_ID),
        _Field("Dept_0", "Note", field_id=_TAX_NOTE_ID),
        _Field("Regions", "TaxonomyFieldTypeMulti", field_id=_MULTI_ID, text_field_id=_MULTI_NOTE_ID),
        _Field("Regions_0", "Note", field_id=_MULTI_NOTE_ID),
    ]


def test_list_source_projects_taxonomy_as_bare_term_guids():
    # A taxonomy read returns a label and a site-local WssId next to the term id;
    # only the term id is portable, so the projection keeps that alone and drops
    # the hidden note companion (the target recreates the column and re-serializes).
    items = [
        _Item(
            1,
            {
                "Id": 1,
                "Title": "A",
                "Dept": {"Label": "6", "TermGuid": _TERM_A, "WssId": 6},
                "Dept_0": f"-1;#|{_TERM_A}",
                "Regions": {
                    0: {"Label": "TermA", "TermGuid": _TERM_A, "WssId": 6},
                    1: {"Label": "TermB", "TermGuid": _TERM_B, "WssId": 7},
                },
                "Regions_0": f"-1;#|{_TERM_A};#-1;#|{_TERM_B}",
            },
        )
    ]
    source = SharePointListSource(cast("SPList", _SourceList(items, fields=_taxonomy_fields())))

    record = source.read(source.list_items()[0])

    assert record["Dept"] == [{"TermGuid": _TERM_A}]
    assert record["Regions"] == [{"TermGuid": _TERM_A}, {"TermGuid": _TERM_B}]
    assert "Dept_0" not in record
    assert "Regions_0" not in record


def test_list_source_drops_an_empty_taxonomy_column():
    items = [_Item(1, {"Id": 1, "Title": "A", "Dept": None, "Regions": {}})]
    source = SharePointListSource(cast("SPList", _SourceList(items, fields=_taxonomy_fields())))

    record = source.read(source.list_items()[0])

    assert "Dept" not in record
    assert "Regions" not in record


def test_list_target_remaps_taxonomy_to_typed_dict_and_note_text():
    # A single-value column takes a typed TaxonomyFieldValue dict (label blank —
    # the server resolves by term id); a multi-value one only accepts the hidden
    # note companion's ``-1;#Label|guid`` text form (a typed collection is rejected).
    target = SharePointListTarget(cast("SPList", _TargetList(fields=_taxonomy_fields())))
    record = {
        "Title": "A",
        "Dept": [{"TermGuid": _TERM_A}],
        "Regions": [{"TermGuid": _TERM_A}, {"TermGuid": _TERM_B}],
    }

    target._remap_taxonomies([record])

    assert record == {
        "Title": "A",
        "Dept": {
            "__metadata": {"type": "SP.Taxonomy.TaxonomyFieldValue"},
            "Label": "",
            "TermGuid": _TERM_A,
            "WssId": -1,
        },
        "Regions_0": f"-1;#|{_TERM_A};#-1;#|{_TERM_B}",
    }


def test_list_target_drops_taxonomy_column_absent_on_the_target():
    target = SharePointListTarget(cast("SPList", _TargetList(fields=[_Field("Other", "Text")])))
    record = {"Dept": [{"TermGuid": _TERM_A}]}

    target._remap_taxonomies([record])

    assert record == {}
    assert any("Dept" in warning for warning in target.warnings)


def test_list_checksums_ignore_taxonomy_label_and_wss_id():
    # Verification must treat the term id as the identity: the label and WssId are
    # cosmetic/site-local and differ between the source and its migrated copy.
    source = SharePointListSource(
        cast(
            "SPList",
            _SourceList(
                [
                    _Item(
                        1,
                        {
                            "Id": 1,
                            "Title": "A",
                            "Dept": {"Label": "6", "TermGuid": _TERM_A, "WssId": 6},
                            "Regions": {
                                0: {"Label": "TermA", "TermGuid": _TERM_A, "WssId": 6},
                                1: {"Label": "TermB", "TermGuid": _TERM_B, "WssId": 7},
                            },
                        },
                    )
                ],
                fields=_taxonomy_fields(),
            ),
        )
    )
    source_item = source.list_items()[0]
    source.read(source_item)

    row = _TargetRow(
        10,
        "1",
        properties={
            "Title": "A",
            "Dept": {"Label": "1", "TermGuid": _TERM_A, "WssId": 1},
            "Regions": {
                0: {"Label": "TermA", "TermGuid": _TERM_B, "WssId": 2},
                1: {"Label": "TermB", "TermGuid": _TERM_A, "WssId": 1},
            },
            "Regions_0": f"-1;#|{_TERM_B};#-1;#|{_TERM_A}",
        },
    )
    target = SharePointListTarget(cast("SPList", _TargetList(rows=[row], fields=_taxonomy_fields())))

    checksum = target.checksum(source_item)

    assert checksum == source.checksum(source_item)


def test_list_target_replays_a_captured_structure_once(monkeypatch):
    # A bundle's records are payload; the columns they name travel in the sidecar, so
    # the structure has to land on the target before the first record is written.
    calls: list = []

    def fake_provision(sp_list, structure, **kwargs):
        calls.append((sp_list, structure, kwargs))
        return ["column 'ProjCode' was created with a different type"]

    monkeypatch.setattr(adapters, "provision_list_structure", fake_provision)
    target_list = _TargetList()
    structure = ListStructure(title="Tasks", base_template=100, base_type=0)
    target = SharePointListTarget(cast("SPList", target_list), structure=structure)

    target.configure(MigrationOptions())
    target.apply_structure()

    assert [call[0] for call in calls] == [target_list]
    assert calls[0][1] is structure
    assert target.warnings == ["column 'ProjCode' was created with a different type"]
