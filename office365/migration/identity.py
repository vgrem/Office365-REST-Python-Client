"""Identity mapping — resolve source principals onto target principals.

Authorship and ACLs are expressed as *principals*, and a principal is a
tenant-local fact: ``i:0#.f|membership|anna@contoso.com`` means nothing on a
tenant where the same person is ``anna@fabrikam.com``. Migrating inside one
tenant needs no map (the logins already resolve); migrating across tenants — or
into a tenant where logins were normalized — needs one, and the source PUID in
:attr:`~office365.migration.base.Principal.system_id` is actively wrong.

Three resolution rules, in order, each cheaper than the next:

1. **Exact** — the source login, its claims tail (``…|anna@contoso.com``) or the
   CSV's own key, compared case-insensitively.
2. **Domain rewrite** — swap the e-mail domain (``contoso.com`` → ``fabrikam.com``)
   while keeping the rest of the login, including the claims prefix. This covers
   the common case ("same people, new domain") without a CSV row per person.
3. **Unmapped policy** — ``skip`` (drop the principal and report it), ``fail``
   (raise at the first miss) or ``fallback_owner`` (substitute one known account).

A name that is already a *target* login resolves to itself, so applying the map
twice (a resumed run re-mapping an item the previous run already mapped) is a
no-op rather than a miss.

A miss is never silent: every unmapped name is kept in :attr:`IdentityMap.unmapped`
and surfaces in the run report.

The map is applied by the engine (:class:`~office365.migration.runner.MigrationRunner`)
to the item's author/editor and to the ACL entries, so it applies to every adapter
pair — client-side REST and the server-side package target alike.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field, replace
from enum import Enum
from pathlib import Path
from typing import Iterable, Mapping, Sequence, Tuple, Union

from office365.migration.base import PermissionEntry, Principal

__all__ = [
    "IdentityEntry",
    "IdentityMap",
    "ResolvedIdentity",
    "UnmappedPolicy",
    "UnmappedPrincipalError",
]

#: Claims logins are ``<claim type>|<value>``, so the tail is the e-mail/UPN.
_CLAIMS_SEPARATOR = "|"

#: Column aliases accepted in a mapping CSV (lower-cased).
_SOURCE_COLUMNS = ("source", "source_login", "source_email", "source_principal")
_TARGET_COLUMNS = ("target", "target_login", "target_email", "target_principal")
_SYSTEM_ID_COLUMNS = ("system_id", "target_system_id", "puid")


class UnmappedPolicy(str, Enum):
    """What to do with a principal the map cannot resolve."""

    SKIP = "skip"
    """Drop the principal: authorship is cleared, the ACL entry is not applied."""

    FAIL = "fail"
    """Raise :class:`UnmappedPrincipalError` at the first miss."""

    FALLBACK_OWNER = "fallback_owner"
    """Substitute ``fallback_owner`` (for example a migration service account)."""

    def __str__(self) -> str:  # pragma: no cover - display only
        return self.value

    @classmethod
    def parse(cls, value: "str | UnmappedPolicy") -> "UnmappedPolicy":
        """Coerce a string (case/separator tolerant) into a policy."""
        if isinstance(value, cls):
            return value
        normalized = str(value).strip().lower().replace("-", "_").replace(" ", "_")
        try:
            return cls(normalized)
        except ValueError:
            allowed = ", ".join(p.value for p in cls)
            raise ValueError(f"unknown unmapped policy {value!r} (expected one of: {allowed})") from None


class UnmappedPrincipalError(LookupError):
    """A principal could not be resolved and the policy is ``fail``."""

    def __init__(self, principal_name: str) -> None:
        super().__init__(f"no target identity for principal {principal_name!r}")
        self.principal_name = principal_name


@dataclass(frozen=True)
class IdentityEntry:
    """One mapping row: a source principal and the target principal it becomes.

    ``system_id`` is the *target's* PUID; supply it when the deployment needs
    ``UserGroup.xml`` to carry a resolved ``SystemId`` (a cross-tenant package).
    """

    source: str
    target: str
    system_id: str | None = None


@dataclass(frozen=True)
class ResolvedIdentity:
    """The target-side identity a source principal resolves to."""

    login_name: str
    system_id: str | None = None
    email: str | None = None


def _email_of(login_name: str) -> str | None:
    """The e-mail inside a login (``i:0#.f|membership|a@b.com`` → ``a@b.com``)."""
    tail = login_name.rpartition(_CLAIMS_SEPARATOR)[2].strip()
    return tail if "@" in tail else None


def _key(name: str) -> str:
    """Case-insensitive lookup key: the login as written, and its claims tail."""
    return name.strip().casefold()


@dataclass
class IdentityMap:
    """Source → target principal map (see the module docstring for the rules)."""

    entries: Sequence[Union[IdentityEntry, Tuple[str, ...]]] = ()
    domain_rewrites: Mapping[str, str] = field(default_factory=dict)
    unmapped_policy: UnmappedPolicy = UnmappedPolicy.SKIP
    fallback_owner: str | None = None
    _index: dict[str, IdentityEntry] = field(default_factory=dict, init=False, repr=False)
    _domain_rewrites: dict[str, str] = field(default_factory=dict, init=False, repr=False)
    _domain_keys: list[tuple[str, str]] = field(default_factory=list, init=False, repr=False)
    _unmapped: list[str] = field(default_factory=list, init=False, repr=False)
    _unmapped_seen: set[str] = field(default_factory=set, init=False, repr=False)
    _known_targets: set[str] = field(default_factory=set, init=False, repr=False)
    _rewritten: int = field(default=0, init=False, repr=False)

    def __post_init__(self) -> None:
        self.unmapped_policy = UnmappedPolicy.parse(self.unmapped_policy)
        if self.unmapped_policy is UnmappedPolicy.FALLBACK_OWNER and not self.fallback_owner:
            raise ValueError("unmapped_policy='fallback_owner' requires fallback_owner=<login>")
        # Accept ``(source, target)`` / ``(source, target, system_id)`` rows as well as
        # ``IdentityEntry`` objects — the tuple is what a caller writes by hand.
        self.entries = [entry if isinstance(entry, IdentityEntry) else IdentityEntry(*entry) for entry in self.entries]
        for entry in self.entries:
            for alias in {_key(entry.source), _key(entry.source.rpartition(_CLAIMS_SEPARATOR)[2])}:
                if alias:
                    self._index.setdefault(alias, entry)
            for alias in {_key(entry.target), _key(entry.target.rpartition(_CLAIMS_SEPARATOR)[2])}:
                if alias:
                    self._known_targets.add(alias)
        # Longest domain first: ``mail.contoso.com`` has to win over ``contoso.com``.
        self._domain_rewrites = {_key(src): dst.strip() for src, dst in self.domain_rewrites.items()}
        self._domain_keys = sorted(self._domain_rewrites.items(), key=lambda pair: len(pair[0]), reverse=True)

    # ── Construction ─────────────────────────────────────────────

    @classmethod
    def from_csv(cls, path: str | Path, **kwargs) -> "IdentityMap":
        """Load a mapping CSV (``source,target[,system_id]``, header required).

        Blank lines and ``#`` comments are ignored, a UTF-8 BOM is tolerated, and
        the column order does not matter. ``kwargs`` are forwarded to the
        constructor (``domain_rewrites``, ``unmapped_policy``, ``fallback_owner``).
        """
        file_path = Path(path)
        rows = [
            line
            for line in file_path.read_text(encoding="utf-8-sig").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
        if not rows:
            raise ValueError(f"identity mapping file {file_path} is empty")
        reader = csv.DictReader(rows)
        columns = {_key(name): name for name in (reader.fieldnames or [])}
        source_column = next((columns[c] for c in _SOURCE_COLUMNS if c in columns), None)
        target_column = next((columns[c] for c in _TARGET_COLUMNS if c in columns), None)
        if not source_column or not target_column:
            raise ValueError(
                f"identity mapping file {file_path} needs a 'source' and a 'target' column "
                f"(got: {', '.join(columns.values()) or 'no header'})"
            )
        system_id_column = next((columns[c] for c in _SYSTEM_ID_COLUMNS if c in columns), None)
        entries: list[IdentityEntry] = []
        for row in reader:
            source = (row.get(source_column) or "").strip()
            target = (row.get(target_column) or "").strip()
            if not source or not target:
                continue
            system_id = (row.get(system_id_column) or "").strip() if system_id_column else ""
            entries.append(IdentityEntry(source=source, target=target, system_id=system_id or None))
        return cls(entries=entries, **kwargs)

    @classmethod
    def from_file(cls, path: str | Path, **kwargs) -> "IdentityMap":
        """Load a mapping file; only CSV is supported (``.csv``/``.txt``)."""
        suffix = Path(path).suffix.lower()
        if suffix not in {".csv", ".txt"}:
            raise ValueError(f"unsupported identity mapping file type {suffix!r}: supply a CSV")
        return cls.from_csv(path, **kwargs)

    # ── Resolution ───────────────────────────────────────────────

    def resolve(self, principal_name: str | None) -> ResolvedIdentity | None:
        """Resolve one principal name; ``None`` when it is unmapped and skipped."""
        name = (principal_name or "").strip()
        if not name:
            return None
        entry = self._index.get(_key(name))
        if entry is None:
            entry = self._index.get(_key(name.rpartition(_CLAIMS_SEPARATOR)[2]))
        if entry is not None:
            for alias in {_key(entry.target), _key(entry.target.rpartition(_CLAIMS_SEPARATOR)[2])}:
                if alias:
                    self._known_targets.add(alias)
            return ResolvedIdentity(entry.target, entry.system_id, _email_of(entry.target))
        if _key(name) in self._known_targets:
            # Already a target login: the map is idempotent, so applying it to an item
            # that a previous run (or a resumed manifest) already mapped is a no-op.
            return ResolvedIdentity(name, None, _email_of(name))
        rewritten = self._rewrite_domain(name)
        if rewritten is not None:
            self._rewritten += 1
            self._known_targets.add(_key(rewritten))
            return ResolvedIdentity(rewritten, None, _email_of(rewritten))
        if self.unmapped_policy is UnmappedPolicy.FAIL:
            self._remember(name)
            raise UnmappedPrincipalError(name)
        self._remember(name)
        if self.unmapped_policy is UnmappedPolicy.FALLBACK_OWNER:
            assert self.fallback_owner is not None  # guarded in __post_init__
            return ResolvedIdentity(self.fallback_owner, None, _email_of(self.fallback_owner))
        return None

    def resolve_principal(self, principal: Principal | None) -> Principal | None:
        """Resolve a principal, keeping its display name; ``None`` when dropped."""
        if principal is None:
            return None
        resolved = self.resolve(principal.login_name or principal.email)
        if resolved is None:
            return None
        if resolved.login_name == principal.login_name:
            # Same login inside one tenant: keep the source PUID, it is still valid.
            return principal
        return Principal(
            login_name=resolved.login_name,
            system_id=resolved.system_id,
            display_name=principal.display_name,
            email=resolved.email,
        )

    def resolve_permissions(self, permissions: Iterable[PermissionEntry]) -> list[PermissionEntry]:
        """Resolve ACL entries; unmapped ones are dropped (and reported)."""
        resolved_entries: list[PermissionEntry] = []
        for permission in permissions:
            resolved = self.resolve(permission.principal_name)
            if resolved is None:
                continue
            if resolved.login_name == permission.principal_name and resolved.system_id is None:
                resolved_entries.append(permission)
                continue
            resolved_entries.append(
                replace(
                    permission,
                    principal_name=resolved.login_name,
                    # The source PUID identifies a user in *another* tenant: carrying it
                    # would make the package target emit an unresolvable SystemId.
                    system_id=resolved.system_id,
                    email=resolved.email or permission.email,
                )
            )
        return resolved_entries

    def _rewrite_domain(self, name: str) -> str | None:
        """Swap the e-mail domain, keeping the claims prefix (``None`` when no rule fits)."""
        if not self._domain_keys:
            return None
        prefix, separator, tail = name.rpartition(_CLAIMS_SEPARATOR)
        local, at, domain = tail.partition("@")
        if not at:
            return None
        target_domain = self._domain_rewrites.get(_key(domain))
        if target_domain is None:
            return None
        rewritten_tail = f"{local}@{target_domain}"
        rewritten = f"{prefix}{separator}{rewritten_tail}" if separator else rewritten_tail
        return None if rewritten == name else rewritten

    def _remember(self, name: str) -> None:
        if name not in self._unmapped_seen:
            self._unmapped_seen.add(name)
            self._unmapped.append(name)

    # ── Reporting ────────────────────────────────────────────────

    @property
    def unmapped(self) -> list[str]:
        """Source principals nothing could be found for (first-seen order, deduped)."""
        return list(self._unmapped)

    @property
    def rewritten_count(self) -> int:
        """How many principals resolved through a domain rewrite (not an exact row)."""
        return self._rewritten

    def summary(self) -> dict[str, object]:
        """Report row describing the map's work (goes into the run summary)."""
        return {
            "identity_mappings": len(self.entries),
            "identity_rewritten": self._rewritten,
            "identity_unmapped": len(self._unmapped),
            "identity_unmapped_principals": "; ".join(self._unmapped),
            "identity_policy": self.unmapped_policy.value,
        }
