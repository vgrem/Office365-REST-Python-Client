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
    _MultiValueCreateTarget,
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


def test_list_target_content_checksum_compares_multi_choice_values():
    # The source records a bare list while the target reads a positional mapping;
    # both must project to the same content or every run reports a false mismatch.
    row = _TargetRow(10, "1", properties={"Title": "Alpha", "Tags": {0: "red", 1: "green"}})
    fields = [_Field("Tags", "MultiChoice", allow_multiple_values=True)]
    target = SharePointListTarget(cast("SPList", _TargetList(rows=[row], fields=fields)))

    checksum = target.checksum(MigrationItem("Docs/1", "1", item_type="record"))

    assert checksum == _content_checksum({"Title": "Alpha", "Tags": ["red", "green"]})


def test_list_target_content_checksum_compares_hyperlink_values():
    # The source records the value object it read; the target reads the same shape
    # back, so both must hash identically.
    value = {"Description": "one", "Url": "https://example.com/1"}
    row = _TargetRow(10, "1", properties={"Title": "Alpha", "Link": value})
    target = SharePointListTarget(cast("SPList", _TargetList(rows=[row])))

    checksum = target.checksum(MigrationItem("Docs/1", "1", item_type="record"))

    assert checksum == _content_checksum({"Title": "Alpha", "Link": value})


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
