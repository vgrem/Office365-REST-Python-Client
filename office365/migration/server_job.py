"""Server-side migration job — submit + monitor.

The SharePoint Migration API runs large migrations server-side: content is
packaged and uploaded to Azure Storage, then an *ingestion job* ingests it. This
wrapper submits such a job and polls its status with a ``Progress`` hook.

Status can be read two ways:

- ``GetMigrationJobProgress`` — the recommended API; use :meth:`status_fn` as the
  ``monitor`` status source (or :meth:`progress` directly);
- a caller-supplied ``status_fn`` — e.g. an Azure queue or the Graph
  ``SharePointMigrationJobProgressEvent`` stream.

Every wait has an async twin (:meth:`monitor_async` and friends) so a long
ingestion job can be polled off the event loop, next to other work.

The wait itself is :class:`MigrationJobWait`, the shared
:class:`office365.runtime.operation.Operation` specialised to "one poll = read the
job's status and counters". So the deadline is measured on the clock (a slow
``GetMigrationJobProgress`` call counts against it, rather than being free), the
pause honours ``Retry-After`` when there is one, and a caller who wants more than
the terminal status can hold the wait and stream it:

    wait = job.job_wait(job_id)
    for status in wait.stream():
        print(status.status, status.percentage_complete)
"""

from __future__ import annotations

import asyncio
import json
import time
import uuid
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any

from office365.runtime.operation import Operation, OperationStatus
from office365.runtime.operations import emit_progress

if TYPE_CHECKING:
    from office365.runtime.operations import Progress

__all__ = ["MigrationJobWait", "MigrationServerJob", "job_errors", "parse_progress_events"]

#: A job counter carries no HTTP status of its own. ``202`` is the honest stand-in:
#: it keeps "is this terminal?" a question about the job's own status string, so an
#: unrecognised status keeps polling instead of being read as an ending.
_JOB_PENDING_HTTP = 202

_StatusFn = Callable[[str], "tuple[str, int, int | None]"]
_AsyncStatusFn = Callable[[str], "Awaitable[tuple[str, int, int | None]]"]

# Migration API progress events -> monitor statuses (JobEnd resolved separately).
_EVENT_STATUS = {
    "JobQueued": "queued",
    "JobStart": "processing",
    "JobProgress": "processing",
    "JobError": "processing",
}


def parse_progress_events(events: list[dict]) -> tuple[str, int, int | None]:
    """Reduce accumulated Migration API progress events to ``(status, done, total)``.

    Pass the events accumulated across polls (they are append-only), so the status
    stays monotonic even when a poll returns no new events.
    """
    status = "queued"
    done = 0
    total: int | None = None
    for event in events:
        kind = event.get("Event")
        if kind == "JobEnd":
            status = "failed" if int(event.get("TotalErrors") or 0) else "succeeded"
        elif kind in _EVENT_STATUS:
            status = _EVENT_STATUS[kind]
        if event.get("ObjectsProcessed") is not None:
            done = int(event["ObjectsProcessed"])
        if event.get("TotalExpectedSPObjects") is not None:
            total = int(event["TotalExpectedSPObjects"])
    return status, done, total


def job_errors(events: list[dict]) -> list[dict]:
    """The ``JobError`` events from a progress log (each carries ``Message``/``ErrorType``/``Url``)."""
    return [event for event in events if event.get("Event") == "JobError"]


