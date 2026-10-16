"""Offline tests for record-list fidelity: durability, timestamps, authorship, ACLs.

The client-side list adapters used to expose no metadata/permission hooks, so the
fidelity flags failed fast for record lists. They now support:

* **durability** — ``SharePointListTarget`` declares ``deferred_writes`` so the
  runner flushes (and checkpoints) every chunk even at ``concurrency == 1``;
* **timestamps** — ``apply_timestamps``/``read_metadata`` via
  ``ValidateUpdateListItem``;
* **authorship** — ``apply_authorship``/``read_authorship`` via ``EnsureUser``;
* **permissions** — ``read_permissions``/``apply_permissions``, guarded on
  ``HasUniqueRoleAssignments`` (REST otherwise reports inherited ACLs).
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from office365.sharepoint.lists.list import List as SPList

from office365.migration.base import ItemStatus, MigrationItem, MigrationOptions
from office365.migration.checkpoint import Checkpoint
from office365.migration.runner import MigrationRunner
from office365.migration.sharepoint.adapters import (
    DEFAULT_LIST_IDENTITY_FIELD,
    SharePointListTarget,
    _has_unique_role_assignments,
)
from office365.migration.validators import _verify_authorship
from office365.sharepoint.principal.type import PrincipalType

# ── Fakes ────────────────────────────────────────────────────────────────────


class _Executable:
    def execute_query(self):
        return self


class _Get:
    def __init__(self, value):
        self._value = value

    def get(self):
        return self

    def execute_query(self):
        return self._value


class _NameId:
    def __init__(self, name_id):
        self.NameId = name_id


class _SiteUser:
    def __init__(self, user_id, login, name_id="1003200065102863", title=None, email=None):
        self.id = user_id
        self.login_name = login
        self.title = title
        self.properties = {"UserId": _NameId(name_id), "Email": email}


class _SiteUsers:
    def __init__(self, users):
        self._by_id = {u.id: u for u in users}

    def get_by_id(self, key):
        return _Get(self._by_id.get(int(key)))


class _Group:
    def __init__(self, name):
        self.name = name
        self.login_name = name
        self.principal_type = PrincipalType.SecurityGroup

    def get(self):
        return _Get(self)


class _RoleDefinition:
    def __init__(self, name):
        self.name = name


class _SiteGroups:
    def __init__(self, groups):
        self._by_name = {g.name: g for g in groups}

    def get_by_name(self, name):
        return _Get(self._by_name.get(name))


class _RoleDefinitions:
    def __init__(self, roles):
        self._roles = list(roles)

    def get(self):
        return _Get(self._roles)


class _Web:
    def __init__(self, users=(), groups=(), roles=(), associated_groups=None):
        self.site_users = _SiteUsers(list(users))
        self.site_groups = _SiteGroups(list(groups))
        self.role_definitions = _RoleDefinitions(roles)
        associated_groups = associated_groups or {}
        self.associated_owner_group = associated_groups.get("Owners")
        self.associated_member_group = associated_groups.get("Members")
        self.associated_visitor_group = associated_groups.get("Visitors")
        self._by_login = {}
        for user in users:
            self._by_login[user.login_name] = user
            self._by_login[user.login_name.rsplit("|", 1)[-1]] = user
        self.ensure_calls: list[str] = []

    def ensure_user(self, login):
        self.ensure_calls.append(login)
        return _Get(self._by_login.get(login))


class _Context:
    def __init__(self, web):
        self.web = web
        self.has_pending_request = False
        self.batches = 0

    def execute_batch(self, items_per_batch=100, concurrency=1):
        self.batches += 1
        self.has_pending_request = False

    def execute_query(self):
        pass


class _BasePermissions:
    def __init__(self):
        self.High = 176
        self.Low = 138612833


class _AssignmentRole:
    def __init__(self, name):
        self.name = name
        self.base_permissions = _BasePermissions()


class _Member:
    def __init__(self, login, principal_type=PrincipalType.User):
        self.id = 10
        self.login_name = login
        self.user_principal_name = login
        self.principal_type = principal_type


class _Assignment:
    def __init__(self, member, roles):
        self.member = member
        self.role_definition_bindings = [r if isinstance(r, _AssignmentRole) else _AssignmentRole(r) for r in roles]


class _RoleAssignments:
    def __init__(self, assignments):
        self._items = list(assignments)

    def expand(self, _props):
        return self

    def get(self):
        return self

    def execute_query(self):
        return self._items


class _TargetListItem:
    def __init__(self, target_id, identity=None, *, author_id=None, editor_id=None, unique=None, assignments=()):
        self.id = target_id
        self.properties: dict[str, object] = {"Id": target_id}
        if identity is not None:
            self.properties[DEFAULT_LIST_IDENTITY_FIELD] = identity
        if author_id is not None:
            self.properties["AuthorId"] = author_id
        if editor_id is not None:
            self.properties["EditorId"] = editor_id
        if unique is not None:
            self.properties["HasUniqueRoleAssignments"] = unique
        self.role_assignments = _RoleAssignments(assignments)
        self.updates: list = []
        self.broke_inheritance = None
        self.assignments_added: list = []
        self.get_calls = 0
        self.ensured_property = None

    @property
    def has_unique_role_assignments(self):
        return self.properties.get("HasUniqueRoleAssignments", None)

    def get(self):
        self.get_calls += 1
        return self

    def execute_query(self):
        return self

    def ensure_property(self, name):
        self.ensured_property = name
        return _Executable()

    def validate_update_list_item(self, form_values, new_document_update=False, checkin_comment=None, dates_in_utc=None):
        self.updates.append((dict(form_values), dates_in_utc, new_document_update))
        return _Executable()

    def break_role_inheritance(self, copy_role_assignments=True, clear_sub_scopes=True):
        self.broke_inheritance = (copy_role_assignments, clear_sub_scopes)
        self.properties["HasUniqueRoleAssignments"] = True
        return _Executable()

    def add_role_assignment(self, principal, role):
        self.assignments_added.append((principal, role))
        return _Executable()


class _TargetItems:
    def __init__(self, owner):
        self._owner = owner
        self._select = None
        self._filter = None

    def select(self, columns):
        self._select = list(columns)
        return self

    def filter(self, expr):
        self._filter = expr
        self._owner.filters.append(expr)
        return self

    def get_all(self):
        return self

    def execute_query(self):
        rows = self._owner.rows
        if self._filter and self._filter.startswith("Id gt "):
            threshold = int(self._filter.split()[-1])
            rows = [r for r in rows if r.id > threshold]
        self._filter = None
        return rows

    def queue_records(self, records, progress=None):
        self._owner.queued.extend(records)
        self._owner.context.has_pending_request = True

    def clear(self):
        self._owner.queued.clear()


class _TargetList:
    def __init__(self, rows=None, web=None):
        self.title = "TargetList"
        self.rows = rows or []
        self.queued = []
        self.filters = []
        self.identity_fields = []
        self.context = _Context(web or _Web())
        self.items = _TargetItems(self)
        self.fields = self

    def ensure(self, parameters):
        self.identity_fields.append(parameters)
        return _Executable()

    def execute_query(self):
        return self


class _SourceItems:
    def __init__(self, items):
        self._items = items
        self._select = None

    def select(self, columns):
        self._select = list(columns)
        return self

    def expand(self, _e):
        return self

    def get_all(self):
        return self

    def execute_query(self):
        return list(self._items)


class _SourceList:
    def __init__(self, items, web=None):
        self.title = "SourceList"
        self.context = _Context(web or _Web())
        self.items = _SourceItems(items)


# ── Durability ───────────────────────────────────────────────────────────────


def test_deferred_write_capability_is_declared():
    assert SharePointListTarget.deferred_writes is True


def test_runner_uses_chunked_writes_for_a_deferred_target_at_concurrency_one():
    class _DeferredTarget:
        deferred_writes = True

        def __init__(self):
            self.chunk_calls = 0
            self.written = []

        def exists(self, item):
            return False

        def write(self, item, payload):  # pragma: no cover — must not be used
            raise AssertionError("deferred target must be written in chunks")

        def write_many(self, items, payloads, concurrency=1):
            self.chunk_calls += 1
            self.written.extend(item.dest_path for item in items)
            return []

        def list_paths(self):
            return list(self.written)

        def checksum(self, item):
            return ""

        def commit(self, options=None):
            pass

        def close(self):
            pass

    class _Source:
        def read(self, item):
            return {"v": item.dest_path}

        def close(self):
            pass

    items = [MigrationItem(source_path=f"/s{i}", dest_path=f"r{i}") for i in range(5)]
    target = _DeferredTarget()
    checkpoint = Checkpoint.create()

    stats = MigrationRunner().run(
        _Source(),  # type: ignore[arg-type]
        target,  # type: ignore[arg-type]
        items,
        MigrationOptions(concurrency=1, batch_size=2),
        checkpoint,
    )

    assert stats.success == 5  # noqa: PLR2004
    assert target.chunk_calls == 3  # noqa: PLR2004 — 2 + 2 + 1
    assert all(checkpoint.status_of(item) is ItemStatus.DONE for item in items)


def test_identity_index_refreshes_incrementally_after_a_flush():
    rows = [_TargetListItem(10, "1"), _TargetListItem(11, "2")]
    target_list = _TargetList(rows)
    target = SharePointListTarget(cast("SPList", target_list))

    assert target.exists(MigrationItem("Docs/1", "1", item_type="record")) is True
    assert target_list.filters == []  # first load is a full scan

    target.write_many([MigrationItem("Docs/3", "3", item_type="record")], [{"Title": "C"}])
    rows.append(_TargetListItem(12, "3"))  # the server assigned the new item id

    assert target.exists(MigrationItem("Docs/3", "3", item_type="record")) is True
    assert target_list.filters == ["Id gt 11"]  # only what was created since the last load


# ── Timestamps ───────────────────────────────────────────────────────────────


def test_apply_timestamps_uses_validated_update_with_utc_dates():
    row = _TargetListItem(10, "1")
    target = SharePointListTarget(cast("SPList", _TargetList([row])))
    item = MigrationItem(
        "Docs/1",
        "1",
        item_type="record",
        created="2019-03-04T05:06:07+00:00",
        modified="2020-04-05T06:07:08+00:00",
    )

    target.apply_timestamps(item)

    form_values, dates_in_utc, new_document_update = row.updates[0]
    assert form_values == {"Created": "2019-03-04T05:06:07Z", "Modified": "2020-04-05T06:07:08Z"}
    assert dates_in_utc is True
    assert new_document_update is False


def test_read_metadata_refreshes_the_item_before_diffing():
    row = _TargetListItem(10, "1")
    row.properties["Created"] = "2019-03-04T05:06:07Z"
    target = SharePointListTarget(cast("SPList", _TargetList([row])))

    metadata = target.read_metadata(MigrationItem("Docs/1", "1", item_type="record"))

    assert metadata == {"created": "2019-03-04T05:06:07Z", "modified": None}
    assert row.get_calls == 1  # apply_timestamps wrote after the index was built


def test_timestamps_fold_in_pending_authorship_so_editor_is_not_reset():
    # The timestamp write runs last; REST would otherwise bump ``Editor`` to the
    # caller, so the pending Author/Editor values must ride along in that write.
    login = "vgrem@mediadev8.onmicrosoft.com"
    row = _TargetListItem(10, "1")
    web = _Web(users=[_SiteUser(9, login, title="Vadim")])
    target = SharePointListTarget(cast("SPList", _TargetList([row], web=web)))

    from office365.migration.base import Principal

    item = MigrationItem(
        "Docs/1",
        "1",
        item_type="record",
        created="2019-03-04T05:06:07+00:00",
        modified="2020-04-05T06:07:08+00:00",
    )
    item.author = Principal(login, "1003200065102863", "Vadim")
    item.editor = Principal(login, "1003200065102863", "Vadim")

    target.apply_authorship(item)
    target.apply_timestamps(item)

    final, dates_in_utc, _ = row.updates[-1]
    assert final["Created"] == "2019-03-04T05:06:07Z"
    assert final["Modified"] == "2020-04-05T06:07:08Z"
    assert final["Author"].LookupId == 9  # noqa: PLR2004
    assert final["Editor"].LookupId == 9  # noqa: PLR2004
    assert dates_in_utc is True


# ── Authorship ───────────────────────────────────────────────────────────────


def test_apply_authorship_resolves_users_and_sets_person_fields():
    login = "i:0#.f|membership|vgrem@mediadev8.onmicrosoft.com"
    row = _TargetListItem(10, "1")
    web = _Web(users=[_SiteUser(9, login, title="Vadim")])
    target = SharePointListTarget(cast("SPList", _TargetList([row], web=web)))

    from office365.migration.base import Principal

    item = MigrationItem("Docs/1", "1", item_type="record")
    item.author = Principal(login, "1003200065102863", "Vadim")
    item.editor = Principal(login, "1003200065102863", "Vadim")

    target.apply_authorship(item)

    assert web.ensure_calls == ["vgrem@mediadev8.onmicrosoft.com"]  # the claims prefix is stripped
    form_values, _, _ = row.updates[0]
    assert form_values["Author"].LookupId == 9  # noqa: PLR2004
    assert form_values["Editor"].LookupId == 9  # noqa: PLR2004
    assert form_values["Author"].LookupValue == login


def test_apply_authorship_skips_unresolved_principals():
    row = _TargetListItem(10, "1")
    web = _Web(users=[])  # EnsureUser cannot resolve anyone
    target = SharePointListTarget(cast("SPList", _TargetList([row], web=web)))

    from office365.migration.base import Principal

    item = MigrationItem("Docs/1", "1", item_type="record")
    item.author = Principal("i:0#.f|membership|ghost@mediadev8.onmicrosoft.com", "1", "Ghost")

    target.apply_authorship(item)

    assert row.updates == []  # nothing to write
    assert target.warnings == []  # EnsureUser returned nothing, not an error


def test_read_authorship_resolves_author_and_editor_logins():
    login = "i:0#.f|membership|vgrem@mediadev8.onmicrosoft.com"
    row = _TargetListItem(10, "1", author_id=9, editor_id=9)
    web = _Web(users=[_SiteUser(9, login)])
    target = SharePointListTarget(cast("SPList", _TargetList([row], web=web)))

    assert target.read_authorship(MigrationItem("Docs/1", "1", item_type="record")) == (login, login)


# ── Permissions ──────────────────────────────────────────────────────────────


def test_has_unique_role_assignments_reads_and_defaults_to_not_unique():
    assert _has_unique_role_assignments(SimpleNamespace(has_unique_role_assignments=True)) is True
    assert _has_unique_role_assignments(SimpleNamespace(has_unique_role_assignments=False)) is False

    class _Broken:
        has_unique_role_assignments = None

        def ensure_property(self, name):
            raise RuntimeError("no access")

    assert _has_unique_role_assignments(_Broken()) is False


def test_read_permissions_returns_empty_for_inherited_assignments():
    inherited = _RoleAssignments([_Assignment(_Member("Project Members"), ["Edit"])])
    row = _TargetListItem(10, "1", unique=False)
    row.role_assignments = inherited
    target = SharePointListTarget(cast("SPList", _TargetList([row])))

    assert target.read_permissions(MigrationItem("Docs/1", "1", item_type="record")) == []


def test_read_permissions_returns_entries_for_unique_assignments():
    row = _TargetListItem(10, "1", unique=True, assignments=[_Assignment(_Member("Project Members"), ["Edit"])])
    target = SharePointListTarget(cast("SPList", _TargetList([row])))

    entries = target.read_permissions(MigrationItem("Docs/1", "1", item_type="record"))

    assert [e.principal_name for e in entries] == ["Project Members"]
    assert entries[0].roles == ["Edit"]


def test_apply_permissions_breaks_inheritance_and_resolves_principals():
    admin = _SiteUser(6, "i:0#.f|membership|admin@mediadev8.onmicrosoft.com")
    group = _Group("Project Members")
    read = _RoleDefinition("Read")
    web = _Web(users=[admin], groups=[group], roles=[read])
    row = _TargetListItem(10, "1")
    target = SharePointListTarget(cast("SPList", _TargetList([row], web=web)))

    from office365.migration.base import PermissionEntry

    permissions = [
        PermissionEntry(principal_name=group.name, roles=["Read"]),
        PermissionEntry(principal_name=admin.login_name, roles=["Read"]),
    ]
    target.apply_permissions(MigrationItem("Docs/1", "1", item_type="record"), permissions)

    assert row.broke_inheritance == (False, False)
    principals = [p for p, _ in row.assignments_added]
    assert principals[0] is group
    assert principals[1].login_name == admin.login_name
    assert [r for _, r in row.assignments_added] == [read, read]


def test_apply_permissions_maps_a_default_group_by_role_kind():
    # Default groups are titled after the site, so the source name rarely matches
    # the target's; the trailing Owners/Members/Visitors kind maps to the target's
    # associated group instead (team Members -> team_out Members).
    target_group = _Group("team_out Members")
    read = _RoleDefinition("Read")
    web = _Web(roles=[read], associated_groups={"Members": target_group})
    row = _TargetListItem(10, "1")
    target = SharePointListTarget(cast("SPList", _TargetList([row], web=web)))

    from office365.migration.base import PermissionEntry

    target.apply_permissions(
        MigrationItem("Docs/1", "1", item_type="record"),
        [PermissionEntry(principal_name="team Members", roles=["Read"])],
    )

    assert [p for p, _ in row.assignments_added] == [target_group]
    assert target.warnings == []


def test_default_group_names_normalize_and_resolve_from_the_token():
    # Both sides canonicalize a default group's title to ``default:<Kind>`` so a
    # renamed site (team Visitors -> team_out Visitors) still verifies as preserved;
    # the token is also resolvable back onto the target's associated group.
    from office365.migration.sharepoint.adapters import _DefaultGroups, _TargetPrincipals

    visitors = _Group("team_out Visitors")
    web = _Web(associated_groups={"Visitors": visitors})

    defaults = _DefaultGroups(web)
    assert defaults.normalize("team_out Visitors") == "default:Visitors"
    assert defaults.normalize("Custom Team") == "Custom Team"

    principals = _TargetPrincipals(web, [])
    assert principals.normalize("team_out Visitors") == "default:Visitors"
    assert principals.principal("default:Visitors") is visitors


# ── Verification (authorship diff) ───────────────────────────────────────────


def test_verify_authorship_reports_a_mismatch():
    login = "i:0#.f|membership|vgrem@mediadev8.onmicrosoft.com"

    class _Source:
        def read_authorship(self, item):
            return (login, login)

    class _Target:
        def read_authorship(self, item):
            return (None, None)

    report = SimpleNamespace(unverifiable=[], mismatches=[])
    from office365.migration.base import Principal

    item = MigrationItem("Docs/1", "1", item_type="record")
    item.author = Principal(login, "1", "V")

    _verify_authorship(_Source(), _Target(), [item], report)

    assert report.unverifiable == []
    assert report.mismatches == ["authorship mismatch: 1"]


def test_verify_authorship_is_unverifiable_without_the_hooks():
    report = SimpleNamespace(unverifiable=[], mismatches=[])
    _verify_authorship(object(), object(), [MigrationItem("Docs/1", "1")], report)

    assert report.mismatches == []
    assert report.unverifiable == ["authorship: adapters do not implement read_authorship(item)"]
