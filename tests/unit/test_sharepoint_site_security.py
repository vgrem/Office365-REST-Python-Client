"""Offline tests for best-effort web- and list-level security replication.

The item adapters restore each item's *unique* ACL; ``security.py`` covers the two
container scopes. These tests drive it with fakes — no network — and assert that
custom groups are created (default groups are mapped onto the target's associated
groups), membership and web role assignments are reapplied, a *list's* own ACLs are
broken and replayed on the target (a restricted library must not arrive readable),
and unresolvable principals are warned about rather than dropped silently.
"""

from __future__ import annotations

from office365.migration.sharepoint.security import (
    apply_site_list_security,
    apply_site_security,
    verify_list_security,
    verify_site_security,
)
from office365.sharepoint.permissions.base_permissions import BasePermissions
from office365.sharepoint.principal.type import PrincipalType


class _User:
    def __init__(self, login: str, user_id: int = 100) -> None:
        self.login_name = login
        self.user_principal_name = login
        self.title = login
        self.id = user_id
        self.principal_type = PrincipalType.User

    def get(self):
        return self

    def execute_query(self):
        return self


class _Users:
    def __init__(self, members=()) -> None:
        self._items = [_User(m) if isinstance(m, str) else m for m in members]

    def get(self):
        return self

    def execute_query(self):
        return list(self._items)

    def add_user(self, user) -> None:
        self._items.append(user)


class _Group:
    def __init__(self, title: str, group_id: int, description=None, flags=None, members=(), web=None) -> None:
        self.title = title
        self.id = group_id
        self.description = description
        self.properties: dict[str, object] = {"Id": group_id, "Title": title}
        if description is not None:
            self.properties["Description"] = description
        self.properties.update(flags or {})
        self.users = _Users(members)
        self._web = web
        self.updates: list[dict] = []

    def get(self):
        return self

    def execute_query(self):
        return self

    def update_properties(self, **properties):
        self.updates.append(properties)
        self.properties.update(properties)
        return self


class _Role:
    def __init__(self, name: str, role_id: int, mask: int = 0, kind=None, description=None, hidden=False) -> None:
        self.name = name
        self.id = role_id
        self.role_type_kind = kind
        self.description = description
        self.hidden = hidden
        self.order = 1
        self.base_permissions = BasePermissions(High=mask >> 32, Low=mask & 0xFFFFFFFF)


class _RoleDefinitions:
    def __init__(self, roles) -> None:
        self._roles = list(roles)
        self.added: list[tuple] = []

    def get(self):
        return self

    def execute_query(self):
        return list(self._roles)

    def add(self, base_permissions, name, description=None, order=None):
        self.added.append((base_permissions, name, description, order))
        self._roles.append(
            _Role(
                name,
                600,
                (int(base_permissions.High) << 32) | int(base_permissions.Low),
                description=description,
            )
        )
        return self._roles[-1]


class _Assignment:
    def __init__(self, member, roles) -> None:
        self.member = member
        self.role_definition_bindings = [r if isinstance(r, _Role) else _Role(r, 0) for r in roles]


class _RoleAssignments:
    def __init__(self, assignments=()) -> None:
        self._items = list(assignments)

    def expand(self, _props):
        return self

    def get(self):
        return self

    def execute_query(self):
        return list(self._items)


class _GetOne:
    def __init__(self, value) -> None:
        self._value = value

    def get(self):
        return self

    def execute_query(self):
        return self._value


class _SiteGroups:
    def __init__(self, groups, web) -> None:
        self._groups = list(groups)
        self._web = web

    def get(self):
        return self

    def execute_query(self):
        return list(self._groups)

    def get_by_name(self, name):
        return _GetOne(next((g for g in self._groups if g.title == name), None))

    def add(self, title, description=None):
        group = _Group(title, self._web._next_id(), description, web=self._web)
        self._groups.append(group)
        self._web.created_groups.append(group)
        return group


class _Web:
    def __init__(self, groups, associated, assignments=(), roles=()) -> None:
        self._ids = iter(range(50, 100))
        self._groups = list(groups)
        self.associated_owner_group = associated.get("Owners")
        self.associated_member_group = associated.get("Members")
        self.associated_visitor_group = associated.get("Visitors")
        self.site_groups = _SiteGroups(self._groups, self)
        self.role_definitions = _RoleDefinitions(roles)
        self.role_assignments = _RoleAssignments(assignments)
        self.ensure_users: dict[str, _User] = {}
        self.ensure_calls: list[str] = []
        self.assignments_added: list = []
        self.created_groups: list[_Group] = []
        self.executed = 0
        self.unresolvable: set[str] = set()
        self.context = self

    def _next_id(self) -> int:
        return next(self._ids)

    def ensure_user(self, login):
        self.ensure_calls.append(login)
        if login in self.unresolvable:
            raise RuntimeError(f"user {login} not found")
        return self.ensure_users.setdefault(login, _User(login, next(self._ids)))

    def add_role_assignment(self, principal, role) -> None:
        self.assignments_added.append((principal, role))

    def execute_query(self) -> None:
        self.executed += 1


