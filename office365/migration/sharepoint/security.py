"""Best-effort replication of a web's site groups and web-level role assignments.

The item adapters carry each item's *unique* ACL (``preserve_permissions``); the
web scope is handled here: the source web's custom site groups are re-created on
the target (the three associated groups — Owners/Members/Visitors — are mapped onto
the target web's, which may be renamed), their membership is restored, and the
source web's role assignments are reapplied to the matching principals.

Same-tenant only: a principal is matched by login (users via ``EnsureUser``, groups
by name). Anything that cannot be resolved is skipped with a warning — never
silently. Membership of the associated groups is *not* restored (it is managed by
the Microsoft 365 group behind a team site); custom-group membership is.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from office365.migration.sharepoint.adapters import (
    _DefaultGroups,
    _read_role_assignments,
    _TargetPrincipals,
)

#: Group properties copied verbatim when they differ on the target group.
_GROUP_FLAGS = (
    "AllowMembersEditMembership",
    "AllowRequestToJoinLeave",
    "AutoAcceptRequestToJoinLeave",
    "OnlyAllowMembersViewMembership",
)


@dataclass
class SiteGroup:
    """A source web's site group: identity, settable flags and (for custom groups) members."""

    title: str
    description: Optional[str] = None
    flags: dict[str, bool] = field(default_factory=dict)
    members: list[str] = field(default_factory=list)
    is_default: bool = False


def capture_site_groups(web) -> list[SiteGroup]:
    """Read a web's site groups (flags for all; membership for custom groups only)."""
    defaults = _DefaultGroups(web)
    result: list[SiteGroup] = []
    for group in web.site_groups.get().execute_query():
        title = group.title
        if not title:
            continue
        is_default = defaults.normalize(title).startswith("default:")
        flags = {name: bool(value) for name in _GROUP_FLAGS if (value := group.properties.get(name)) is not None}
        members: list[str] = []
        if not is_default:  # associated-group membership is managed by the M365 group
            for user in group.users.get().execute_query():
                login = user.login_name or user.user_principal_name
                if login:
                    members.append(login)
        result.append(
            SiteGroup(
                title=title,
                description=group.description,
                flags=flags,
                members=members,
                is_default=is_default,
            )
        )
    return result


def _member_logins(group) -> set[str]:
    logins: set[str] = set()
    for user in group.users.get().execute_query():
        login = user.login_name or user.user_principal_name
        if login:
            logins.add(login)
    return logins


def _assignment_pairs(web, normalize) -> set[tuple[str, str]]:
    """Every ``(principal, role name)`` the web grants, normalized for a renamed site."""
    return {
        (entry.principal_name, role_name)
        for entry in _read_role_assignments(web, normalize=normalize)
        for role_name in entry.roles
    }


def _ensure_target_group(
    group: SiteGroup,
    source_defaults: _DefaultGroups,
    principals: _TargetPrincipals,
    target_web,
    existing: dict[str, Any],
    warnings: list[str],
):
    """The target group for a source group: the associated group, or a created custom one."""
    if group.is_default:
        return principals.principal(source_defaults.normalize(group.title))
    target_group = existing.get(group.title)
    if target_group is not None:
        return target_group
    try:
        target_group = target_web.site_groups.add(group.title, group.description).execute_query()
    except Exception as e:  # noqa: BLE001 — a failed group create is reported, not fatal
        warnings.append(f"could not create site group {group.title!r}: {e}")
        return None
    existing[group.title] = target_group
    return target_group


def _apply_group_properties(target_group, group: SiteGroup) -> None:
    updates: dict[str, Any] = {}
    if group.description != target_group.description:
        updates["Description"] = group.description or ""
    for name, value in group.flags.items():
        if target_group.properties.get(name) != value:
            updates[name] = value
    if updates:
        target_group.update_properties(**updates)


def _apply_group_members(target_group, group: SiteGroup, principals: _TargetPrincipals, warnings: list[str]) -> bool:
    existing = _member_logins(target_group)
    added = False
    for login in group.members:
        if login in existing:
            continue
        user = principals.user(login)
        if user is None:
            warnings.append(f"site group {group.title!r}: could not resolve member {login!r}")
            continue
        target_group.users.add_user(user)
        added = True
    return added


def apply_site_security(source_web, target_web, warnings: list[str]) -> None:
    """Re-create the source web's site groups and web-level role assignments on the target.

    Best-effort and additive: existing target groups are reused (custom groups are
    created only when missing), and a role assignment that is already present is
    left alone. Unresolvable principals are appended to ``warnings``.
    """
    groups = capture_site_groups(source_web)
    source_defaults = _DefaultGroups(source_web)
    assignments = _read_role_assignments(source_web, normalize=source_defaults.normalize)
    if not groups and not assignments:
        return

    principals = _TargetPrincipals(target_web, warnings)
    target_defaults = _DefaultGroups(target_web)
    existing_groups = {g.title: g for g in target_web.site_groups.get().execute_query() if g.title}
    existing_assignments = _assignment_pairs(target_web, target_defaults.normalize)

    wrote = False
    for group in groups:
        target_group = _ensure_target_group(group, source_defaults, principals, target_web, existing_groups, warnings)
        if target_group is None:
            continue
        if not group.is_default:
            _apply_group_properties(target_group, group)
            wrote |= _apply_group_members(target_group, group, principals, warnings)

    for entry in assignments:
        principal = principals.principal(entry.principal_name)
        if principal is None:
            continue
        for role_name in entry.roles:
            role = principals.role(role_name)
            if role is None:
                warnings.append(f"could not resolve role {role_name!r} on the target")
                continue
            if (entry.principal_name, role_name) in existing_assignments:
                continue
            target_web.add_role_assignment(principal, role)
            wrote = True

    if wrote:
        target_web.context.execute_query()


def verify_site_security(source_web, target_web) -> list[str]:
    """Reconcile a migrated web's site groups and role assignments against the source.

    Returns human-readable notes for anything a requested ``preserve_permissions``
    run could not restore (empty means the site scope matches). Associated-group
    membership is out of scope and never reported.
    """
    source_defaults = _DefaultGroups(source_web)
    target_defaults = _DefaultGroups(target_web)
    target_groups = {g.title: g for g in target_web.site_groups.get().execute_query() if g.title}
    issues: list[str] = []
    for group in capture_site_groups(source_web):
        if group.is_default:
            continue
        target_group = target_groups.get(group.title)
        if target_group is None:
            issues.append(f"site group {group.title!r} was not created on the target")
            continue
        missing = [login for login in group.members if login not in _member_logins(target_group)]
        if missing:
            issues.append(f"site group {group.title!r}: member(s) not restored: {', '.join(missing)}")
    source_assignments = _assignment_pairs(source_web, source_defaults.normalize)
    target_assignments = _assignment_pairs(target_web, target_defaults.normalize)
    for principal_name, role_name in sorted(source_assignments - target_assignments):
        issues.append(f"web role assignment not restored: {principal_name} -> {role_name}")
    return issues
