"""
Run a durable, resumable queue of OneDrive copy jobs.

Graph ``driveItem.copy`` is a long-running operation: the request is accepted
with ``202 Accepted`` and a monitor URL you poll until the new item lands. A
production "copy these 10,000 files" worker cannot hold all of that state in
memory, so it persists each job's *continuation token* — then a crash, a Ctrl-C
or a deploy resumes the in-flight copies instead of restarting them.

This example is that worker in miniature:

* a manifest of copy jobs (``--manifest``, or three generated samples),
* a JSON state file (``--state``) mapping every job to pending/running/done/failed
  and, while running, its serialized ``ContinuationToken``,
* a bounded pool (``--concurrency``) of async tasks, each submitting a copy and
  polling it off the event loop,
* Ctrl-C pauses: the in-flight tokens are already on disk, so re-running the same
  command picks up exactly where it stopped and skips the completed jobs.

Run it once to copy the samples, then run it again to watch it skip them:

    python copy_queue_worker_async.py
    python copy_queue_worker_async.py            # everything is already done

Requires delegated permission ``Files.ReadWrite``.

https://learn.microsoft.com/en-us/graph/api/driveitem-copy
https://learn.microsoft.com/en-us/graph/long-running-actions-overview
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from office365.graph_client import GraphClient
from office365.runtime.lro import ContinuationToken, OperationPoller, OperationStatus
from tests import create_unique_name
from tests.settings import client_id, password, tenant, username

_SAMPLE_COUNT = 3


@dataclass
class CopyJob:
    """One ``source file -> destination folder`` copy request."""

    source: str
    dest_folder: str
    name: str

    @property
    def key(self) -> str:
        """Stable identity used as the state-file key (and for resumption)."""
        return f"{self.source} -> {self.dest_folder}/{self.name}"


def load_state(path: Path) -> dict[str, Any]:
    """Read the state file, or return an empty queue when it is absent/corrupt."""
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_state(path: Path, state: dict[str, Any]) -> None:
    """Atomically persist the queue state (a crash never leaves a half-written file)."""
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(path)


def file_exists(path: Path) -> bool:
    return path.exists()


def remove_file(path: Path) -> None:
    path.unlink(missing_ok=True)


def load_manifest(path: str) -> list[CopyJob]:
    """Read a JSON list of ``{source, dest_folder, name}`` rows."""
    rows = json.loads(Path(path).read_text(encoding="utf-8"))
    return [CopyJob(row["source"], row["dest_folder"], row["name"]) for row in rows]


def write_manifest(path: Path, jobs: list[CopyJob]) -> None:
    path.write_text(json.dumps([asdict(job) for job in jobs], indent=2), encoding="utf-8")


async def bootstrap(client: GraphClient) -> list[CopyJob]:
    """Upload a handful of sample files and a destination folder to copy them into."""
    root = client.me.drive.root
    source_folder = await root.create_folder(create_unique_name("queue_src")).execute_query_async()
    dest_folder = await root.create_folder(create_unique_name("queue_dst")).execute_query_async()

    jobs: list[CopyJob] = []
    for index in range(1, _SAMPLE_COUNT + 1):
        file_name = f"part-{index:02d}.bin"
        await source_folder.upload(file_name, b"x" * (index * 1024)).execute_query_async()
        jobs.append(
            CopyJob(
                source=f"{source_folder.name}/{file_name}",
                dest_folder=dest_folder.name,
                name=f"{file_name}.copy",
            )
        )
    return jobs


async def cleanup(client: GraphClient, jobs: list[CopyJob]) -> None:
    """Delete the generated sample folders (files are removed with their parent)."""
    root = client.me.drive.root
    folders = {job.dest_folder for job in jobs} | {job.source.split("/", 1)[0] for job in jobs}
    for name in folders:
        await root.get_by_path(name).delete_object().execute_query_async()


class CopyQueue:
    """A bounded pool of copy jobs backed by a resumable JSON state file."""

    def __init__(
        self,
        client: GraphClient,
        state_path: Path,
        *,
        concurrency: int,
        interval: float,
        timeout: float,
        verbose: bool,
    ) -> None:
        self._client = client
        self._state_path = state_path
        self._state = load_state(state_path)
        self._concurrency = concurrency
        self._interval = interval
        self._timeout = timeout
        self._verbose = verbose
        self._sem: asyncio.Semaphore | None = None
        self._lock: asyncio.Lock | None = None
        self._submit_lock: asyncio.Lock | None = None
        self.counts = {"copied": 0, "resumed": 0, "skipped": 0, "failed": 0}

    async def run(self, jobs: list[CopyJob]) -> dict[str, int]:
        """Run every job (bounded), returning per-outcome counts."""
        self._sem = asyncio.Semaphore(self._concurrency)
        self._lock = asyncio.Lock()
        self._submit_lock = asyncio.Lock()
        await asyncio.gather(*(self._run_one(job) for job in jobs))
        return self.counts

    async def _run_one(self, job: CopyJob) -> None:
        assert self._sem is not None and self._lock is not None
        async with self._sem:
            if self._state.get(job.key, {}).get("status") == "done":
                self.counts["skipped"] += 1
                print(f"  skip   {job.name} (already copied)")
                return
            try:
                poller, resumed = await self._start(job)
                # Persist the token *before* polling, so an interrupt can resume it.
                await self._mark(job.key, status="running", token=poller.to_continuation_token().to_json())
                if resumed:
                    self.counts["resumed"] += 1
                    print(f"  resume {job.name}")
                else:
                    print(f"  submit {job.name} -> {poller.poll_url}")
                status = await poller.wait_async(on_progress=self._reporter(job))
            except asyncio.CancelledError:
                raise
            except Exception as ex:  # noqa: BLE001 — isolate per-job failures
                await self._mark(job.key, status="failed", error=str(ex))
                self.counts["failed"] += 1
                print(f"  fail   {job.name}: {ex}")
                return
            await self._mark(job.key, status="done", resource_id=status.resource_id)
            self.counts["copied"] += 1
            print(f"  done   {job.name} ({status.resource_id})")

    async def _start(self, job: CopyJob) -> tuple[OperationPoller, bool]:
        """Resume a saved operation, or submit a fresh copy. Returns ``(poller, resumed)``."""
        token_json = self._state.get(job.key, {}).get("token")
        if token_json:
            poller = OperationPoller.from_continuation_token(
                self._client,
                ContinuationToken.from_json(token_json),
                interval=self._interval,
                timeout=self._timeout,
                authenticate=True,
            )
            return poller, True

        assert self._submit_lock is not None
        async with self._submit_lock:  # a context owns one request queue — serialize submits
            root = self._client.me.drive.root
            source = await root.get_by_path(job.source).get().execute_query_async()
            dest = await root.get_by_path(job.dest_folder).get().execute_query_async()
            result = source.copy(name=job.name, parent=dest)
            await result.execute_query_async()
        return result.to_poller(interval=self._interval, timeout=self._timeout), False

    async def _mark(self, key: str, **fields: Any) -> None:
        assert self._lock is not None
        async with self._lock:
            entry = self._state.setdefault(key, {})
            entry.update(fields)
            if entry.get("status") == "done":
                entry.pop("token", None)
            save_state(self._state_path, self._state)

    def _reporter(self, job: CopyJob):
        if not self._verbose:
            return None

        def report(status: OperationStatus) -> None:
            pct = f"{status.percentage_complete:5.1f}%" if status.percentage_complete is not None else "  ..."
            print(f"  poll   {job.name}: {pct} {status.status or status.http_status}", flush=True)

        return report


async def main() -> None:
    parser = argparse.ArgumentParser(description="Run a durable, resumable copy queue")
    parser.add_argument("--manifest", help="JSON list of copy jobs; samples are generated when omitted")
    parser.add_argument("--state", default="copy_queue_state.json", help="where the resumable state lives")
    parser.add_argument("--default-manifest", default="copy_queue_jobs.json", help="manifest written for samples")
    parser.add_argument("--concurrency", type=int, default=3, help="copies in flight (default: 3)")
    parser.add_argument("--interval", type=float, default=5, help="seconds between polls (default: 5)")
    parser.add_argument("--timeout", type=float, default=1800, help="per-copy timeout in seconds")
    parser.add_argument("--reset", action="store_true", help="ignore/reset any saved state and start over")
    parser.add_argument("--quiet", action="store_true", help="hide per-poll progress lines")
    parser.add_argument("--keep", action="store_true", help="keep the generated samples and state")
    args = parser.parse_args()

    state_path = Path(args.state)
    if args.reset:
        remove_file(state_path)

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    async with client:
        bootstrapped = False
        if args.manifest:
            jobs = load_manifest(args.manifest)
        else:
            default_manifest = Path(args.default_manifest)
            if file_exists(default_manifest) and file_exists(state_path):
                jobs = load_manifest(str(default_manifest))
                print(f"Resuming {len(jobs)} job(s) from {state_path}")
            else:
                jobs = await bootstrap(client)
                write_manifest(default_manifest, jobs)
                bootstrapped = True
                print(f"Generated {len(jobs)} sample job(s); manifest {default_manifest}")

        queue = CopyQueue(
            client,
            state_path,
            concurrency=args.concurrency,
            interval=args.interval,
            timeout=args.timeout,
            verbose=not args.quiet,
        )
        try:
            counts = await queue.run(jobs)
        finally:
            print(f"\nState saved to {state_path}")
        print(f"Summary: {counts}")

        if bootstrapped and not args.keep:
            await cleanup(client, jobs)
            remove_file(state_path)
            remove_file(Path(args.default_manifest))
            print("Samples and state removed.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(130)
