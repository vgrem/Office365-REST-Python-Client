from __future__ import annotations

import copy
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, Generic, Optional, TypeVar

from typing_extensions import Self

from office365.runtime.client_value import ClientValue
from office365.runtime.converters.value import deserialize_value
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.retry import DEFAULT_RETRY_EXCEPTIONS

if TYPE_CHECKING:
    from office365.runtime.client_runtime_context import ClientRuntimeContext

ClientValueT = TypeVar("ClientValueT", bound=object)


class ClientResult(Generic[ClientValueT]):
    """Client result"""

    _value: Optional[ClientValueT]

    def __init__(
        self,
        context: ClientRuntimeContext,
        default_value: Optional[ClientValueT] = None,
    ) -> None:
        """Client result"""
        self._context = context
        self._value = copy.deepcopy(default_value)

    def before_execute(self, action: Callable[[RequestOptions], None]) -> Self:
        """Attach an event handler which is triggered before query is submitted to server"""
        self._context.before_execute(action)
        return self

    def after_execute(
        self,
        action: Callable[[Any], None],
        execute_first: bool = False,
        include_response: bool = False,
    ) -> Self:
        """Attach an event handler which is triggered after query is submitted to server"""
        self._context.after_execute(action, execute_first, include_response)
        return self

    def set_property(self, key: str, value: Any, persist_changes: bool = False) -> Self:
        if key == "__value":
            # A raw/scalar payload (non-JSON responses, e.g. report CSVs) carries
            # the result's value. A model that represents raw content (``Report``)
            # receives it through its ``content`` field, keeping the declared type.
            current = self._value
            if isinstance(current, ClientValue) and hasattr(current, "content"):
                current.set_property("content", value)
                return self
            # A declared ``datetime`` / ``Enum`` value is coerced by the branch
            # below, so only assign raw values that have no declared type.
            if not isinstance(current, (datetime, Enum)):
                self._value = value
                return self
        current = self._value
        if isinstance(current, ClientValue):
            current.set_property(key, value, persist_changes)
        elif isinstance(current, dict):
            current[key] = value
        elif isinstance(current, (datetime, Enum)):
            coerced = deserialize_value(None, value, current, persist_changes)
            if coerced is not None:
                self._value = coerced
        else:
            self._value = value
        return self

    @property
    def value(self) -> ClientValueT:
        """Returns the value (populated after execution)."""
        assert self._value is not None
        return self._value

    def __str__(self) -> str:
        """Return the wrapped value's natural string form."""
        if self._value is None:
            return "ClientResult(<empty>)"
        return str(self._value)

    def __repr__(self) -> str:
        """Return ``ClientResult(<value>)`` without triggering a request."""
        if self._value is None:
            return "ClientResult(<empty>)"
        return f"ClientResult({self._value!r})"

    def to_bytes(self) -> bytes:
        """Returns the response payload as bytes.

        Normalizes the shapes binary endpoints return — raw ``bytes`` /
        ``bytearray``, a ``str``, or an object exposing a ``content`` attribute
        (e.g. :class:`~office365.reports.report.Report`). Anything else yields
        ``b""``.
        """
        value: Any = self._value
        if isinstance(value, (bytes, bytearray)):
            return bytes(value)
        if isinstance(value, str):
            return value.encode("utf-8")
        content = getattr(value, "content", None)
        if isinstance(content, (bytes, bytearray)):
            return bytes(content)
        if isinstance(content, str):
            return content.encode("utf-8")
        return b""

    def execute_query(self) -> ClientResult[ClientValueT]:
        """Submit request(s) to the server"""
        self._context.execute_query()
        return self

    async def execute_query_async(self) -> ClientResult[ClientValueT]:
        """Submit request(s) to the server without blocking the loop"""
        await self._context.execute_query_async()
        return self

    def execute_query_retry(
        self,
        max_retry: int = 5,
        timeout_secs: int = 5,
        max_delay: Optional[int] = None,
        jitter: bool = True,
        success_callback: Optional[Callable[[Any], None]] = None,
        failure_callback: Optional[Callable[[int, Exception], None]] = None,
        exceptions: tuple[type[Exception], ...] = DEFAULT_RETRY_EXCEPTIONS,
        is_retriable: Optional[Callable[[Exception], bool]] = None,
    ) -> ClientResult[ClientValueT]:
        """
        Executes the current set of data retrieval queries and method invocations and retries it if needed.


         Args:
            max_retry: Maximum retry attempts
            timeout_secs: Base delay for exponential backoff (seconds)
            max_delay: Optional cap on the exponential delay (seconds)
            jitter: Whether to randomize the delay
            success_callback: Called on successful execution
            failure_callback: Called after failed retries
            exceptions: Exception types that trigger retries
            is_retriable: Optional predicate deciding whether a caught exception
                is retried (defaults to transient-only)

         Returns:
            Self for method chaining

        """
        self._context.execute_query_retry(
            max_retry=max_retry,
            timeout_secs=timeout_secs,
            max_delay=max_delay,
            jitter=jitter,
            success_callback=success_callback,
            failure_callback=failure_callback,
            exceptions=exceptions,
            is_retriable=is_retriable,
        )
        return self

    async def execute_query_async_retry(
        self,
        max_retry: int = 5,
        timeout_secs: int = 5,
        max_delay: Optional[int] = None,
        jitter: bool = True,
        success_callback: Optional[Callable[[Any], None]] = None,
        failure_callback: Optional[Callable[[int, Exception], None]] = None,
        exceptions: tuple[type[Exception], ...] = DEFAULT_RETRY_EXCEPTIONS,
        is_retriable: Optional[Callable[[Exception], bool]] = None,
    ) -> ClientResult[ClientValueT]:
        """Async counterpart of :meth:`execute_query_retry`."""
        await self._context.execute_query_async_retry(
            max_retry=max_retry,
            timeout_secs=timeout_secs,
            max_delay=max_delay,
            jitter=jitter,
            success_callback=success_callback,
            failure_callback=failure_callback,
            exceptions=exceptions,
            is_retriable=is_retriable,
        )
        return self
