"""``Prefer`` request-header helpers.

The ``Prefer`` header opts a single request into non-default server behaviour.
The client exposes the shared-lock bypass used when a file is open for editing
(e.g. in Office) and would otherwise be rejected with HTTP 423, and the
``respond-async`` preference used by OData services that can accept a request
asynchronously.
"""

from __future__ import annotations

from office365.runtime.http.request_options import RequestOptions

#: Value of the ``Prefer`` header that bypasses a *shared lock* on a file.
BYPASS_SHARED_LOCK = "bypass-shared-lock"

#: Value of the ``Prefer`` header that asks the service to answer ``202 Accepted``
#: with a monitor URL instead of blocking until the work completes.
RESPOND_ASYNC = "respond-async"

#: Value of the ``Prefer`` header that asks the service to return evolvable-enum
#: members it would otherwise collapse to ``unknownFutureValue`` (Microsoft Graph).
INCLUDE_UNKNOWN_ENUM_MEMBERS = "include-unknown-enum-members"

#: Value of the ``Prefer`` header required to filter a drive item by
#: ``lastModifiedDateTime``. The service warns the result may be incomplete
#: because the property is not indexed, but without the header it rejects the
#: whole request rather than returning an approximate answer.
TRY_FILTER_LAST_MODIFIED_DATE_TIME = "TryFilterLastModifiedDateTimeTimeWarningMayFailRandomly"

#: Value of the ``Prefer`` header that turns a ``PATCH`` into an *upsert*: a
#: ``PATCH`` against a (client-keyed) resource that does not exist creates it
#: instead of returning ``404``. Requires the service to declare the entity set
#: upsertable (Microsoft Graph ``Upsertable`` / alternate key). See
#: :func:`prefer_upsert`.
CREATE_IF_MISSING = "create-if-missing"

#: Value of the ``Prefer`` header that asks the service to return the canonical
#: representation of the affected resource in the response body (Microsoft
#: Graph). Used together with :data:`CREATE_IF_MISSING` so an upsert yields the
#: persisted entity rather than an empty ``204``.
RETURN_REPRESENTATION = "return=representation"


def _prefer_values(request: RequestOptions) -> list[str]:
    """The ``Prefer`` header values already set on a request, split on commas."""
    header = request.headers.get("Prefer")
    if not header:
        return []
    return [value.strip() for value in header.split(",") if value.strip()]


def add_prefer(request: RequestOptions, *values: str) -> None:
    """Merge one or more values into the request's ``Prefer`` header (idempotent).

    Unlike :func:`prefer_bypass_shared_lock` and friends (which set a single
    header), this appends to whatever is already there without duplicating an
    existing value — so a collection can layer a property-specific preference on
    top of one the caller attached by hand.
    """
    merged = _prefer_values(request)
    for value in values:
        if value and value not in merged:
            merged.append(value)
    if merged:
        request.set_header("Prefer", ", ".join(merged))


def prefer_bypass_shared_lock(request: RequestOptions) -> None:
    """Attach ``Prefer: bypass-shared-lock`` to a request.

    A shared lock (as opposed to a check-out lock) is placed on a file while it
    is open for coauthoring. Only some operations honour the bypass - notably
    delete. Content uploads cannot bypass a shared lock.

    Attach it to a single request with ``context.before_execute``, or pass
    ``bypass_shared_lock=True`` to ``delete_object``.
    """
    request.set_header("Prefer", BYPASS_SHARED_LOCK)


def prefer_respond_async(request: RequestOptions, wait: int | None = None) -> None:
    """Attach ``Prefer: respond-async`` to a request.

    Microsoft Graph and other OData services document ``Prefer: respond-async``
    on operations that may take longer than a single request: instead of holding
    the connection open, the service answers ``202 Accepted`` with a ``Location``
    header pointing at an operation-status (monitor) URL. Poll that URL (see
    :mod:`office365.runtime.respond_async`) until the operation completes.

    Requests that finish quickly are answered normally (the preference is a
    hint), so callers must handle both the synchronous and the ``202`` outcomes.

    Args:
        request: The request to annotate.
        wait: Optional RFC 7240 ``wait`` preference (seconds) advising the server
            how long the client is willing to wait before responding
            asynchronously. Rendered as ``Prefer: respond-async, wait=N``.
    """
    value = RESPOND_ASYNC if wait is None else f"{RESPOND_ASYNC}, wait={wait}"
    request.set_header("Prefer", value)


def prefer_create_if_missing(request: RequestOptions) -> None:
    """Attach ``Prefer: create-if-missing`` to a request.

    Merges (rather than replaces) the header so it can be combined with
    :func:`prefer_return_representation` — see :func:`prefer_upsert`.
    """
    add_prefer(request, CREATE_IF_MISSING)


def prefer_return_representation(request: RequestOptions) -> None:
    """Attach ``Prefer: return=representation`` to a request."""
    add_prefer(request, RETURN_REPRESENTATION)


def prefer_upsert(request: RequestOptions) -> None:
    """Opt a single ``PATCH`` into the server-side *upsert* pattern.

    Attaches ``Prefer: create-if-missing, return=representation`` in one go: the
    resource addressed by the request (an alternate-key or singleton URL) is
    created when missing and updated otherwise, and the canonical representation
    is returned in the response body.

    The service must support it — generally an entity set that declares an
    alternate key (Microsoft Graph ``Upsertable``). When it does not, the server
    answers ``404`` for a missing resource (or rejects the request); callers that
    need a universal operation fall back to the client-side lookup-then-write
    path in :meth:`~office365.entity_collection.EntityCollection.upsert`.
    """
    add_prefer(request, CREATE_IF_MISSING, RETURN_REPRESENTATION)


def prefer_include_unknown_enum_members(request: RequestOptions) -> None:
    """Attach ``Prefer: include-unknown-enum-members`` to a request.

    Microsoft Graph marks newer members of some enums as "evolvable": by default
    it collapses them to ``unknownFutureValue`` so that older clients keep
    working. Adding this preference asks the service to return the real member
    (for example ``shared`` for :class:`ChannelMembershipType`, which would
    otherwise read as ``unknownFutureValue``).

    Attach it to a single request with ``context.before_execute`` (repeat for
    every query that needs it).
    """
    request.set_header("Prefer", INCLUDE_UNKNOWN_ENUM_MEMBERS)