class MigrationJobWait(Operation[str]):
    """The wait on a server-side migration job.

    One poll reads the job's status and counters; the deadline, pacing, progress
    hook, cancel and streaming come from :class:`Operation`. ``wait()`` returns the
    terminal status string, spelled as the status source spelled it — monitoring
    reports what happened, it does not rewrite the job's vocabulary.

    ``http_status`` on each snapshot is :data:`_JOB_PENDING_HTTP`: a job counter has
    no HTTP status, and terminality here is a question about the *status string*, so
    an unrecognised status keeps polling rather than ending the wait.
    """

    def __init__(
        self,
        job_id: str,
        *,
        status_fn: _StatusFn | None = None,
        async_status_fn: _AsyncStatusFn | None = None,
        interval: float = 5.0,
        timeout: float = 1800.0,
        progress: Callable[["Progress"], None] | None = None,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] | None = None,
        async_sleep: Callable[[float], Any] | None = None,
    ) -> None:
        super().__init__(
            interval=interval,
            timeout=timeout,
            on_progress=self._emit,
            clock=clock,
            sleep=sleep,
            async_sleep=async_sleep,
        )
        self._job_id = job_id
        self._status_fn = status_fn
        self._async_status_fn = async_status_fn
        self._progress = progress
        self._objects_done = 0
        self._objects_total: int | None = None

    def _step(self) -> OperationStatus:
        if self._status_fn is None:
            raise NotImplementedError("this wait was given only an async status function; use wait_async()/astream()")
        return self._observe(self._status_fn(self._job_id))

    async def _step_async(self) -> OperationStatus:
        if self._async_status_fn is None:
            raise NotImplementedError("this wait was given only a sync status function; use wait()/stream()")
        return self._observe(await self._async_status_fn(self._job_id))

    def _outcome(self, status: OperationStatus) -> str:
        """The job's terminal status, as its own status source spelled it."""
        return status.status or ""

    def _observe(self, result: tuple[str, int, int | None]) -> OperationStatus:
        status, done, total = result
        self._objects_done, self._objects_total = done, total
        return OperationStatus(
            status=status,
            http_status=_JOB_PENDING_HTTP,
            percentage_complete=(100.0 * done / total) if total else None,
        )

    def _emit(self, status: OperationStatus) -> None:
        """Report the counters the job source gave, as a ``Progress`` snapshot."""
        emit_progress(
            self._progress,
            done=self._objects_done,
            total=self._objects_total,
            stage="migrating",
        )

    @property
    def job_id(self) -> str:
        """The job being waited on."""
        return self._job_id


