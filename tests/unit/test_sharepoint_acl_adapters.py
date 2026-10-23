"""Tests for the SharePoint role-assignment capture helpers (offline)."""

from __future__ import annotations

from office365.migration.base import Principal
from office365.migration.sharepoint.adapters import (
    _read_role_assignments,
    _resolve_group_ownership,
)
from office365.sharepoint.principal.type import PrincipalType


class _BasePermissions:
    def __init__(self, high: int, low: int) -> None:
        self.High = high
        self.Low = low


class _Role:
    def __init__(self, name: str, high: int, low: int) -> None:
        self.name = name
        self.base_permissions = _BasePermissions(high, low)


class _Member:
    def __init__(
        self, login: str, principal_type: PrincipalType | None, member_id: int, title: str | None = None
    ) -> None:
        self.login_name = login
        self.user_principal_name = login
        self.principal_type = principal_type
        self.id = member_id
        self.title = title or login


class _Assignment:
    def __init__(self, member: _Member, roles: list[_Role]) -> None:
        self.member = member
        self.role_definition_bindings = roles


class _Assignments:
    def __init__(self, assignments: list[_Assignment]) -> None:
        self._items = assignments

    def expand(self, _props) -> _Assignments:
        return self

    def get(self) -> _Assignments:
        return self

    def execute_query(self) -> list[_Assignment]:
        return self._items


class _Securable:
    def __init__(self, assignments: list[_Assignment]) -> None:
        self.role_assignments = _Assignments(assignments)


def test_read_role_assignments_captures_masks_and_resolves_users_only():
    resolved: list[int] = []

    def resolve(user_id):
        resolved.append(user_id)
        return Principal("i:0#.f|membership|a@contoso.com", "1003200065102863", "Alice")

    user = _Member("i:0#.f|membership|a@contoso.com", PrincipalType.User, 10)
    group = _Member("Team Owners", PrincipalType.SecurityGroup, 20)
    securable = _Securable(
        [
            _Assignment(user, [_Role("Read", 176, 138612833)]),
            _Assignment(group, [_Role("Contribute", 1, 2)]),
        ]
    )

    entries = _read_role_assignments(securable, resolve=resolve)

    assert entries[0].roles == ["Read"]
    assert entries[0].role_masks == {"Read": "756052856929"}
    assert entries[0].system_id == "1003200065102863"
    assert entries[0].display_name == "Alice"
    assert entries[1].system_id is None  # a group is never resolved to a PUID
    assert resolved == [10]


class _OwnerResource:
    def __init__(self, owner) -> None:
        self._owner = owner

    def get(self) -> _OwnerResource:
        return self

    def execute_query(self) -> object:
        return self._owner


class _SiteGroup:
    # A real ``Group`` extends ``Principal``, so it does carry a kind.
    principal_type = PrincipalType.SharePointGroup

    def __init__(self, title: str, owner) -> None:
        self.title = title
        self.owner = _OwnerResource(owner)


class _GroupCollection:
    def __init__(self, groups: list[_SiteGroup]) -> None:
        self._groups = groups

    def get(self) -> _GroupCollection:
        return self

    def execute_query(self) -> list[_SiteGroup]:
        return self._groups


class _OwnerWeb:
    def __init__(self, groups: list[_SiteGroup]) -> None:
        self.site_groups = _GroupCollection(groups)


def test_resolve_group_ownership_follows_the_chain_to_a_user():
    # Live shape: Visitors is owned by the Owners group, which is owned by a user.
    alice = _Member("i:0#.f|membership|a@contoso.com", PrincipalType.User, 10, title="Alice")
    owners = _SiteGroup("Owners", alice)
    web = _OwnerWeb([_SiteGroup("Visitors", owners), owners])

    def resolve(user_id):
        return Principal("i:0#.f|membership|a@contoso.com", "1003200065102863", "Alice")

    owner, groups = _resolve_group_ownership(web, "Visitors", resolve)

    assert groups == ["Owners"]  # nearest first
    assert owner is not None and owner.system_id == "1003200065102863"
