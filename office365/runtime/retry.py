"""Generic retry with exponential backoff + jitter — reusable, first-class retry helper.

Follows the Microsoft Graph / SharePoint guidance: honor the server's
``Retry-After`` header when present, otherwise back off exponentially with
jitter (so a fleet of clients doesn't retry in lock-step).
"""

from __future__ import annotations

import asyncio
import random
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from functools import wraps
from math import ceil
from time import sleep
from typing import Any, Awaitable, Callable, Optional, Tuple, Type

from requests import exceptions as requests_exceptions
from typing_extensions import ParamSpec

from office365.runtime.client_request_exception import ClientRequestException

_P = ParamSpec("_P")

TRANSIENT_STATUS_CODES = frozenset({408, 429, 500, 502, 503, 504})

#: Transport-level (non-HTTP) failures that are worth retrying: a dropped
#: connection, a socket/read timeout or a connection closed mid-body. TLS
#: verification failures (``SSLError``) are excluded even though ``requests``
#: makes them subclasses of ``ConnectionError`` — they are permanent.
TRANSIENT_TRANSPORT_EXCEPTIONS: Tuple[Type[Exception], ...] = (
    requests_exceptions.ConnectionError,
    requests_exceptions.Timeout,
    requests_exceptions.ChunkedEncodingError,
)

#: Default set of exception types eligible for retry.
DEFAULT_RETRY_EXCEPTIONS: Tuple[Type[Exception], ...] = (
    ClientRequestException,
    requests_exceptions.RequestException,
)


def is_transient_error(ex: Exception) -> bool:
    """Whether an exception reflects a transient failure worth retrying.

    HTTP failures are transient only for :data:`TRANSIENT_STATUS_CODES`.
    Transport failures are transient only for :data:`TRANSIENT_TRANSPORT_EXCEPTIONS`
    (so a malformed URL or a TLS error is not retried). Any other non-HTTP error
    is treated as transient, preserving the historical behaviour for custom
    exceptions.
    """
    status_code = getattr(getattr(ex, "response", None), "status_code", None)
    if status_code is not None:
        return status_code in TRANSIENT_STATUS_CODES
    # A library HTTP error without a response has an unknown cause; keep the
    # historical "non-HTTP is transient" behaviour for it.
    if isinstance(ex, ClientRequestException):
        return True
    if isinstance(ex, requests_exceptions.RequestException):
        if isinstance(ex, requests_exceptions.SSLError):
            return False
        return isinstance(ex, TRANSIENT_TRANSPORT_EXCEPTIONS)
    return True


def should_reset_connections(ex: Exception) -> bool:
    """Whether a failed attempt should discard its pooled connection before retrying.

    Microsoft Graph best practices ask clients to back off a ``503`` **and use a
    new connection**, so a poisoned keep-alive socket is not reused. True for
    ``502``/``503``/``504`` responses and for connection/timeout failures.
    """
    status_code = getattr(getattr(ex, "response", None), "status_code", None)
    if status_code is not None:
        return status_code in {502, 503, 504}
    if isinstance(ex, requests_exceptions.SSLError):
        return False
    return isinstance(ex, TRANSIENT_TRANSPORT_EXCEPTIONS)


def retry_after_delay(ex: Exception) -> Optional[int]:
    """Return the server-requested retry delay for a transient error.

    Reads the ``Retry-After`` header of any :data:`TRANSIENT_STATUS_CODES`
    response (408/429/5xx, including ``504``); returns ``None`` when it is
    unavailable or malformed so callers fall back to the backoff.

    Args:
        ex: The exception that was raised
    """
    response = getattr(ex, "response", None)
    if response is None or getattr(response, "status_code", None) not in TRANSIENT_STATUS_CODES:
        return None
    return response_retry_after(response)


def response_retry_after(response: Any) -> Optional[int]:
    """Parse the ``Retry-After`` header from a response, if any.

    Supports both forms allowed by RFC 7231: a non-negative number of seconds
    (``Retry-After: 10``) and an HTTP-date (``Retry-After: Wed, 21 Oct 2015
    07:28:00 GMT``), which is converted to a positive delay relative to now.
    Returns ``None`` when the header is absent or malformed.

    Args:
        response: A ``requests.Response`` (or object exposing ``.headers``)
    """
    if response is None:
        return None
    value = response.headers.get("Retry-After", None)
    if value is None:
        return None
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        pass
    try:
        parsed = parsedate_to_datetime(str(value))
    except (TypeError, ValueError):
        return None
    if parsed is None:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    delay = (parsed - datetime.now(timezone.utc)).total_seconds()
    return max(0, ceil(delay))


