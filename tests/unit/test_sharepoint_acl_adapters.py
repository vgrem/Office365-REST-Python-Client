"""Tests for the SharePoint role-assignment capture helpers (offline)."""

from __future__ import annotations

from office365.migration.base import Principal, is_puid, normalize_puid
from office365.migration.sharepoint.adapters import (
    SharePointLibrarySource,
    _is_user_principal,
    _perm_mask,
    _read_role_assignments,
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
    def __init__(self, login: str, principal_type: PrincipalType, member_id: int) -> None:
        self.login_name = login
        self.user_principal_name = login
        self.principal_type = principal_type
        self.id = member_id


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


def test_perm_mask_is_decimal_and_defensive():
    # (176 << 32) | 138612833 == 756052856929 (live-verified "Read" mask)
    assert _perm_mask(_Role("Read", 176, 138612833)) == "756052856929"
    assert _perm_mask(object()) is None


def test_is_user_principal():
    assert _is_user_principal(_Member("u", PrincipalType.User, 1))
    assert not _is_user_principal(_Member("g", PrincipalType.SecurityGroup, 2))
    assert not _is_user_principal(object())


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


def test_is_puid():
    assert is_puid("1003200065102863")
    # SharePoint exposes the PUID as hex; the digits may include a-f (e.g. user 7,
    # whose NameId is 100320006514b083) and must not be mistaken for non-numeric.
    assert is_puid("100320006514b083")
    assert is_puid("100320006514B083")
    assert is_puid("0x100320006514b083")
    assert not is_puid("f310f81b-4066-4591-bcf3-e88804b12315")
    assert not is_puid("f310f81b40664591bcf3e88804b12315")  # GUID without dashes
    assert not is_puid("10032000651")  # too short
    assert not is_puid("i:0#.f|membership|jane@contoso.com")
    assert not is_puid("app@sharepoint")
    assert not is_puid(None)
    assert not is_puid("")


def test_normalize_puid_strips_the_literal_prefix_and_whitespace():
    # Only the digits belong in ``SystemId``: the service parses it as a number,
    # so a client's ``0x`` rendering must not be carried through verbatim.
    assert normalize_puid("100320006514b083") == "100320006514b083"
    assert normalize_puid("0x100320006514b083") == "100320006514b083"
    assert normalize_puid("  0X1003200065102863\n") == "1003200065102863"
    assert normalize_puid("100320006514B083") == "100320006514B083"  # case is preserved
    assert normalize_puid("f310f81b-4066-4591-bcf3-e88804b12315") is None
    assert normalize_puid("0x") is None
    assert normalize_puid(None) is None
    assert normalize_puid("") is None


def test_principal_for_canonicalizes_a_prefixed_puid():
    folder = _Folder({10: _User("i:0#.f|membership|jane@contoso.com", "0x100320006514b083", "Jane")})
    source = SharePointLibrarySource(folder)

    principal = source._principal_for(10)

    assert principal is not None
    assert principal.system_id == "100320006514b083"
    assert source.warnings == []


class _NameId:
    def __init__(self, name_id) -> None:
        self.NameId = name_id


class _User:
    def __init__(self, login, name_id, title=None, email=None) -> None:
        self.login_name = login
        self.title = title
        self.properties = {"UserId": _NameId(name_id), "Email": email}


class _Get:
    def __init__(self, user) -> None:
        self._user = user

    def get(self):
        return self

    def execute_query(self):
        return self._user


class _SiteUsers:
    def __init__(self, users) -> None:
        self._users = users

    def get_by_id(self, key):
        return _Get(self._users[key])


class _Folder:
    def __init__(self, users) -> None:
        self.server_relative_url = "/sites/x/Docs"
        self.context = type("Ctx", (), {"web": type("Web", (), {"site_users": _SiteUsers(users)})()})()


def test_principal_for_blanks_a_non_puid_system_id():
    folder = _Folder(
        {1073741822: _User("i:0i.t|00000003-0000-0ff1-ce00-000000000000|app@sharepoint", "app@sharepoint", "User")}
    )
    source = SharePointLibrarySource(folder)

    principal = source._principal_for(1073741822)

    assert principal is not None
    assert principal.system_id is None
    assert any("PUID" in w for w in source.warnings)
    assert source._principal_for(1073741822) is principal  # cached


def test_principal_for_keeps_a_valid_puid():
    folder = _Folder({10: _User("i:0#.f|membership|vgrem@mediadev8.onmicrosoft.com", "1003200065102863", "Vadim")})
    source = SharePointLibrarySource(folder)

    principal = source._principal_for(10)

    assert principal is not None
    assert principal.system_id == "1003200065102863"
    assert principal.login_name == "i:0#.f|membership|vgrem@mediadev8.onmicrosoft.com"
    assert principal.display_name == "Vadim"
    assert source.warnings == []
