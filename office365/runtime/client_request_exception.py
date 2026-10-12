from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Optional

from requests import RequestException, Response

from office365.runtime.converters.scalars import parse_int

_HEADER_REQUEST_IDS = ("request-id", "client-request-id", "SPRequestGuid")
_OPERATION_ID_MARKER = " - Operation ID (for customer support):"


def _clean_message(text: str) -> str:
    """Normalise a Graph/Intune error message into a readable one-liner.

    The Intune proxy returns ``error.message`` as a JSON object string
    (``{"_version": 3, "Message": "Application is not authorized ..."}``)
    and appends support diagnostics (`` - Operation ID ... - Activity ID ...``).
    This unwraps the inner ``Message`` and drops the diagnostics, without
    changing plain-text messages from other services.
    """
    message = text
    stripped = message.strip()
    if stripped.startswith("{"):
        try:
            payload = json.loads(stripped)
        except ValueError:
            payload = None
        if isinstance(payload, dict):
            inner = payload.get("Message") or payload.get("message")
            if isinstance(inner, str):
                message = inner
    head, marker, _ = message.partition(_OPERATION_ID_MARKER)
    return head if marker else message


@dataclass(frozen=True)
class ErrorPayload:
    """Normalized view of an OData error response, parsed once for classification."""

    code: str = ""
    message: str = ""
    details: tuple[dict, ...] = ()
    status: Optional[int] = None

    @property
    def hresult(self) -> Optional[str]:
        """The leading HRESULT of a SharePoint ``code`` (e.g. ``-2147018894``).

        SharePoint encodes the error as ``"<hresult>, <dotnet-type>"`` (locale
        independent), while Graph uses symbolic codes; returns ``None`` when the
        code has no numeric prefix.
        """
        token = self.code.split(",", 1)[0].strip()
        return token if token.lstrip("-").isdigit() else None

    @property
    def error_type(self) -> Optional[str]:
        """The .NET type name embedded in a SharePoint ``code`` after the comma.

        For ``"-2147018894, Microsoft.SharePoint.SPFileLockException"`` this is
        ``"Microsoft.SharePoint.SPFileLockException"`` — a locale-independent,
        self-describing discriminator that avoids matching on translated messages.
        """
        if "," not in self.code:
            return None
        type_name = self.code.split(",", 1)[1].strip()
        return type_name or None


def _parse_error(response: Response) -> dict:
    try:
        error = response.json().get("error", {})
    except Exception:
        return {}
    return error if isinstance(error, dict) else {}


def _to_payload(error: dict, response: Response) -> ErrorPayload:
    msg = error.get("message")
    message = str(msg.get("value", "")) if isinstance(msg, dict) else str(msg or "")
    message = _clean_message(message)
    details = error.get("details")
    return ErrorPayload(
        code=str(error.get("code") or ""),
        message=message,
        details=tuple(d for d in details if isinstance(d, dict)) if isinstance(details, list) else (),
        status=getattr(response, "status_code", None),
    )