def retry_after_policy(_attempt: int, ex: Exception) -> Optional[int]:
    """The default ``on_failure`` policy: wait for what the server asked of you.

    Signature-compatible with ``on_failure``/``failure_callback`` so a caller can
    pass it as-is; it exists because :func:`retry_after_delay` reads one argument
    and the retry loops promise two.
    """
    return retry_after_delay(ex)


def backoff_delay(attempt: int, base: int, max_delay: Optional[int] = None, jitter: bool = True) -> float:
    """Compute the delay before retry ``attempt``.

    Exponential: ``base * 2 ** (attempt - 1)``, capped at ``max_delay``. With
    ``jitter`` enabled (default) the delay is randomized in ``[0, delay]`` per
    the "full jitter" strategy, avoiding synchronized retry storms.

    Args:
        attempt: 1-based retry attempt number.
        base: Base delay in seconds (``timeout_secs``).
        max_delay: Optional upper bound in seconds for the exponential growth.
        jitter: Whether to randomize the delay (default True).

    Returns:
        Seconds to sleep before this attempt.
    """
    delay = base * (2 ** (attempt - 1))
    if max_delay is not None:
        delay = min(delay, max_delay)
    if jitter:
        delay = random.uniform(0, delay)
    return delay


def delay_before_attempt(
    attempt: int,
    retry_after: Optional[int],
    timeout_secs: int,
    max_delay: Optional[int],
    jitter: bool,
) -> float:
    """Seconds to wait before retry ``attempt``: the server's request, else the backoff.

    ``max_delay`` bounds whichever is chosen, so a caller that caps its retries
    also caps the wait a server is allowed to ask for — a ``Retry-After`` of an
    hour is honored by a caller who asked for it and bounded by one who asked
    for a ceiling.
    """
    delay = retry_after if retry_after is not None else backoff_delay(attempt, timeout_secs, max_delay, jitter)
    if max_delay is not None:
        delay = min(delay, max_delay)
    return delay


def _run_with_retry(
    func: Callable[[], Any],
    *,
    max_retry: int,
    timeout_secs: int,
    max_delay: Optional[int],
    jitter: bool,
    exceptions: Tuple[Type[Exception], ...],
    is_retriable: Callable[[Exception], bool],
    on_failure: Optional[Callable[[int, Exception], Optional[int]]],
    on_success: Optional[Callable[[Any], None]],
) -> Any:
    last_ex: Exception | None = None
    for attempt in range(1, max_retry + 1):
        try:
            result = func()
            if callable(on_success):
                on_success(result)
            return result
        except exceptions as e:
            if not callable(is_retriable) or not is_retriable(e):
                raise
            last_ex = e
            retry_after = on_failure(attempt, e) if callable(on_failure) else retry_after_policy(attempt, e)
            delay = delay_before_attempt(attempt, retry_after, timeout_secs, max_delay, jitter)
            sleep(delay)
    assert last_ex is not None
    raise last_ex


