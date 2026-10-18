from __future__ import annotations

import json
import re
from email import message_from_bytes
from email.message import Message
from typing import TYPE_CHECKING, Iterator, List, Optional, Tuple

import requests
from requests import Response
from requests.exceptions import HTTPError
from requests.structures import CaseInsensitiveDict

from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.odata.batch_util import WHOLE_BATCH_REJECT_CODES, WholeBatchRejected, record_batch_failure
from office365.runtime.odata.request import ODataRequest
from office365.runtime.queries.batch import BatchQuery, create_boundary
from office365.runtime.queries.client_query import ClientQuery

if TYPE_CHECKING:
    from office365.runtime.client_runtime_context import ClientRuntimeContext


DEFAULT_MAX_BATCH_BYTES = 1024 * 1024  # SharePoint Online conservative request-size cap


class ODataBatchV3Request(ODataRequest):
    """Handles OData v3.0 batch requests and responses.

    This class implements the OData v3.0 batch protocol for sending multiple
    operations in a single HTTP request and processing the multipart response.
    """

    def build_request(self, query: BatchQuery) -> RequestOptions:  # type: ignore[reportIncompatibleMethodOverride]
        """Construct an OData v3 batch request.

        Args:
            query: The batch query containing all operations

        Returns:
            Configured RequestOptions with multipart/mixed content
        """
        request = RequestOptions(url=query.url)
        request.method = HttpMethod.Post
        media_type = "multipart/mixed"
        content_type = "; ".join([media_type, f"boundary={query.current_boundary}"])
        request.ensure_header("Content-Type", content_type)
        request.data = self._prepare_payload(query)
        return request

    def process_response(self, response: Response, query: BatchQuery) -> None:  # type: ignore[reportIncompatibleMethodOverride]
        """Process a batch response by handling each sub-response.

        Args:
            response: The raw batch response
            query: The original batch query
        """
        for sub_qry, sub_resp in self._extract_response(response, query):
            self._observe_throttle(sub_resp)
            try:
                sub_resp.raise_for_status()
            except HTTPError:
                # Same tolerant-scope rule as the retry path; the non-tolerant
                # path still raises the original ``HTTPError``.
                if record_batch_failure(query.context, sub_qry, ClientRequestException.from_response(sub_resp)):
                    continue
                raise
            self._apply_sub_response(sub_qry, sub_resp, query.context)

    def _apply_sub_response(self, sub_qry: ClientQuery, sub_resp: Response, context: "ClientRuntimeContext") -> None:
        """Map one sub-response, then fire the sub-query's pending handlers.

        Batch execution bypasses the ``_get_next_query`` cursor, so a sub-query's
        ``after_execute`` handlers (registered on ``context.pending_request()``
        and keyed on ``context.current_query``) would otherwise never run. Expose
        the sub-query and run them exactly as the non-batch path does, so
        callback-driven follow-up queries are queued for the next round.
        """
        with context.current_query_scope(sub_qry):
            super().process_response(sub_resp, sub_qry)
            context.pending_request().afterExecute(sub_resp)

    def execute_query_with_retry(
        self,
        query: BatchQuery,
        max_retry: int = 5,
        base_delay: int = 5,
        jitter: bool = True,
    ) -> None:
        """Execute a batch, retrying only the transiently-failed sub-requests.

        A throttled sub-request (HTTP 429/503) is retried on its own after the
        longest ``Retry-After`` (or exponential backoff) — already-succeeded
        sub-requests are not re-applied, so a partial batch failure doesn't
        duplicate writes. Routes the retry loop through the shared
        :func:`~office365.runtime.retry.retry` primitive.

        Args:
            query: The batch query to execute
            max_retry: Maximum number of retry attempts per sub-request
            base_delay: Base delay for exponential backoff (seconds)
            jitter: Whether to randomize the delay (default True)
        """
        from office365.runtime.retry import retry, retry_after_delay, should_reset_connections

        state: dict = {"pending": query, "retry_after": None}

        def _on_failure(_attempt_num: int, ex: Exception) -> Optional[int]:
            if should_reset_connections(ex):
                self.transport.reset_connections()
            return state["retry_after"] or retry_after_delay(ex)

        def _attempt() -> None:
            try:
                response = self.execute_request_direct(self.build_request(state["pending"]))
            except ClientRequestException as exc:
                status = getattr(getattr(exc, "response", None), "status_code", None)
                if status in WHOLE_BATCH_REJECT_CODES:
                    # Whole-batch transport rejection (nothing was applied) —
                    # signal callers to split, not mask per-item errors.
                    raise WholeBatchRejected(state["pending"].queries, exc) from exc
                raise
            failures, retry_after = self._collect_failures(response, state["pending"])
            if not failures:
                self.afterExecute(response)
                return
            state["retry_after"] = retry_after or None
            state["pending"] = self._retry_pending(query, failures)
            raise ClientRequestException.from_response(failures[0][1])

        try:
            retry(
                _attempt,
                max_retry=max_retry,
                timeout_secs=base_delay,
                jitter=jitter,
                on_failure=_on_failure,
            )
        except WholeBatchRejected as reject:
            self._split_and_retry(query, reject, max_retry, base_delay, jitter)
        except ClientRequestException as exc:
            # Sub-requests still failing after every retry: a tolerant scope
            # records them, otherwise the first one propagates as before.
            if not self._record_failures(query, state["pending"].queries, exc):
                raise

    async def execute_query_with_retry_async(
        self,
        query: BatchQuery,
        max_retry: int = 5,
        base_delay: int = 5,
        jitter: bool = True,
    ) -> None:
        """Async twin of :meth:`execute_query_with_retry`.

        Sends the batch through :meth:`execute_request_direct_async` — so a
        native async transport is used when configured, otherwise the blocking
        call is offloaded to a worker thread — and retries only the transiently
        failed sub-requests, honoring ``Retry-After``. Whole-batch rejections are
        split and retried the same way as the sync path.
        """
        from office365.runtime.retry import retry_after_delay, retry_async, should_reset_connections

        state: dict = {"pending": query, "retry_after": None}

        def _on_failure(_attempt_num: int, ex: Exception) -> Optional[int]:
            if should_reset_connections(ex):
                self.async_transport.reset_connections()
            return state["retry_after"] or retry_after_delay(ex)

        async def _attempt() -> None:
            try:
                response = await self.execute_request_direct_async(self.build_request(state["pending"]))
            except ClientRequestException as exc:
                status = getattr(getattr(exc, "response", None), "status_code", None)
                if status in WHOLE_BATCH_REJECT_CODES:
                    raise WholeBatchRejected(state["pending"].queries, exc) from exc
                raise
            failures, retry_after = self._collect_failures(response, state["pending"])
            if not failures:
                self.afterExecute(response)
                return
            state["retry_after"] = retry_after or None
            state["pending"] = self._retry_pending(query, failures)
            raise ClientRequestException.from_response(failures[0][1])

        try:
            await retry_async(
                _attempt,
                max_retry=max_retry,
                timeout_secs=base_delay,
                jitter=jitter,
                on_failure=_on_failure,
            )
        except WholeBatchRejected as reject:
            await self._split_and_retry_async(query, reject, max_retry, base_delay, jitter)
        except ClientRequestException as exc:
            if not self._record_failures(query, state["pending"].queries, exc):
                raise

    def _collect_failures(
        self, response: Response, query: BatchQuery
    ) -> Tuple[List[Tuple[ClientQuery, Response]], Optional[int]]:
        """Process one batch response: apply successes, return transient failures.

        Sub-responses that are not transient are applied immediately (raising on
        a permanent failure); transient ones are returned so the caller can resend
        just those. Shared by the sync and async retry loops.
        """
        from office365.runtime.retry import TRANSIENT_STATUS_CODES, response_retry_after

        failures: List[Tuple[ClientQuery, Response]] = []
        retry_after: Optional[int] = None
        for sub_qry, sub_resp in self._extract_response(response, query):
            self._observe_throttle(sub_resp)
            if sub_resp.status_code in TRANSIENT_STATUS_CODES:
                failures.append((sub_qry, sub_resp))
                retry_after = max(retry_after or 0, response_retry_after(sub_resp) or 0)
            else:
                try:
                    self._raise_for_status(sub_resp)
                except ClientRequestException as exc:
                    # Tolerant scope: this sub-request is one item's failure, not
                    # the batch's — record it and keep applying the rest.
                    if record_batch_failure(query.context, sub_qry, exc):
                        continue
                    raise
                self._apply_sub_response(sub_qry, sub_resp, query.context)
        return failures, retry_after

    @staticmethod
    def _record_failures(query: BatchQuery, queries: List[ClientQuery], exc: ClientRequestException) -> bool:
        """Record one failure per still-failing sub-request when a tolerant scope is active.

        Returns ``False`` when it is not, so the caller re-raises the original error.
        """
        recorded = [record_batch_failure(query.context, sub_qry, exc) for sub_qry in queries]
        return bool(recorded) and all(recorded)

    def _retry_pending(self, query: BatchQuery, failures: List[Tuple[ClientQuery, Response]]) -> BatchQuery:
        """Rebuild the pending batch from the transiently-failed sub-requests."""
        return BatchQuery(query.context, [qry for qry, _ in failures])

    def _split_and_retry(
        self,
        query: BatchQuery,
        reject: WholeBatchRejected,
        max_retry: int,
        base_delay: int,
        jitter: bool,
    ) -> None:
        """Halve a whole-rejected batch and retry each half (down to a single request)."""
        queries = reject.queries
        if len(queries) <= 1:
            first = queries[0]
            req = first.build_request()
            message = f"{reject}; a batch of 1 was still rejected — request {req.method} {req.url}"
            if record_batch_failure(query.context, first, ClientRequestException(message, response=reject.response)):
                return
            raise ClientRequestException(message, response=reject.response) from reject
        mid = len(queries) // 2  # noqa: PLR2004
        for half in (queries[:mid], queries[mid:]):
            self.execute_query_with_retry(BatchQuery(query.context, half), max_retry, base_delay, jitter)

    async def _split_and_retry_async(
        self,
        query: BatchQuery,
        reject: WholeBatchRejected,
        max_retry: int,
        base_delay: int,
        jitter: bool,
    ) -> None:
        """Async twin of :meth:`_split_and_retry`."""
        queries = reject.queries
        if len(queries) <= 1:
            first = queries[0]
            req = first.build_request()
            message = f"{reject}; a batch of 1 was still rejected — request {req.method} {req.url}"
            if record_batch_failure(query.context, first, ClientRequestException(message, response=reject.response)):
                return
            raise ClientRequestException(message, response=reject.response) from reject
        mid = len(queries) // 2  # noqa: PLR2004
        for half in (queries[:mid], queries[mid:]):
            await self.execute_query_with_retry_async(BatchQuery(query.context, half), max_retry, base_delay, jitter)

    def _extract_response(self, response: Response, query: BatchQuery) -> Iterator[Tuple[ClientQuery, Response]]:
        """Extract individual responses from a multipart batch response.

        Args:
            response: The raw HTTP response
            query: The original batch query

        Yields:
            Tuples of (sub-query, sub-response) for each operation
        """
        content_type = response.headers["Content-Type"].encode("ascii")
        http_body = b"Content-Type: " + content_type + b"\r\n\r\n" + response.content

        message = message_from_bytes(http_body)

        query_id = 0
        for raw_response in message.get_payload():
            if isinstance(raw_response, Message) and raw_response.get_content_type() == "application/http":
                qry = query.ordered_queries[query_id]
                query_id += 1
                yield qry, self._deserialize_response(raw_response)

    def _prepare_payload(self, query: BatchQuery) -> bytes:
        """Prepare the multipart payload for a batch request.

        Args:
            query: The batch query containing operations

        Returns:
            The encoded multipart message body
        """
        main_message = Message()
        main_message.add_header("Content-Type", "multipart/mixed")
        main_message.set_boundary(query.current_boundary)

        if query.has_change_sets:
            change_set_message = Message()
            change_set_boundary = create_boundary("changeset_", True)
            change_set_message.add_header("Content-Type", "multipart/mixed")
            change_set_message.set_boundary(change_set_boundary)

            for qry in query.change_sets:
                with query.context.current_query_scope(qry):
                    request = qry.build_request()
                message = self._serialize_request(request)
                change_set_message.attach(message)
            main_message.attach(change_set_message)

        for qry in query.get_queries:
            with query.context.current_query_scope(qry):
                request = qry.build_request()
            message = self._serialize_request(request)
            main_message.attach(message)

        return main_message.as_bytes()

    @staticmethod
    def _normalize_headers(headers_raw: List[str]) -> CaseInsensitiveDict:
        """Normalize HTTP headers into a case-insensitive dictionary.

        Args:
            headers_raw: List of raw header strings

        Returns:
            Normalized headers dictionary
        """
        headers = {}
        for header_line in headers_raw:
            k, v = header_line.split(":", 1)
            headers[k.title()] = v.strip()
        return CaseInsensitiveDict(headers)

    def _deserialize_response(self, raw_response: Message) -> Response:
        """Deserialize a single sub-response from the batch.

        The body is sliced off the raw bytes at the header/body separator and kept
        as-is, so binary payloads (e.g. a ``$value`` file download) survive intact
        instead of being decoded line by line as text.

        Args:
            raw_response: The message part containing the HTTP response

        Returns:
            Constructed Response object
        """
        payload = raw_response.get_payload(decode=True)
        assert isinstance(payload, bytes)
        head, _, body = payload.partition(b"\r\n\r\n")
        lines = list(filter(None, head.decode("utf-8", "replace").split("\r\n")))
        response_status_regex = "^HTTP/1\\.\\d (\\d{3}) (.*)$"
        status_result = re.match(response_status_regex, lines[0])
        assert status_result is not None
        status_info = status_result.groups()

        resp = requests.Response()
        resp.status_code = int(status_info[0])
        resp.headers = self._normalize_headers(lines[1:])
        resp._content = body
        return resp

    @staticmethod
    def _serialize_request(request: RequestOptions) -> Message:
        """Serialize a single request for inclusion in the batch.

        Args:
            request: The request options to serialize

        Returns:
            Message object containing the serialized request
        """
        eol = "\r\n"
        method = request.method
        if "X-HTTP-Method" in request.headers:
            method = request.headers["X-HTTP-Method"]
        lines = [f"{method} {request.url} HTTP/1.1"] + [":".join(h) for h in request.headers.items()]
        if request.data:
            lines.append(eol)
            lines.append(json.dumps(request.data))
        raw_content = eol + eol.join(lines) + eol
        payload = raw_content.encode("utf-8").lstrip()

        message = Message()
        message.add_header("Content-Type", "application/http")
        message.add_header("Content-Transfer-Encoding", "binary")
        message.set_payload(payload)
        return message

    @property
    def service_root_url(self) -> str:
        """Gets the batch request URL."""
        return f"{self._base_url}/$batch"