class MigrationServerJob:
    """A server-side migration job: submit an ingestion job, then monitor it."""

    def __init__(self, site) -> None:
        self._site = site

    def submit(
        self,
        g_web_id,
        azure_container_source_uri: str,
        azure_container_manifest_uri: str,
        azure_queue_report_uri: str | None = None,
        ingestion_task_key: str | None = None,
    ) -> str:
        """Submit an ingestion job for the staged package and return its job id.

        Args:
            g_web_id: Identifier of the destination web.
            azure_container_source_uri: Content container URI (with SAS token).
            azure_container_manifest_uri: Manifest container URI (with SAS token).
            azure_queue_report_uri: Optional Azure queue URI receiving progress reports.
            ingestion_task_key: Optional task key (a UUID is generated when omitted).
        """
        result = self._site.create_migration_ingestion_job(
            g_web_id=g_web_id,
            azure_container_source_uri=azure_container_source_uri,
            azure_container_manifest_uri=azure_container_manifest_uri,
            azure_queue_report_uri=azure_queue_report_uri,
            ingestion_task_key=ingestion_task_key or uuid.uuid4().hex,
        )
        return result.execute_query().value

    def submit_encrypted(
        self,
        g_web_id,
        azure_container_source_uri: str,
        azure_container_manifest_uri: str,
        aes256_cbc_key: str | bytes,
        azure_queue_report_uri: str | None = None,
    ) -> str:
        """Submit an ingestion job for an AES-256-CBC encrypted package.

        Required for SharePoint-provided containers; use the ``EncryptionKey`` from
        ``Site.provision_migration_containers`` (a base64 string, passed through).
        """
        result = self._site.create_migration_job_encrypted(
            g_web_id=g_web_id,
            azure_container_source_uri=azure_container_source_uri,
            azure_container_manifest_uri=azure_container_manifest_uri,
            aes256_cbc_key=aes256_cbc_key,
            azure_queue_report_uri=azure_queue_report_uri,
        )
        return result.execute_query().value

    def progress(self, job_id: str, next_token: str = "0") -> tuple[list[dict], str]:
        """Fetch a page of progress events and the next paging token.

        Args:
            job_id: The migration job id.
            next_token: Paging token; use ``"0"`` for the initial request.

        Returns:
            ``(events, next_token)`` — events are decoded from the JSON log strings.
        """
        result = self._site.get_migration_job_progress(job_id, next_token).execute_query()
        value = result.value
        events = [json.loads(line) for line in (value.Logs or [])]
        return events, value.NextToken or next_token

    async def progress_async(self, job_id: str, next_token: str = "0") -> tuple[list[dict], str]:
        """Async twin of :meth:`progress` — awaits the progress GET off the loop."""
        result = await self._site.get_migration_job_progress(job_id, next_token).execute_query_async()
        value = result.value
        events = [json.loads(line) for line in (value.Logs or [])]
        return events, value.NextToken or next_token

    def all_events(self, job_id: str) -> list[dict]:
        """All progress events for a job (paged until the token stops advancing).

        For a completed job the API is idempotent per token, so this collects the
        full lifecycle — including any ``JobError`` entries.
        """
        events: list[dict] = []
        token = "0"
        for _ in range(100):  # bound: a page with no new events ends the loop
            page, next_token = self.progress(job_id, token)
            events.extend(page)
            if not page or next_token == token:
                break
            token = next_token
        return events

    async def all_events_async(self, job_id: str) -> list[dict]:
        """Async twin of :meth:`all_events` — pages the progress log with awaits."""
        events: list[dict] = []
        token = "0"
        for _ in range(100):  # bound: a page with no new events ends the loop
            page, next_token = await self.progress_async(job_id, token)
            events.extend(page)
            if not page or next_token == token:
                break
            token = next_token
        return events

    def errors(self, job_id: str) -> list[dict]:
        """The ``JobError`` events for a job (message, type, url)."""
        return job_errors(self.all_events(job_id))

    async def errors_async(self, job_id: str) -> list[dict]:
        """Async twin of :meth:`errors` — the ``JobError`` events for a job."""
        return job_errors(await self.all_events_async(job_id))

    def status_fn(self) -> Callable[[str], tuple[str, int, int | None]]:
        """A ``monitor`` status function backed by ``GetMigrationJobProgress``."""
        state: dict = {"token": "0", "events": []}

        def _status(job_id: str) -> tuple[str, int, int | None]:
            events, token = self.progress(job_id, state["token"])
            state["token"] = token
            state["events"].extend(events)
            return parse_progress_events(state["events"])

        return _status

    def status_fn_async(self) -> Callable[[str], Awaitable[tuple[str, int, int | None]]]:
        """An awaitable ``monitor_async`` status function backed by ``GetMigrationJobProgress``."""
        state: dict = {"token": "0", "events": []}

        async def _status(job_id: str) -> tuple[str, int, int | None]:
            events, token = await self.progress_async(job_id, state["token"])
            state["token"] = token
            state["events"].extend(events)
            return parse_progress_events(state["events"])

        return _status

    def job_wait(
        self,
        job_id: str,
        *,
        status_fn: _StatusFn | None = None,
        async_status_fn: _AsyncStatusFn | None = None,
        interval: float = 5,
        timeout: float = 1800,
        progress: Callable[["Progress"], None] | None = None,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] | None = None,
        async_sleep: Callable[[float], Any] | None = None,
    ) -> MigrationJobWait:
        """Build the wait for a job, without running it.

        Handy when the caller wants to stream the polls, cancel the wait, or run
        several jobs concurrently::

            waits = [job.job_wait(job_id, async_status_fn=...) for job_id in jobs]
            statuses = {w.job_id: await w.wait_async() for w in waits}

        Args:
            job_id: The migration job id.
            status_fn: Callable returning ``(status, done, total)`` for a job id.
            async_status_fn: Awaitable twin of ``status_fn``.
            interval: Seconds between polls (``Retry-After`` wins when present).
            timeout: Maximum seconds to wait before raising
                :class:`OperationTimeoutError`.
            progress: Optional hook fired per poll with a ``Progress`` snapshot.
            clock: Injectable monotonic clock (tests).
            sleep: Override the pause between polls (tests); by default it is the
                interruptible one, so :meth:`MigrationJobWait.cancel` wakes it.
            async_sleep: Override the async pause (tests).

        Supplying neither reader defaults both to ``GetMigrationJobProgress`` via
        :meth:`status_fn` / :meth:`status_fn_async`. Supplying only a sync
        ``status_fn`` bridges it for async use with ``asyncio.to_thread`` (the read
        is a blocking HTTP GET), and only an async one is async-only.
        """
        if status_fn is None and async_status_fn is None:
            sync: _StatusFn | None = self.status_fn()
            asyn: _AsyncStatusFn | None = self.status_fn_async()
        elif async_status_fn is None:
            assert status_fn is not None  # the branch above covers both-None
            sync, asyn = status_fn, _as_awaitable(status_fn)
        else:
            sync = status_fn
            asyn = async_status_fn
        return MigrationJobWait(
            job_id,
            status_fn=sync,
            async_status_fn=asyn,
            interval=float(interval),
            timeout=float(timeout),
            progress=progress,
            clock=clock,
            sleep=sleep,
            async_sleep=async_sleep,
        )

    def monitor(
        self,
        job_id: str,
        status_fn: _StatusFn | None = None,
        interval: float = 5,
        timeout: float = 1800,
        progress: Callable[["Progress"], None] | None = None,
    ) -> str:
        """Poll a job until it reaches a terminal status.

        The status is *reported*, not judged: a job that ends ``failed`` returns
        ``"failed"`` (the caller decides what that means), while a job that never
        ends raises :class:`OperationTimeoutError` — a ``TimeoutError``.

        Args:
            job_id: The migration job id.
            status_fn: Callable returning ``(status, done, total)`` for a job id.
              Defaults to a ``GetMigrationJobProgress``-backed reader.
            interval: Seconds between polls.
            timeout: Maximum seconds to wait before raising ``TimeoutError``.
            progress: Optional hook fired per poll with a ``Progress`` snapshot.

        Returns:
            The terminal status.

        Raises:
            TimeoutError: When the job doesn't finish within ``timeout`` seconds.
        """
        return self.job_wait(job_id, status_fn=status_fn, interval=interval, timeout=timeout, progress=progress).wait(
            raise_on_failure=False
        )

    async def monitor_async(
        self,
        job_id: str,
        status_fn: _AsyncStatusFn | None = None,
        interval: float = 5,
        timeout: float = 1800,
        progress: Callable[["Progress"], None] | None = None,
    ) -> str:
        """Await a job until it reaches a terminal status (async twin of :meth:`monitor`).

        The status GET and the wait between polls run on the event loop, so this
        can monitor one job while the caller serves other requests, or monitor
        several jobs concurrently (one :class:`MigrationServerJob` per context).

        Args:
            job_id: The migration job id.
            status_fn: Awaitable returning ``(status, done, total)`` for a job id.
              Defaults to a ``GetMigrationJobProgress``-backed reader.
            interval: Seconds between polls.
            timeout: Maximum seconds to wait before raising ``TimeoutError``.
            progress: Optional hook fired per poll with a ``Progress`` snapshot.

        Returns:
            The terminal status.

        Raises:
            TimeoutError: When the job doesn't finish within ``timeout`` seconds.
        """
        return await self.job_wait(
            job_id,
            async_status_fn=status_fn,
            interval=interval,
            timeout=timeout,
            progress=progress,
        ).wait_async(raise_on_failure=False)


def _as_awaitable(status_fn: _StatusFn) -> _AsyncStatusFn:
    """Bridge a blocking status reader for async use (the read is an HTTP GET)."""

    async def _status(job_id: str) -> tuple[str, int, int | None]:
        return await asyncio.to_thread(status_fn, job_id)

    return _status