def retry(
    func: Optional[Callable[[], Any]] = None,
    max_retry: int = 5,
    timeout_secs: int = 5,
    max_delay: Optional[int] = None,
    jitter: bool = True,
    exceptions: Tuple[Type[Exception], ...] = DEFAULT_RETRY_EXCEPTIONS,
    is_retriable: Callable[[Exception], bool] = is_transient_error,
    on_failure: Optional[Callable[[int, Exception], Optional[int]]] = None,
    on_success: Optional[Callable[[Any], None]] = None,
) -> Any:
    """Run ``func`` with retries — or, called without ``func``, return a decorator.

    Permanent failures re-raise immediately; the last exception is re-raised
    once retries are exhausted. The delay between attempts is the one the server
    named (``Retry-After``, via :func:`retry_after_policy`) and falls back to
    exponential backoff with jitter (:func:`backoff_delay`) when it named none;
    ``on_failure`` replaces that policy, and ``max_delay`` bounds whichever delay
    results.

    Two forms::

        retry(do_request, max_retry=3)  # run now (existing behaviour)


        @retry(max_retry=3)  # decorate a callable
        def do_request(): ...

    Args:
        func: Callable to execute. Omit to get a decorator.
        max_retry: Maximum number of retry attempts
        timeout_secs: Base delay for exponential backoff (seconds)
        max_delay: Optional cap for any delay, the server's included (seconds)
        jitter: Whether to randomize the backoff delay (default True)
        exceptions: Exception types that are candidates for retry
        is_retriable: Classifier deciding whether a caught exception is retried
        on_failure: Called after each failed attempt with ``(attempt, ex)``;
            may return a retry delay (seconds) to override the policy. Defaults
            to :func:`retry_after_policy` — the server's ``Retry-After``
        on_success: Called with ``func()`` result on success
    """
    options = {
        "max_retry": max_retry,
        "timeout_secs": timeout_secs,
        "max_delay": max_delay,
        "jitter": jitter,
        "exceptions": exceptions,
        "is_retriable": is_retriable,
        "on_failure": on_failure,
        "on_success": on_success,
    }
    if func is None:

        def decorator(fn: Callable[_P, Any]) -> Callable[_P, Any]:
            @wraps(fn)
            def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> Any:
                return _run_with_retry(lambda: fn(*args, **kwargs), **options)  # type: ignore[arg-type]

            return wrapper

        return decorator
    return _run_with_retry(func, **options)  # type: ignore[arg-type]


async def retry_async(
    func: Callable[[], Awaitable[Any]],
    *,
    max_retry: int = 5,
    timeout_secs: int = 5,
    max_delay: Optional[int] = None,
    jitter: bool = True,
    exceptions: Tuple[Type[Exception], ...] = DEFAULT_RETRY_EXCEPTIONS,
    is_retriable: Callable[[Exception], bool] = is_transient_error,
    on_failure: Optional[Callable[[int, Exception], Optional[int]]] = None,
    on_success: Optional[Callable[[Any], None]] = None,
) -> Any:
    """Run an awaitable ``func`` with retries, without blocking the event loop.

    Async counterpart of :func:`retry`: identical retry/backoff semantics
    (transient-only by default, the server's ``Retry-After`` ahead of exponential
    backoff with jitter), but the wait between attempts uses ``asyncio.sleep`` so
    concurrently-running tasks keep making progress.

    Args:
        func: Awaitable callable to execute.
        max_retry: Maximum number of retry attempts
        timeout_secs: Base delay for exponential backoff (seconds)
        max_delay: Optional cap for any delay, the server's included (seconds)
        jitter: Whether to randomize the backoff delay (default True)
        exceptions: Exception types that are candidates for retry
        is_retriable: Classifier deciding whether a caught exception is retried
        on_failure: Called after each failed attempt with ``(attempt, ex)``;
            may return a retry delay (seconds) to override the policy. Defaults
            to :func:`retry_after_policy` — the server's ``Retry-After``
        on_success: Called with ``await func()`` result on success
    """
    last_ex: Exception | None = None
    for attempt in range(1, max_retry + 1):
        try:
            result = await func()
            if callable(on_success):
                on_success(result)
            return result
        except exceptions as e:
            if not callable(is_retriable) or not is_retriable(e):
                raise
            last_ex = e
            retry_after = on_failure(attempt, e) if callable(on_failure) else retry_after_policy(attempt, e)
            delay = delay_before_attempt(attempt, retry_after, timeout_secs, max_delay, jitter)
            await asyncio.sleep(delay)
    assert last_ex is not None
    raise last_ex


def retry_on(*exception_types: Type[Exception]) -> Callable[[Exception], bool]:
    """Return a predicate that retries only the given exception types.

    By default only transient failures are retried (HTTP 408/429/500/502/503/504
    or non-HTTP errors). Use this as ``is_retriable`` to opt into retrying
    failures the runtime does not consider transient - for example a file that
    is locked while a user has it open (HTTP 423)::

        from office365.runtime.exceptions import FileLockedException
        from office365.runtime.retry import retry_on

        folder.upload_file(name, content).execute_query_retry(is_retriable=retry_on(FileLockedException))

    Args:
        exception_types: Exception classes that should be retried.
    """
    return lambda ex: isinstance(ex, exception_types)