class ClientRequestException(RequestException):
    """Custom exception for client requests with enhanced error handling.

    In addition to ``code`` / ``message`` it surfaces correlation and server
    diagnostics when the error response provides them (Graph ``innerError``,
    ``request-id``; SharePoint ``SPRequestGuid`` / ``SPRequestDuration`` /
    ``X-SharePointHealthScore``).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._error: dict = {}
        self._hints: list[str] = []

    #: Optional class-level remediation appended to ``str(exc)`` by
    #: :meth:`_render` (e.g. the generic advice on
    #: :class:`~office365.runtime.exceptions.AccessDeniedException`).
    GUIDANCE: str = ""

    #: Specificity of this type when several match a payload; the highest wins
    #: (ties broken by registration order). Lets catch-alls coexist with the
    #: concrete types without depending on import order.
    MATCH_PRIORITY: int = 0

    @classmethod
    def matches(cls, payload: ErrorPayload) -> bool:
        """Whether this exception type describes the given error payload."""
        return False

    @classmethod
    def from_response(cls, response: Response) -> ClientRequestException:
        """Factory: parse error response, dispatch to the right exception type.

        Inspects the error payload once and returns the most specific matching
        subclass (e.g. ``DuplicatedObjectException``), so callers never deal with
        HTTP status codes or error JSON. ``MATCH_PRIORITY`` decides between
        overlapping types and registration order breaks ties.
        """
        from office365.runtime import exceptions  # noqa: F401 — registers the built-in error types

        error = _parse_error(response)
        payload = _to_payload(error, response)
        matches = [
            (getattr(exc_type, "MATCH_PRIORITY", 0), -index, exc_type)
            for index, exc_type in enumerate(_ERROR_TYPES)
            if exc_type.matches(payload)
        ]
        exc: ClientRequestException = (
            max(matches, key=lambda item: item[:2])[2](response=response) if matches else cls(response=response)
        )

        exc._error = error
        if error:
            exc.args = (exc.code or "", exc.message or "")
        else:
            http_error_msg = f"{response.status_code} {response.reason} for url: {response.url}"
            exc.args = (str(response.status_code), http_error_msg)
        return exc

    @property
    def code(self) -> Optional[str]:
        return self._error.get("code")

    @property
    def hresult(self) -> Optional[str]:
        """The leading HRESULT of a SharePoint ``code`` (``None`` for Graph codes)."""
        code = self.code
        if not code:
            return None
        token = code.split(",", 1)[0].strip()
        return token if token.lstrip("-").isdigit() else None

    @property
    def error_type(self) -> Optional[str]:
        """The .NET type name embedded in a SharePoint ``code`` (after the comma)."""
        code = self.code
        if not code or "," not in code:
            return None
        type_name = code.split(",", 1)[1].strip()
        return type_name or None

    @property
    def message(self) -> str:
        msg = self._error.get("message")
        if isinstance(msg, dict):
            return _clean_message(str(msg.get("value", "")))
        return _clean_message(str(msg or ""))

    @property
    def message_lang(self) -> Optional[str]:
        msg = self._error.get("message")
        return msg.get("lang") if isinstance(msg, dict) else None

    @property
    def inner_error(self) -> Optional[dict]:
        """The Graph ``innerError`` payload (``request-id``, ``date``, ...), if any."""
        inner = self._error.get("innerError")
        return inner if isinstance(inner, dict) else None

    @property
    def request_id(self) -> Optional[str]:
        """Correlation ID for the failed request, if reported.

        Prefers Graph/SharePoint response headers (``request-id``,
        ``client-request-id``, ``SPRequestGuid``), then the Graph
        ``innerError.request-id``.
        """
        headers = getattr(self.response, "headers", None) or {}
        for name in _HEADER_REQUEST_IDS:
            value = headers.get(name)
            if value:
                return value
        inner = self.inner_error or {}
        return inner.get("request-id")

    @property
    def server_guid(self) -> Optional[str]:
        """SharePoint server request GUID (``SPRequestGuid`` header)."""
        return (getattr(self.response, "headers", None) or {}).get("SPRequestGuid")

    @property
    def duration_ms(self) -> Optional[int]:
        """SharePoint server-side processing time (``SPRequestDuration``), ms."""
        return parse_int((getattr(self.response, "headers", None) or {}).get("SPRequestDuration"))

    @property
    def health_score(self) -> Optional[int]:
        """SharePoint server health score (``X-SharePointHealthScore``)."""
        return parse_int((getattr(self.response, "headers", None) or {}).get("X-SharePointHealthScore"))

    def add_hint(self, hint: str) -> "ClientRequestException":
        """Append a remediation hint that ``str(exc)`` will display (chainable).

        Used by the runtime to explain a denied request with the permissions the
        called API declares (via ``@require_permission``). Callers may add their
        own hints to ``except`` blocks without re-wrapping the exception.
        """
        if hint:
            self._hints.append(hint)
        return self

    @property
    def hints(self) -> tuple[str, ...]:
        """Remediation hints attached to this error (class ``GUIDANCE`` excluded)."""
        return tuple(self._hints)

    def _base_description(self) -> str:
        """The underlying ``RequestException`` description (no guidance/hints)."""
        return super().__str__()

    def _render(self, described: str) -> str:
        """Compose the description with class ``GUIDANCE`` and any hints."""
        parts = [described] if described else []
        parts.extend(extra for extra in ([self.GUIDANCE] if self.GUIDANCE else []) + self._hints if extra)
        return "\n".join(parts)

    def __str__(self) -> str:
        return self._render(self._base_description())


# Error types consulted by ``from_response``. The generic runtime types live in
# ``office365.runtime.exceptions`` and product packages (e.g.
# ``office365.sharepoint.exceptions``) register their own; both call
# ``register_error_type`` so the dispatcher stays product-agnostic. Specificity is
# decided by ``MATCH_PRIORITY`` (registration order breaks ties), not import order.
_ERROR_TYPES: list[type[ClientRequestException]] = []


def register_error_type(exc_type: type[ClientRequestException]) -> None:
    """Register an error type for ``from_response`` dispatch.

    Modules call this at import time; the dispatcher picks the highest
    ``MATCH_PRIORITY`` match, breaking ties by registration order (earlier wins).
    """
    if exc_type not in _ERROR_TYPES:
        _ERROR_TYPES.append(exc_type)


_LAZY_EXPORTS = ("DuplicatedObjectException", "ObjectNotFoundException")


def __getattr__(name: str):
    """Backward-compatible re-export of the generic error types (now in ``exceptions``)."""
    if name in _LAZY_EXPORTS:
        from office365.runtime import exceptions

        return getattr(exceptions, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
