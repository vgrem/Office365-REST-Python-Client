"""Server-side upsert query (``PATCH`` + ``Prefer: create-if-missing``).

An *upsert* is an update whose resource is created when it does not exist. The
client expresses it as a ``PATCH`` against a resource addressed by an alternate
key (or a singleton) plus ``Prefer: create-if-missing``: the service updates the
existing resource or creates it, and ``return=representation`` asks for the
persisted representation back.

The query reuses the update plumbing (same binding object and JSON body) but,
unlike a plain update, binds the response to the entity and adds the upsert
preference and optional conditional headers. Services that do not support the
pattern answer ``404`` for a missing resource instead of creating it;
:func:`raise_if_upsert_unsupported` translates that into
:class:`~office365.runtime.exceptions.UpsertNotSupported` so the caller can fall
back to a client-side lookup-then-write.
"""

from __future__ import annotations

from typing import Optional

from office365.runtime.client_object import ClientObject
from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.exceptions import UpsertNotSupported
from office365.runtime.queries.update_entity import UpdateEntityQuery

#: Substrings that, in a ``400`` body, indicate the service rejected the upsert
#: preference/operation rather than the payload itself.
_UNSUPPORTED_TOKENS = ("create-if-missing", "prefer", "upsert", "not supported")


class UpsertEntityQuery(UpdateEntityQuery):
    """Represents a server-side upsert (``PATCH`` with ``Prefer: create-if-missing``).

    Args:
        entity: The entity to upsert (source of the body and target of the
            response). It must be addressed by an alternate key or be a
            singleton so the service can identify the resource before creating
            it.
        if_match: Optional ``If-Match`` value (optimistic concurrency; turns the
            upsert into an update-only request).
        if_none_match: Optional ``If-None-Match`` value (``*`` turns the upsert
            into a create-only request).
    """

    def __init__(
        self,
        entity: ClientObject,
        *,
        if_match: Optional[str] = None,
        if_none_match: Optional[str] = None,
    ) -> None:
        super().__init__(entity)
        # Unlike a plain update, an upsert asks for (and returns) the persisted
        # representation, so bind the response to the entity.
        self._return_type = entity
        self._if_match = if_match
        self._if_none_match = if_none_match

    @property
    def if_match(self) -> Optional[str]:
        """The ``If-Match`` precondition, if any."""
        return self._if_match

    @property
    def if_none_match(self) -> Optional[str]:
        """The ``If-None-Match`` precondition, if any."""
        return self._if_none_match


def to_upsert_not_supported(error: ClientRequestException) -> Optional[UpsertNotSupported]:
    """Classify a failed server-side upsert, or return ``None`` if it is unrelated.

    A ``404`` is the reliable signal: the alternate-key resource was missing and
    the service did not honour ``create-if-missing``. A ``400`` is ambiguous, so
    it only counts when the service names the preference/operation; otherwise the
    request was genuinely invalid and is surfaced as-is.
    """
    status = getattr(getattr(error, "response", None), "status_code", None)
    unsupported = status == 404  # noqa: PLR2004
    if status == 400:  # noqa: PLR2004
        text = f"{error.code or ''} {error.message or ''}".lower()
        unsupported = any(token in text for token in _UNSUPPORTED_TOKENS)
    if not unsupported:
        return None
    return UpsertNotSupported(
        "The service did not create the resource on PATCH "
        "(Prefer: create-if-missing was not honoured); server-side upsert is "
        "not available for this endpoint.",
        response=getattr(error, "response", None),
    )


def raise_if_upsert_unsupported(error: ClientRequestException) -> None:
    """``on_error`` handler: translate an unsupported upsert, otherwise re-raise.

    The error is always re-raised (translated or original) so that attaching this
    handler never silently swallows a failure.
    """
    wrapped = to_upsert_not_supported(error)
    if wrapped is not None:
        raise wrapped from error
    raise error
