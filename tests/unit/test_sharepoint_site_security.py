"""Offline tests for best-effort web-level (site) security replication.

The item adapters restore each item's *unique* ACL; ``security.py`` covers the web
scope. These tests drive it with fakes — no network — and assert that custom groups
are created (default groups are mapped onto the target's associated groups),
membership and web role assignments are reapplied, and unresolvable principals are
warned about rather than dropped silently.
"""

from __future__ import annotations

from office365.migration.sharepoint.security import (
    SiteGroup,
    apply_site_security,
    capture_site_groups,
    verify_site_security,
)
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
    def __init__(self, name: str, role_id: int) -> None:
        self.name = name
        self.id = role_id


class _RoleDefinitions:
    def __init__(self, roles) -> None:
        self._roles = list(roles)

    def get(self):
        return self

    def execute_query(self):
        return list(self._roles)


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
        self.context = self

    def _next_id(self) -> int:
        return next(self._ids)

    def ensure_user(self, login):
        self.ensure_calls.append(login)
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


def test_capture_marks_default_groups_and_reads_only_custom_membership():
    source = _source_web()

    captured = {g.title: g for g in capture_site_groups(source)}

    assert captured["S Owners"].is_default is True
    assert captured["S Owners"].members == []  # associated-group membership is not read
    assert captured["Auditors"].is_default is False
    assert captured["Auditors"].members == ["mary@contoso.com"]


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


def test_site_group_dataclass_defaults():
    group = SiteGroup(title="X")

    assert group.is_default is False
    assert group.members == []
    assert group.flags == {}
