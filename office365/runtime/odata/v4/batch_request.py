from __future__ import annotations

import json
from typing import Any, Dict, Iterator, List, Optional, Tuple

from requests import Response
from requests.exceptions import HTTPError
from requests.structures import CaseInsensitiveDict

from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.odata.batch_util import WHOLE_BATCH_REJECT_CODES, WholeBatchRejected, record_batch_failure
from office365.runtime.odata.request import ODataRequest
from office365.runtime.queries.batch import BatchQuery
from office365.runtime.queries.client_query import ClientQuery

DEFAULT_MAX_BATCH_BYTES = 3 * 1024 * 1024  # Microsoft Graph JSON-batch limit is ~4 MB; conservative cap


class ODataV4BatchRequest(ODataRequest):
    """Handles JSON batch requests for OData v4 protocol.

    This class implements the OData batch processing specification for sending multiple
    OData operations in a single HTTP request and processing the batched responses.
    """

    def build_request(self, query: BatchQuery) -> RequestOptions:  # type: ignore[reportIncompatibleMethodOverride]
        """Constructs a batch request from multiple individual queries.

        Args:
            query: A BatchQuery containing multiple individual queries

        Returns:
            RequestOptions: Configured batch request with proper headers and payload
        """
        request = RequestOptions(query.url)
        request.method = HttpMethod.Post
        request.ensure_header("Content-Type", "application/json")
        request.ensure_header("Accept", "application/json")
        request.data = self._prepare_payload(query)
        return request

    def process_response(self, response: Response, query: BatchQuery) -> None:  # type: ignore[reportIncompatibleMethodOverride]
        """Processes the batch response and handles each individual response.

        Args:
            response: The raw HTTP response from the batch request
            query: The original BatchQuery containing the individual queries

        Raises:
            HTTPError: If any sub-request in the batch fails
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
            super().process_response(sub_resp, sub_qry)

    def execute_query_with_retry(
        self,
        query: BatchQuery,
        max_retry: int = 5,
        base_delay: int = 5,
        jitter: bool = True,
    ) -> None:
        """Execute a batch, retrying only the transiently-failed sub-requests.

        Per the Microsoft Graph batching guidance, a throttled sub-request
        (HTTP 429/503) is retried on its own after the longest ``Retry-After``
        (or exponential backoff) — already-succeeded sub-requests are not
        re-applied, so a partial batch failure doesn't duplicate writes. Routes
        the retry loop through the shared
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
                super(ODataV4BatchRequest, self).process_response(sub_resp, sub_qry)
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
        return BatchQuery(query.context, [qry for qry, _ in failures], sequential=query.sequential)

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
            self.execute_query_with_retry(
                BatchQuery(query.context, half, sequential=query.sequential), max_retry, base_delay, jitter
            )

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
            await self.execute_query_with_retry_async(
                BatchQuery(query.context, half, sequential=query.sequential), max_retry, base_delay, jitter
            )

    @staticmethod
    def _extract_response(response: Response, query: BatchQuery) -> Iterator[Tuple[ClientQuery, Response]]:
        """Extracts individual responses from the batch response.

        Args:
            response: The batch HTTP response
            query: The original BatchQuery

        Yields:
            Tuples of (ClientQuery, Response) for each sub-request
        """
        json_responses = response.json()
        for json_resp in json_responses["responses"]:
            resp = Response()
            resp.status_code = int(json_resp["status"])
            resp.headers = CaseInsensitiveDict(json_resp["headers"])
            resp._content = json.dumps(json_resp["body"]).encode("utf-8")
            qry_id = int(json_resp["id"])
            # Ids are assigned in submission order (see ``_prepare_payload``), so
            # map back with the same list — ``ordered_queries`` re-groups (non-GET
            # first) and would attribute mixed batches to the wrong queries.
            qry = query.queries[qry_id]
            yield qry, resp

    def _prepare_payload(self, query: BatchQuery) -> Dict[str, Any]:
        """Prepares the batch request payload.

        With ``query.sequential`` the sub-requests are chained with ``dependsOn``
        so Graph runs them in order (a failed dependency yields ``424``). Ids are
        assigned in submission order — the same order :meth:`_extract_response`
        maps responses back with.

        Args:
            query: The BatchQuery containing individual queries

        Returns:
            Dictionary containing the JSON batch request structure
        """
        requests_json: list[dict] = []
        previous_id: Optional[str] = None
        for qry in query.queries:
            qry_id = str(len(requests_json))
            depends_on = [previous_id] if (query.sequential and previous_id is not None) else None
            requests_json.append(self._normalize_request(qry, qry_id, depends_on))
            previous_id = qry_id

        return {"requests": requests_json}

    @staticmethod
    def _normalize_request(query: ClientQuery, query_id: str, depends_on: Optional[List[str]] = None) -> Dict[str, Any]:
        """Normalizes an individual query into batch request format.

        Args:
            query: The individual ClientQuery to normalize
            query_id: Unique identifier for the sub-request
            depends_on: List of query IDs this request depends on

        Returns:
            Dictionary representing the normalized request
        """
        request = query.build_request()

        request_json = {
            "id": query_id,
            "url": request.url.replace(query.context.service_root_url, ""),
            "method": request.method.value,
            "headers": request.headers,
        }
        if request.data:
            request_json["body"] = request.data

        if depends_on is not None:
            request_json["dependsOn"] = depends_on
        return request_json
