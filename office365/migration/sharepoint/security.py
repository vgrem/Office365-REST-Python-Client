"""Best-effort replication of a web's site groups, web-level and list-level ACLs.

Three scopes live here, because the item adapters only cover the fourth:

* the **web** scope — the source web's **custom permission levels** are created on
  the target (an assignment naming a level the target lacks cannot be restored),
  its custom site groups are re-created (the three associated groups —
  Owners/Members/Visitors — are mapped onto the target web's, which may be
  renamed), their membership is restored, and the source web's role assignments
  are reapplied to the matching principals;
* the **list** scope — a library or list whose permissions are *unique* (the
  source broke inheritance to restrict it) is replayed by
  :func:`apply_site_list_security`, because a list's own ACL is not an item ACL:
  without it a restricted library migrates world-readable at the web's level;
* the **item** scope is the adapters' (``preserve_permissions`` per item).

List ACLs are applied *after* the content (a re-broken list is briefly unreadable
and the writer needs to reach it), which is why the resolver cannot do it: the
run calls it when the migration has finished — ``migrate_site.py`` does.

Same-tenant only: a principal is matched by login (users via ``EnsureUser``, groups
by name). Anything that cannot be resolved is skipped with a warning — never
silently. Membership of the associated groups is *not* restored (it is managed by
the Microsoft 365 group behind a team site); custom-group membership is.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from office365.migration.base import PermissionEntry
from office365.migration.sharepoint.adapters import (
    _DefaultGroups,
    _perm_mask,
    _read_role_assignments,
    _TargetPrincipals,
)
from office365.sharepoint.permissions.base_permissions import BasePermissions

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


@dataclass(frozen=True)
class PermissionLevel:
    """A source web's permission level: name, order, description and its permission mask.

    ``kind`` is the service's ``RoleTypeKind``; a falsy kind marks a level the site
    defined itself (``0``/absent), while a built-in one exists on every site under a
    possibly localized name.
    """

    name: str
    description: Optional[str] = None
    order: Optional[int] = None
    mask: str = "0"
    kind: Optional[int] = None

    @property
    def is_custom(self) -> bool:
        """Whether the site defined this level itself (built-in levels are never created by us)."""
        return not self.kind


@dataclass
class ListSecurityReport:
    """What a list-level permission pass found and restored.

    ``restricted`` names the source lists that carry their *own* ACLs (everything
    else inherits the web's, which is already covered by the web scope);
    ``applied`` names the ones whose target ACL was written by this pass.
    """

    restricted: list[str] = field(default_factory=list)
    applied: list[str] = field(default_factory=list)

    def summary(self) -> str:
        """One line for a run log."""
        if not self.restricted:
            return "no list carries unique permissions"
        detail = f"{len(self.restricted)} list(s) carry unique permissions"
        if self.applied:
            detail += f", {len(self.applied)} applied"
        return detail

    def to_dict(self) -> dict[str, Any]:
        """JSON-friendly shape."""
        return {"restricted": list(self.restricted), "applied": list(self.applied)}


def capture_permission_levels(web) -> list[PermissionLevel]:
    """Read a web's permission levels — the grants a role assignment can name.

    Hidden levels are skipped: "Limited Access" is granted by the service itself
    whenever a scope is broken, never by a migration.
    """
    levels: list[PermissionLevel] = []
    for role_definition in web.role_definitions.get().execute_query():
        name = role_definition.name
        if not name or role_definition.hidden:
            continue
        levels.append(
            PermissionLevel(
                name=name,
                description=role_definition.description,
                order=role_definition.order,
                mask=_perm_mask(role_definition) or "0",
                kind=role_definition.role_type_kind,
            )
        )
    return levels


def _match_level(level: PermissionLevel, by_name: dict[str, Any], by_kind: dict[int, Any]):
    """The target level for a source level — by name, or a built-in one by its kind."""
    target = by_name.get(level.name)
    if target is None and level.kind:
        target = by_kind.get(level.kind)  # a built-in level may carry a localized name
    return target


def _apply_permission_levels(levels: list[PermissionLevel], target_web, warnings: list[str]) -> bool:
    """Create the target's missing *custom* levels; report the rest, never modify.

    An existing level whose mask differs is left as-is and reported: rewriting a
    built-in level's permissions would silently change what everyone on the target
    site can do.
    """
    existing = [rd for rd in target_web.role_definitions.get().execute_query() if rd.name]
    by_name = {rd.name: rd for rd in existing}
    by_kind = {rd.role_type_kind: rd for rd in existing if rd.role_type_kind}
    created = False
    for level in levels:
        target = _match_level(level, by_name, by_kind)
        if target is not None:
            target_mask = _perm_mask(target)
            if target_mask is not None and target_mask != level.mask:
                warnings.append(
                    f"permission level {level.name!r} exists on the target with a different permission set "
                    f"({target_mask} vs {level.mask}) — left as-is"
                )
            continue
        if not level.is_custom:
            warnings.append(f"permission level {level.name!r} (a built-in level) is missing on the target")
            continue
        mask = int(level.mask)
        target_web.role_definitions.add(
            BasePermissions(High=mask >> 32, Low=mask & 0xFFFFFFFF),
            level.name,
            level.description,
            level.order,
        )
        created = True
    if created:
        target_web.context.execute_query()
    return created


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

    Best-effort and additive: a permission level the target lacks is created when
    the *site* defined it (a built-in one is reported instead), existing target
    groups are reused (custom groups are created only when missing), and a role
    assignment that is already present is left alone. Unresolvable principals are
    appended to ``warnings``.
    """
    groups = capture_site_groups(source_web)
    levels = capture_permission_levels(source_web)
    source_defaults = _DefaultGroups(source_web)
    assignments = _read_role_assignments(source_web, normalize=source_defaults.normalize)
    if not groups and not assignments and not levels:
        return

    _apply_permission_levels(levels, target_web, warnings)  # assignments name levels
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


def _normalize(securable):
    """The principal normalizer for a securable object's web (renamed sites compare)."""
    return _DefaultGroups(securable.context.web).normalize


def capture_list_security(securable) -> Optional[list[PermissionEntry]]:
    """A list's own role assignments, or ``None`` when it simply inherits the web's.

    ``HasUniqueRoleAssignments`` is not part of a plain list read, so it costs one
    extra GET — issued only inside a ``preserve_permissions`` pass. The same shape
    works for any securable object, which is what makes the source and target sides
    of the list diff compare like with like.
    """
    properties = securable.ensure_properties(["HasUniqueRoleAssignments"]).execute_query().properties
    if not properties.get("HasUniqueRoleAssignments"):
        return None
    return _read_role_assignments(securable, normalize=_normalize(securable))


def _pairs(entries: Optional[list[PermissionEntry]]) -> Optional[set[tuple[str, str]]]:
    """Every ``(principal, role name)`` in a read result (``None`` stays ``None``)."""
    if entries is None:
        return None
    return {(entry.principal_name, role) for entry in entries for role in entry.roles}


def _list_pairs(source_web, target_web, titles: Optional[list[str]] = None) -> list[tuple[Any, Any]]:
    """``(source list, target list)`` for every list both webs have, by title."""
    wanted = {title.casefold() for title in titles} if titles is not None else None
    target_lists = {sp_list.title: sp_list for sp_list in target_web.lists.get().execute_query() if sp_list.title}
    pairs: list[tuple[Any, Any]] = []
    for source_list in source_web.lists.get().execute_query():
        title = source_list.title
        if not title or (wanted is not None and title.casefold() not in wanted):
            continue
        target_list = target_lists.get(title)
        if target_list is not None:
            pairs.append((source_list, target_list))
    return pairs


def _apply_list_acl(
    source_pairs: set[tuple[str, str]],
    target_list,
    principals: _TargetPrincipals,
    warnings: list[str],
) -> bool:
    """Break the target list's inheritance (once) and add the missing assignments."""
    wrote = False
    target_pairs = _pairs(capture_list_security(target_list))
    if target_pairs is None:  # still inheriting: make the source's ACL the list's own
        target_list.break_role_inheritance(copy_role_assignments=False, clear_sub_scopes=False)
        target_list.context.execute_query()
        target_pairs = set()
        wrote = True
    for principal_name, role_name in sorted(source_pairs - target_pairs):
        principal = principals.principal(principal_name)
        if principal is None:
            continue
        role = principals.role(role_name)
        if role is None:
            warnings.append(f"could not resolve role {role_name!r} on the target")
            continue
        target_list.add_role_assignment(principal, role)
        wrote = True
    if wrote:
        target_list.context.execute_query()
    return wrote


def apply_site_list_security(
    source_web,
    target_web,
    *,
    lists: Optional[list[str]] = None,
    warnings: Optional[list[str]] = None,
) -> ListSecurityReport:
    """Replay every source list's *unique* ACLs onto its target counterpart.

    Additive and idempotent: a target list that still inherits has its inheritance
    broken once, an assignment that is already present is left alone, and a target
    list that is *not* restricted on the source is never touched. Pass ``lists``
    (titles) to narrow the pass. Unresolvable principals are appended to
    ``warnings``; run this **after** the content — a freshly broken list is
    unreadable to everyone but the writer.
    """
    notes: list[str] = [] if warnings is None else warnings
    report = ListSecurityReport()
    principals = _TargetPrincipals(target_web, notes)
    for source_list, target_list in _list_pairs(source_web, target_web, lists):
        source_pairs = _pairs(capture_list_security(source_list))
        if not source_pairs:  # inherits, or unique with nothing readable to restore
            continue
        report.restricted.append(source_list.title)
        if _apply_list_acl(source_pairs, target_list, principals, notes):
            report.applied.append(source_list.title)
    return report


def verify_list_security(source_web, target_web, *, lists: Optional[list[str]] = None) -> list[str]:
    """Reconcile every list's own ACL against the source (read-only).

    Returns human-readable notes for anything a requested ``preserve_permissions``
    run could not restore — including the direction that matters most: a list the
    source restricts but the target still leaves at the web's permissions.
    """
    issues: list[str] = []
    for source_list, target_list in _list_pairs(source_web, target_web, lists):
        title = source_list.title
        source_pairs = _pairs(capture_list_security(source_list))
        target_pairs = _pairs(capture_list_security(target_list))
        if source_pairs is None:
            if target_pairs is not None:
                issues.append(
                    f"list {title!r} is restricted on the target but inherits the web's permissions on the source"
                )
            continue
        if not source_pairs:  # unique on the source, but nothing readable to reconcile
            continue
        if target_pairs is None:
            issues.append(
                f"list {title!r} inherits the web's permissions on the target; the source restricts it "
                f"({len(source_pairs)} assignment(s))"
            )
            continue
        missing = sorted(source_pairs - target_pairs)
        extra = sorted(target_pairs - source_pairs)
        if missing:
            detail = ", ".join(f"{principal} -> {role}" for principal, role in missing[:5])
            issues.append(f"list {title!r}: role assignment(s) not restored: {detail}")
        if extra:
            detail = ", ".join(f"{principal} -> {role}" for principal, role in extra[:5])
            issues.append(f"list {title!r}: role assignment(s) the source does not grant: {detail}")
    return issues


def _level_gaps(source_web, target_web) -> list[str]:
    """Permission levels the source grants with that the target does not match."""
    existing = [rd for rd in target_web.role_definitions.get().execute_query() if rd.name]
    by_name = {rd.name: rd for rd in existing}
    by_kind = {rd.role_type_kind: rd for rd in existing if rd.role_type_kind}
    issues: list[str] = []
    for level in capture_permission_levels(source_web):
        target = _match_level(level, by_name, by_kind)
        if target is None:
            issues.append(f"permission level {level.name!r} was not created on the target")
            continue
        target_mask = _perm_mask(target)
        if target_mask is not None and target_mask != level.mask:
            issues.append(
                f"permission level {level.name!r} exists on the target with a different permission set "
                f"({target_mask} vs {level.mask})"
            )
    return issues


def verify_site_security(source_web, target_web) -> list[str]:
    """Reconcile a migrated web's permission levels, site groups and assignments.

    Returns human-readable notes for anything a requested ``preserve_permissions``
    run could not restore (empty means the site scope matches). Associated-group
    membership is out of scope and never reported, and a level's permissions are
    only compared — never rewritten.
    """
    source_defaults = _DefaultGroups(source_web)
    target_defaults = _DefaultGroups(target_web)
    target_groups = {g.title: g for g in target_web.site_groups.get().execute_query() if g.title}
    issues: list[str] = []
    for note in _level_gaps(source_web, target_web):
        issues.append(note)
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