def _source_web():
    owners = _Group("S Owners", 3)
    members = _Group("S Members", 4)
    visitors = _Group("S Visitors", 5)
    auditors = _Group("Auditors", 6, members=["mary@contoso.com"])
    groups = [owners, members, visitors, auditors]
    assignments = [
        _Assignment(_Member("S Owners"), ["Full Control"]),
        _Assignment(_Member("S Members"), ["Edit"]),
        _Assignment(_Member("S Visitors"), ["Read"]),
        _Assignment(_Member("Auditors"), ["Read"]),
    ]
    return _Web(groups, {"Owners": owners, "Members": members, "Visitors": visitors}, assignments)


class _Member:
    def __init__(self, login: str) -> None:
        self.login_name = login
        self.user_principal_name = login
        self.id = 1


def _target_web(*, with_auditors: bool = False, extra_assignment: bool = True):
    owners = _Group("T Owners", 13)
    members = _Group("T Members", 14)
    visitors = _Group("T Visitors", 15)
    groups = [owners, members, visitors]
    assignments = [
        _Assignment(_Member("T Owners"), ["Full Control"]),
        _Assignment(_Member("T Members"), ["Edit"]),
        _Assignment(_Member("T Visitors"), ["Read"]),
    ]
    if with_auditors:
        auditors = _Group("Auditors", 16, members=["mary@contoso.com"])
        groups.append(auditors)
        if extra_assignment:
            assignments.append(_Assignment(_Member("Auditors"), ["Read"]))
    roles = [_Role("Full Control", 1073741829), _Role("Edit", 1073741830), _Role("Read", 1073741826)]
    return _Web(groups, {"Owners": owners, "Members": members, "Visitors": visitors}, assignments, roles)


def test_apply_creates_custom_group_restores_membership_and_role_assignment():
    source, target = _source_web(), _target_web()

    warnings: list[str] = []
    apply_site_security(source, target, warnings)

    assert warnings == []
    created = [g for g in target.site_groups.execute_query() if g.title == "Auditors"]
    assert len(created) == 1
    assert target.ensure_calls == ["mary@contoso.com"]
    # existing default assignments are not duplicated; only the custom one is added
    assert [(p.title, r.name) for p, r in target.assignments_added] == [("Auditors", "Read")]
    assert target.executed == 1


def test_apply_does_not_duplicate_an_existing_custom_group_or_assignment():
    source, target = _source_web(), _target_web(with_auditors=True)

    apply_site_security(source, target, [])

    assert target.created_groups == []
    assert target.assignments_added == []
    assert target.executed == 0


def test_apply_warns_on_an_unresolvable_member_without_aborting():
    source = _source_web()
    source._groups[-1].users = _Users(["nobody"])  # replaces the _Users collection
    target = _target_web()

    warnings: list[str] = []
    target.ensure_users["nobody"] = None  # type: ignore[assignment]
    apply_site_security(source, target, warnings)

    # a falsy ensured user is resolved to ``None`` by _TargetPrincipals
    assert any("nobody" in w for w in warnings)


def test_verify_reports_a_missing_custom_group():
    source, target = _source_web(), _target_web()

    issues = verify_site_security(source, target)

    assert any("Auditors" in issue and "not created" in issue for issue in issues)
    assert any("Auditors -> Read" in issue for issue in issues)


def test_verify_is_clean_for_a_replicated_scope():
    source, target = _source_web(), _target_web(with_auditors=True)

    assert verify_site_security(source, target) == []


class _Ctx:
    """A client context stand-in: a web plus the queue's ``execute_query``."""

    def __init__(self, web) -> None:
        self.web = web

    def execute_query(self):
        self.web.execute_query()
        return self


