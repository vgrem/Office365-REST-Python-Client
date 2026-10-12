"""SharePoint-specific request exceptions.

These self-register with
:func:`~office365.runtime.client_request_exception.register_error_type` so the
product-agnostic dispatcher in the runtime can classify SharePoint error
responses without importing this package.

Classification never matches translated messages: SharePoint encodes the error
as ``"<HRESULT>, <dotnet-type>"`` (e.g. ``"-2130575169,
Microsoft.SharePoint.SPDuplicateValuesFoundException"``), so the concrete types
below key off the numeric code and/or the embedded .NET type name — both locale
independent. Any remaining ``Microsoft.SharePoint.*`` error is caught by
:class:`SharePointException`.
"""

from __future__ import annotations

from office365.runtime.client_request_exception import (
    ClientRequestException,
    ErrorPayload,
    register_error_type,
)
from office365.runtime.exceptions import FileLockedException
from office365.sharepoint.thresholds import LIST_VIEW_THRESHOLD, SAFE_PAGE_SIZE

#: SharePoint-flavoured alias of :class:`~office365.runtime.exceptions.FileLockedException`.
#: Raised when a file is open for coauthoring (HTTP 423 /
#: ``Microsoft.SharePoint.SPFileLockException``) and therefore cannot be
#: overwritten. See ``FileLockedException.GUIDANCE`` for the available options.
SPFileLockedException = FileLockedException


class SharePointException(ClientRequestException):
    """Base class for SharePoint server exceptions (``Microsoft.SharePoint.*``).

    Serves as a catch-all so callers can ``except SharePointException`` for any
    otherwise-unclassified SharePoint error. Concrete subclasses set
    :attr:`_HRESULTS` and/or :attr:`_TYPE_NAMES`; they are picked over this base
    by :attr:`ClientRequestException.MATCH_PRIORITY`.
    """

    MATCH_PRIORITY = 0

    _HRESULTS: tuple[str, ...] = ()
    _TYPE_NAMES: tuple[str, ...] = ()

    @classmethod
    def matches(cls, payload: ErrorPayload) -> bool:
        if not cls._HRESULTS and not cls._TYPE_NAMES:
            # Catch-all: any SharePoint-flavoured code, whatever the concrete type.
            return "microsoft.sharepoint." in payload.code.lower()
        error_type = (payload.error_type or "").lower()
        if payload.hresult is not None and payload.hresult in cls._HRESULTS:
            return True
        return any(name.lower() in error_type for name in cls._TYPE_NAMES)


class SecurityValidationException(SharePointException):
    """Raised when SharePoint rejects an expired/invalid form digest (HTTP 403)."""

    MATCH_PRIORITY = 10
    _HRESULTS = ("-2130575251",)


class SPQueryThrottledException(SharePointException):
    """Raised when a query exceeds the SharePoint **list view threshold**.

    SharePoint blocks (HTTP 500) queries that filter or sort on a **non-indexed**
    column and would scan/return more than the threshold (5,000 items by default),
    and sometimes single-shot collection loads of a large collection. See
    https://learn.microsoft.com/en-us/microsoft-365/community/how-to-handle-list-view-threshold

    Classification keys off the stable error code (``-2147024860``) and the
    embedded type name, so localized messages are handled the same way.
    """

    MATCH_PRIORITY = 10
    _HRESULTS = ("-2147024860",)
    _TYPE_NAMES = ("SPQueryThrottledException",)

    GUIDANCE = (
        f"This exceeds the SharePoint list view threshold ({LIST_VIEW_THRESHOLD:,} items by default). "
        f"To fix it, either: (1) page through the data with get_all(page_size<={SAFE_PAGE_SIZE}) "
        "(for list items) or Folder.get_files() / List.get_items(query, page_size=...); "
        "(2) filter/sort on an indexed column - add one with List.ensure_indexed('Column'); "
        "or (3) filter on ID (always indexed)."
    )

    def __str__(self) -> str:
        return self._render(self._base_description())


class SPFileCheckOutException(SharePointException):
    """Raised when a file operation is rejected because of its check-out state.

    SharePoint returns HTTP 423 here too, but this is a *check-out* lock (an
    explicit reservation), not the shared coauthoring lock behind
    :class:`~office365.runtime.exceptions.FileLockedException`. A check-out can
    be released by its owner, so it is actionable rather than permanent.
    """

    MATCH_PRIORITY = 15  # beats the status-only HTTP 423 match on FileLockedException
    _HRESULTS = ("-2130575306",)
    _TYPE_NAMES = ("SPFileCheckOutException",)

    GUIDANCE = (
        "The file is checked out (reserved for editing) by another session. Unlike a shared "
        "coauthoring lock, a check-out can be released: the owner can call File.checkin(...) to "
        "keep the changes or File.undocheckout() to discard them (permissions permitting)."
    )

    def __str__(self) -> str:
        return self._render(self._base_description())


class SPListDataValidationException(SharePointException):
    """Raised when a list-level or field-level validation formula rejects a value.

    SharePoint reports both list validation and (field) value validation with
    this type: ``-2130575162`` for the list formula, ``-2130575163`` for the field.
    """

    MATCH_PRIORITY = 15
    _HRESULTS = ("-2130575162", "-2130575163")
    _TYPE_NAMES = ("SPListDataValidationException",)


class SPFieldValidationException(SharePointException):
    """Raised when a field value (or schema) is rejected — e.g. an unknown term."""

    MATCH_PRIORITY = 15
    _HRESULTS = ("-2146232832",)
    _TYPE_NAMES = ("SPFieldValidationException",)


class SPFieldValueException(SharePointException):
    """Raised when a field value is malformed or otherwise invalid."""

    MATCH_PRIORITY = 15
    _TYPE_NAMES = ("SPFieldValueException",)


class SPDuplicateValuesFoundException(SharePointException):
    """Raised when a value already exists in a column that enforces unique values."""

    MATCH_PRIORITY = 15
    _HRESULTS = ("-2130575169",)
    _TYPE_NAMES = ("SPDuplicateValuesFoundException",)


class SPInvalidLookupValuesException(SharePointException):
    """Raised when a lookup value does not reference an existing item."""

    MATCH_PRIORITY = 15
    _TYPE_NAMES = ("SPInvalidLookupValuesException",)


class SPContentTypeReadOnlyException(SharePointException):
    """Raised when mutating a read-only content type."""

    MATCH_PRIORITY = 15
    _TYPE_NAMES = ("SPContentTypeReadOnlyException",)


class SPContentTypeSealedException(SharePointException):
    """Raised when mutating a sealed content type."""

    MATCH_PRIORITY = 15
    _TYPE_NAMES = ("SPContentTypeSealedException",)


_SP_EXCEPTION_TYPES = (
    SecurityValidationException,
    SPQueryThrottledException,
    SPFileCheckOutException,
    SPListDataValidationException,
    SPFieldValidationException,
    SPFieldValueException,
    SPDuplicateValuesFoundException,
    SPInvalidLookupValuesException,
    SPContentTypeReadOnlyException,
    SPContentTypeSealedException,
)


# Register the catch-all first so concrete types share its precedence baseline,
# then the concrete types (all higher priority).
def _register_exceptions() -> None:
    register_error_type(SharePointException)
    for exc_type in _SP_EXCEPTION_TYPES:
        register_error_type(exc_type)


_register_exceptions()
