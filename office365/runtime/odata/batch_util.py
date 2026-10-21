"""Batch request sizing utilities.

Proactive chunking: batches are split by sub-request **count** and by estimated
**payload bytes** so a batch never exceeds a service request-size limit.
Reactive fallback: a whole-batch transport rejection (nothing was applied) is
signalled with :class:`WholeBatchRejected`, which callers halve and retry.

Error model: by default a permanently failed sub-response aborts the batch. A
caller that wants best-effort semantics opens
:meth:`ClientRuntimeContext.collect_batch_failures` instead, and each failed
sub-request is recorded against its own query rather than raised.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Optional, Sequence

from office365.runtime.client_request_exception import ClientRequestException

if TYPE_CHECKING:
    from office365.runtime.client_runtime_context import ClientRuntimeContext
    from office365.runtime.odata.json_format import JsonProfile
    from office365.runtime.queries.client_query import ClientQuery

# Batch-level HTTP statuses that indicate the whole request was rejected before
# any sub-request ran (e.g. the body exceeds a request-size limit).
WHOLE_BATCH_REJECT_CODES = frozenset({400, 413, 414, 431})

_BATCH_OVERHEAD = 1024  # multipart/JSON envelope allowance per batch
_PART_OVERHEAD = 256  # per-sub-request header/boundary allowance


def estimate_query_bytes(query: "ClientQuery", json_format: Optional["JsonProfile"] = None) -> int:
    """Estimate the wire size of a batched sub-request without building a request.

    Builds the URL from the query's resource path and serializes its payload
    locally — no transport/auth side effects — through the same profile the
    request itself uses, so the estimate is of the body that will be sent
    rather than of a payload nothing will ask for.

    Args:
        query: The sub-query to measure
        json_format: The profile the batch request carries; ``None`` measures
            the payload with no dialect-specific spelling.
    """
    url = getattr(query, "url", "") or ""
    size = len(str(url).encode("utf-8"))

    payload = getattr(query, "parameters_type", None)
    if payload is not None:
        if isinstance(payload, (bytes, bytearray)):
            size += len(bytes(payload))
        elif isinstance(payload, str):
            size += len(payload.encode("utf-8"))
        else:
            try:
                if json_format is None:
                    body = json.dumps(payload, separators=(",", ":"), default=str)
                else:
                    body = json.dumps(json_format.build_payload(payload), separators=(",", ":"), default=str)
            except Exception:
                body = str(payload)
            size += len(body.encode("utf-8"))

    headers = getattr(query, "custom_headers", None) or {}
    for k, v in headers.items():
        size += len(str(k)) + len(str(v))
    return size + _PART_OVERHEAD


def partition_by_limits(
    queries: Sequence,
    max_items: Optional[int],
    max_bytes: Optional[int],
    json_format: Optional["JsonProfile"] = None,
) -> list[list]:
    """Split queries into batches respecting item and byte caps (order preserved).

    A single oversized query still becomes its own one-item batch, so a request
    rejected purely because of size is sent alone.

    Args:
        queries: The sub-queries to split, in submission order
        max_items: Maximum queries per batch
        max_bytes: Maximum estimated payload size per batch
        json_format: The profile the batch request carries, for the byte estimate
    """
    batches: list[list] = []
    current: list = []
    current_bytes = _BATCH_OVERHEAD
    for query in queries:
        if max_items is not None and len(current) >= max_items:
            batches.append(current)
            current, current_bytes = [], _BATCH_OVERHEAD
        item_bytes = estimate_query_bytes(query, json_format)
        if max_bytes is not None and current and current_bytes + item_bytes > max_bytes:
            batches.append(current)
            current, current_bytes = [], _BATCH_OVERHEAD
        current.append(query)
        current_bytes += item_bytes
    if current:
        batches.append(current)
    return batches


def record_batch_failure(context: ClientRuntimeContext, query: ClientQuery, exc: ClientRequestException) -> bool:
    """Record one failed sub-request when a tolerant batch scope is active.

    The sink lives on the context (see ``collect_batch_failures``), not on the
    batch query: batches are partitioned, retried and split into new
    ``BatchQuery`` objects, so a per-query sink would lose failures along the way.

    Args:
        context: The runtime context that owns the batch.
        query: The sub-query that failed (the caller's handle on the item).
        exc: The error to record.

    Returns:
        ``True`` when the failure was recorded; ``False`` when no tolerant scope
        is active, so the caller must re-raise (the default behaviour).
    """
    sink = getattr(context, "_batch_failures", None)
    if sink is None:
        return False
    sink.append((query, exc))
    return True


class WholeBatchRejected(ClientRequestException):
    """Internal marker: the whole batch HTTP request was rejected.

    Raised only for a transport-level rejection (before any sub-request was
    applied); callers may safely halve the batch and retry.
    """

    def __init__(self, queries: list, cause: ClientRequestException) -> None:
        super().__init__(str(cause))
        self.queries = list(queries)
        self.__cause__ = cause
        self.response = getattr(cause, "response", None)