class _SPList:
    """A list stand-in: its own ACLs (or none, when it inherits the web's)."""

    def __init__(self, title: str, assignments=None, web=None) -> None:
        self.title = title
        self.context = web
        self._inherits = assignments is None
        self.role_assignments = _RoleAssignments(list(assignments or []))
        self.properties: dict[str, object] = {"Title": title, "HasUniqueRoleAssignments": not self._inherits}
        self.break_calls = 0
        self.added: list[tuple] = []

    def ensure_properties(self, _names):
        return self

    def get(self):
        return self

    def execute_query(self):
        return self

    def break_role_inheritance(self, copy_role_assignments=True, clear_sub_scopes=True):
        self.break_calls += 1
        self._inherits = False
        self.properties["HasUniqueRoleAssignments"] = True
        self.role_assignments = _RoleAssignments([])
        return self

    def add_role_assignment(self, principal, role):
        self.added.append((principal, role))
        self.role_assignments._items.append(_Assignment(principal, [role]))
        return self


class _Lists:
    def __init__(self, lists) -> None:
        self._lists = list(lists)

    def get(self):
        return self

    def execute_query(self):
        return list(self._lists)


def _list_web(*lists, roles=(), groups=None):
    web = _Web(list(groups or []), {}, roles=roles or [_Role("Read", 1), _Role("Edit", 2)])
    web.lists = _Lists(lists)
    for sp_list in lists:
        sp_list.context = _Ctx(web)
    return web


def _restricted_list(title="Library", principals=("Auditors",), role="Read", web=None):
    return _SPList(title, [_Assignment(_Member(p), [role]) for p in principals], web=web)


def test_a_restricted_list_is_broken_and_replayed_on_the_target():
    source_web = _list_web(_restricted_list())
    target = _SPList("Library")
    target_web = _list_web(target, groups=[_Group("Auditors", 60)])
    warnings: list[str] = []

    report = apply_site_list_security(source_web, target_web, warnings=warnings)

    assert report.restricted == ["Library"]
    assert report.applied == ["Library"]
    assert target.break_calls == 1
    assert [principal.title for principal, _role in target.added] == ["Auditors"]
    assert warnings == []


def test_a_list_that_inherits_on_the_source_is_never_touched():
    target = _SPList("Documents")
    source_web = _list_web(_SPList("Documents"))
    target_web = _list_web(target)

    report = apply_site_list_security(source_web, target_web)

    assert report.restricted == []
    assert report.summary() == "no list carries unique permissions"
    assert target.break_calls == 0
    assert target.added == []


def test_only_the_named_lists_are_visited():
    source_web = _list_web(_restricted_list("A"), _restricted_list("B"))
    target_web = _list_web(_SPList("A"), _SPList("B"))

    report = apply_site_list_security(source_web, target_web, lists=["b"])

    assert report.restricted == ["B"]


def test_verify_names_a_list_the_target_leaves_readable():
    source_web = _list_web(_restricted_list())
    target_web = _list_web(_SPList("Library"))

    issues = verify_list_security(source_web, target_web)

    assert len(issues) == 1
    assert issues[0].startswith("list 'Library' inherits the web's permissions on the target")
    assert "1 assignment(s)" in issues[0]


def test_verify_names_an_assignment_the_target_missed():
    source_web = _list_web(_restricted_list(principals=("Auditors", "S Members")))
    target_web = _list_web(_restricted_list(principals=("Auditors",)))

    issues = verify_list_security(source_web, target_web)

    assert len(issues) == 1
    assert "not restored" in issues[0]
    assert "S Members -> Read" in issues[0]


def _levels_web(roles, *, assignments=(), groups=None):
    web = _Web(list(groups or []), {}, assignments, roles=roles)
    return web


def test_a_custom_level_the_target_lacks_is_created_with_its_mask():
    source = _levels_web([_Role("Read", 1, 8, kind=2), _Role("Custom Reader", 2, 5, kind=0, description="ours")])
    target = _levels_web([_Role("Read", 1, 8, kind=2)])
    warnings: list[str] = []

    apply_site_security(source, target, warnings)

    ((base_permissions, name, description, _order),) = target.role_definitions.added
    assert name == "Custom Reader"
    assert description == "ours"
    assert (base_permissions.High, base_permissions.Low) == (0, 5)
    assert warnings == []


def test_verify_names_a_missing_and_a_diverging_level():
    source = _levels_web([_Role("Custom Reader", 1, 5, kind=0), _Role("Contribute", 2, 8, kind=3)])
    target = _levels_web([_Role("Contribute", 2, 16, kind=3)])

    issues = verify_site_security(source, target)

    assert issues[0] == "permission level 'Custom Reader' was not created on the target"
    assert issues[1].startswith("permission level 'Contribute' exists on the target with a different permission set")
