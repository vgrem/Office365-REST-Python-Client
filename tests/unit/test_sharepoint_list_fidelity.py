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
    """A list item whose *plain* read does not return ``HasUniqueRoleAssignments``.

    That mirrors SharePoint: the flag is absent from a default entity payload, so a
    value cached before an ACL write stays in ``properties`` until a projection asks
    for it — which is what ``server_unique`` models.
    """

    def __init__(
        self,
        target_id,
        identity=None,
        *,
        author_id=None,
        editor_id=None,
        unique=None,
        assignments=(),
        server_unique=None,
    ):
        self.id = target_id
        self._server_unique = server_unique
        self._select: list | None = None
        self.query_options = SimpleNamespace(select=[])
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

    def select(self, columns):
        self._select = list(columns)
        self.query_options.select = list(columns)
        return self

    def get(self):
        self.get_calls += 1
        if self._select == ["HasUniqueRoleAssignments"] and self._server_unique is not None:
            self.properties["HasUniqueRoleAssignments"] = self._server_unique
        self._select = None
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


# ── Durability ───────────────────────────────────────────────────────────────


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


# ── Timestamps ───────────────────────────────────────────────────────────────


def test_timestamps_fold_in_pending_authorship_for_one_final_write():
    # The timestamp write runs last; the pending Author/Editor values ride along
    # so both land atomically (and neither is lost to a later write).
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
    assert len(row.updates) == 1  # authorship did not pay a write of its own


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

    # Resolved and cached, not written: the fidelity write is the last one.
    assert row.updates == []

    target.finalize_fidelity(item)

    assert web.ensure_calls == ["vgrem@mediadev8.onmicrosoft.com"]  # the claims prefix is stripped
    form_values, _, _ = row.updates[0]
    assert form_values["Author"].LookupId == 9  # noqa: PLR2004
    assert form_values["Editor"].LookupId == 9  # noqa: PLR2004
    assert form_values["Author"].LookupValue == login
    assert row.updates[0][2] is True  # a system update (no new version)
    assert len(row.updates) == 1  # one write for the whole item


# ── Approval state ───────────────────────────────────────────────────────────


# ── Permissions ──────────────────────────────────────────────────────────────


def test_read_permissions_sees_an_acl_applied_after_the_item_was_loaded():
    # The target item was loaded before its ACL was applied, so its cached flag says
    # "inherits"; only a projected read reveals the assignments that did land.
    row = _TargetListItem(
        10,
        "1",
        unique=False,
        server_unique=True,
        assignments=[_Assignment(_Member("i:0#.f|membership|anna@contoso.com"), ["Read"])],
    )
    target = SharePointListTarget(cast("SPList", _TargetList([row], web=_Web())))

    entries = target.read_permissions(MigrationItem("Docs/1", "1", item_type="record"))

    assert len(entries) == 1
    assert row.get_calls > 1  # the full read, then the explicit flag re-read


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
