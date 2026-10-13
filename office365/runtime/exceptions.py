"""Generic runtime request exceptions.

Concrete error types shared across products (Graph, SharePoint, ...). They
self-register with the dispatcher in
:mod:`office365.runtime.client_request_exception`, which imports this module
lazily so classification works regardless of import order.
"""

from __future__ import annotations

import re
from typing import Optional

from office365.runtime.client_request_exception import (
    ClientRequestException,
    ErrorPayload,
    register_error_type,
)


class DuplicatedObjectException(ClientRequestException):
    """Raised when creating an object that already exists (HTTP 400 + ConflictingObjects)."""

    MATCH_PRIORITY = 10
    # Lower-case: ``matches`` compares against ``payload.code.lower()``.
    # ``20117`` is OneNote's "an item with this name already exists in this location".
    _CODES = frozenset({"namealreadyexists", "errorfolderexists", "-2130575342", "20117"})

    @classmethod
    def matches(cls, payload: ErrorPayload) -> bool:
        return (
            payload.hresult in cls._CODES
            or payload.code.lower() in cls._CODES
            or any(detail.get("code") == "ConflictingObjects" for detail in payload.details)
            # The generic ``-1, System.Exception`` carries no code, so fall back to
            # the (English) message — scoped to that opaque case only.
            or (payload.hresult == "-1" and "already exists" in payload.message.lower())
        )


class ObjectNotFoundException(ClientRequestException):
    """Raised when a requested object is not found (HTTP 404 or ResourceNotFound code)."""

    MATCH_PRIORITY = 10
    _CODES = frozenset({"itemnotfound", "resourcenotfound", "notfound", "request_resourcenotfound"})
    _TYPE_NAMES = ("FileNotFoundException", "DirectoryNotFoundException", "ResourceNotFoundException")

    @classmethod
    def matches(cls, payload: ErrorPayload) -> bool:
        error_type = (payload.error_type or "").lower()
        return (
            "-2147024809" in payload.code  # System.ArgumentException (kept for back-compat)
            or "-2147024894" in payload.code  # System.IO.FileNotFoundException
            or payload.code.lower() in cls._CODES
            or any(name.lower() in error_type for name in cls._TYPE_NAMES)
        )


register_error_type(DuplicatedObjectException)
register_error_type(ObjectNotFoundException)


class FileLockedException(ClientRequestException):
    """Raised when a file is locked and the requested change is rejected (HTTP 423).

    The usual cause is a **shared lock**: the file is open for coauthoring in
    Office (web or desktop), so SharePoint/Graph refuses the write. Unlike a
    check-out lock, a shared lock cannot be broken through the API. See
    :attr:`GUIDANCE` for the available options.

    HTTP 423 is also used by ``Microsoft.SharePoint.SPFileCheckOutException``;
    that case is classified separately as
    :class:`~office365.sharepoint.exceptions.SPFileCheckOutException` (a higher
    priority match), so this type only claims status-only 423 responses.
    """

    MATCH_PRIORITY = 10
    _CODES = ("-2147018894", "spfilelockexception", "resourcelocked")

    GUIDANCE = (
        "The file is locked - typically because it is open for editing in Office. A shared lock "
        "cannot be broken through the API. Either retry until the other session closes "
        "(execute_query_retry(is_retriable=retry_on(FileLockedException))), update metadata only "
        "with ListItem.update_ex(bypass_shared_lock=True), or - for delete - pass "
        "bypass_shared_lock=True. The lock holder is available via .lock_owner."
    )

    @classmethod
    def matches(cls, payload: ErrorPayload) -> bool:
        code = payload.code.lower()
        if any(marker in code for marker in cls._CODES):
            return True
        return payload.status == 423  # noqa: PLR2004

    @property
    def lock_owner(self) -> Optional[str]:
        """Best-effort display name of the user holding the lock (parsed from the message)."""
        match = re.search(r"locked for shared use by (.+?)\s*\[", self.message, re.IGNORECASE)
        return match.group(1).strip() if match else None

    def __str__(self) -> str:
        owner = self.lock_owner
        described = self._base_description()
        if owner:
            described = f"{described} (locked by {owner})"
        return self._render(described)


register_error_type(FileLockedException)


class AccessDeniedException(ClientRequestException):
    """Raised when the caller is not permitted to perform the request (HTTP 401/403).

    This is a **product-agnostic** type: it covers Microsoft Graph symbolic
    codes (``accessDenied``, ``Authorization_RequestDenied``,
    ``ErrorAccessDenied``), SharePoint's ``System.UnauthorizedAccessException``
    HRESULT, and any status-only 401/403 response (including throttling and
    conditional-access rejections that carry no JSON body).

    It tells apart *not allowed* from *not found* (:class:`ObjectNotFoundException`)
    and *not now* (:class:`FileLockedException`), so callers can react to a denied
    permission instead of parsing error strings.
    """

    MATCH_PRIORITY = 5  # above the base catch-alls (0), below specific typed errors (10/15)
    # Lower-case: ``matches`` compares against ``payload.code.lower()``.
    _CODES = frozenset({"accessdenied", "authorization_requestdenied", "erroraccessdenied", "forbidden"})
    # E_ACCESSDENIED (0x80070005), as emitted by SharePoint/OneDrive.
    _HRESULTS = frozenset({"-2147024891"})

    GUIDANCE = (
        "The caller is not permitted to perform this request. For an app-only call, confirm the "
        "application role is granted and admin-consented; for a delegated call, confirm the signed-in "
        "user has the OAuth scope. Use require_application_permission(...) / require_role(...) to fail "
        "fast with the exact requirement. Prefer a least-privileged permission that covers the endpoint."
    )

    @classmethod
    def matches(cls, payload: ErrorPayload) -> bool:
        return payload.status in (401, 403) or payload.code.lower() in cls._CODES or payload.hresult in cls._HRESULTS


register_error_type(AccessDeniedException)


class UpsertNotSupported(ClientRequestException):
    """Raised when a service does not honour a server-side upsert (``create-if-missing``).

    A server-side upsert is a ``PATCH`` carrying ``Prefer: create-if-missing``
    against a resource addressed by an alternate key (or a singleton). Not every
    entity set supports it: a service that does not answers ``404`` for a missing
    resource instead of creating it. The client translates that response into
    this type (chained to the original error) so callers can fall back to a
    client-side lookup-then-write.

    This type is **not** registered with the payload dispatcher - it is raised by
    the client from :func:`~office365.runtime.queries.upsert_entity.raise_if_upsert_unsupported`,
    never selected by matching an error body.
    """

    GUIDANCE = (
        "The endpoint does not support server-side upsert (Prefer: create-if-missing). Fall back "
        "to a client-side lookup-then-create/update - e.g. the collection's upsert(...) helper, "
        "which reconciles locally."
    )
