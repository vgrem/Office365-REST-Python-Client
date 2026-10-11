"""
Provision many Microsoft Teams concurrently and await every async operation.

Onboarding usually means a batch of teams: create (or clone) each one and wait
for provisioning. Every create/clone is a Graph long-running operation — a
``teamsAsyncOperation`` you poll until ``succeeded`` — so the fan-out is exactly
what async is for: N operations make progress at once instead of one blocking
``create_and_wait`` after another.

This example reads ``name,description?,template?,clone_from?`` rows, submits them
all, then polls the whole batch through ``execute_query_parallel_async`` — the
library's bounded, per-query-retrying fan-out — so no clone or hand-rolled
``Semaphore`` is needed. Failures are isolated to a single team, and the run ends
with a summary. With no ``--file`` it creates a temporary source team and clones
it, so the example is self-contained.

Requires application permissions ``Group.ReadWrite.All`` and
``TeamSettings.ReadWrite.All`` (the app-only client secret flow is used so the
batch is not tied to one signed-in user).

https://learn.microsoft.com/en-us/graph/api/team-post
https://learn.microsoft.com/en-us/graph/api/team-clone
https://learn.microsoft.com/en-us/graph/api/resources/teamsasyncoperation
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import sys
import time
import uuid
from dataclasses import dataclass

from office365.graph_client import GraphClient
from office365.teams.clonableteamparts import ClonableTeamParts
from office365.teams.operations.async_operation import TeamsAsyncOperation
from office365.teams.operations.async_status import TeamsAsyncOperationStatus
from office365.teams.visibility_type import TeamVisibilityType
from tests import create_unique_name
from tests.settings import client_id, client_secret, tenant

DEFAULT_TEMPLATE = "standard"
_TERMINAL = (TeamsAsyncOperationStatus.succeeded, TeamsAsyncOperationStatus.failed)


@dataclass
class TeamRequest:
    """One team to provision."""

    name: str
    description: str | None = None
    template: str = DEFAULT_TEMPLATE
    clone_from: str | None = None


def read_rows(path: str) -> list[TeamRequest]:
    """Parse the CSV (sync file I/O kept out of the event loop)."""
    with open(path, encoding="utf-8") as handle:
        return [
            TeamRequest(
                name=row["name"].strip(),
                description=(row.get("description") or "").strip() or None,
                template=(row.get("template") or DEFAULT_TEMPLATE).strip(),
                clone_from=(row.get("clone_from") or "").strip() or None,
            )
            for row in csv.DictReader(handle)
        ]


def mail_nickname(name: str) -> str:
    """A unique, lowercase mail alias (a clone needs one distinct from the source)."""
    slug = "".join(ch for ch in name.lower() if ch.isalnum())[:20] or "team"
    return f"{slug}{uuid.uuid4().hex[:6]}"


async def submit(client: GraphClient, row: TeamRequest) -> TeamsAsyncOperation:
    """Create or clone a team; either call returns a ``teamsAsyncOperation``."""
    if row.clone_from:
        return (
            await client.teams[row.clone_from]
            .clone(
                mail_nickname=mail_nickname(row.name),
                display_name=row.name,
                parts_to_clone=ClonableTeamParts.settings,
                visibility=TeamVisibilityType.public,
                description=row.description,
            )
            .execute_query_async()
        )
    return await client.teams.create(row.name, row.description, row.template).execute_query_async()


async def poll_all(
    client: GraphClient,
    operations: list[tuple[TeamRequest, TeamsAsyncOperation]],
    *,
    interval: float,
    timeout: float,
    concurrency: int,
) -> None:
    """Poll every submitted operation through one bounded parallel fan-out."""
    deadline = time.monotonic() + timeout
    pending = list(operations)
    while pending:
        errors: list[BaseException] = []
        for _row, operation in pending:
            operation.get()  # queue a status GET for each unfinished operation
        await client.execute_query_parallel_async(
            concurrency=min(concurrency, len(pending)),
            on_error=lambda _query, error, sink=errors: sink.append(error),
        )
        if errors:
            print(f"  {len(errors)} poll(s) failed transiently; retrying")
        pending = [(row, op) for row, op in pending if op.status not in _TERMINAL]
        if not pending:
            return
        if time.monotonic() >= deadline:
            raise TimeoutError(f"{len(pending)} team operation(s) unfinished after {timeout}s")
        await asyncio.sleep(interval)


def report(rows: list[tuple[TeamRequest, TeamsAsyncOperation]]) -> list[str]:
    """Print the per-team outcome and return the ids of the teams that succeeded."""
    ready: list[str] = []
    for row, operation in rows:
        if operation.status == TeamsAsyncOperationStatus.succeeded:
            ready.append(operation.target_resource_id or "")
            print(f"  ready  {row.name} ({operation.target_resource_id})")
        elif operation.status == TeamsAsyncOperationStatus.failed:
            print(f"  failed {row.name}: {operation.error}")
        else:
            print(f"  pending {row.name}: {operation.status.name}")
    return [team_id for team_id in ready if team_id]


async def remove_teams(client: GraphClient, team_ids: list[str], *, concurrency: int) -> None:
    """Delete the provisioned teams (a team is deleted through its backing group)."""
    for team_id in team_ids:
        client.groups[team_id].delete_object()
    if team_ids:
        await client.execute_query_parallel_async(concurrency=min(concurrency, len(team_ids)))
    print(f"Deleted {len(team_ids)} team(s).")


async def main() -> None:
    parser = argparse.ArgumentParser(description="Provision many teams concurrently")
    parser.add_argument("--file", help="CSV with name,description?,template?,clone_from? columns")
    parser.add_argument("--concurrency", type=int, default=4, help="polls in flight (default: 4)")
    parser.add_argument("--interval", type=float, default=15, help="seconds between polls (default: 15)")
    parser.add_argument("--timeout", type=float, default=900, help="batch timeout in seconds")
    parser.add_argument("--keep", action="store_true", help="keep the provisioned teams")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    source_id: str | None = None
    async with client:
        if args.file:
            requests = read_rows(args.file)
        else:
            source_name = create_unique_name("bulk_src")
            source_op = await client.teams.create(source_name, "Template team for the batch").execute_query_async()
            await source_op.poll_for_status_async(
                timeout_sec=int(args.timeout), polling_interval=max(1, int(args.interval))
            )
            if source_op.status != TeamsAsyncOperationStatus.succeeded:
                sys.exit(f"Source team provisioning failed: {source_op.error}")
            source_id = source_op.target_resource_id or ""
            requests = [
                TeamRequest(f"Onboarding {index}", "Cloned from the template team", clone_from=source_id)
                for index in (1, 2)
            ]
            requests.append(TeamRequest("Onboarding 3", "Created from the standard template"))
            print(f"Source team ready: {source_name} ({source_id})")

        if not requests:
            sys.exit("No rows to provision")

        submitted: list[tuple[TeamRequest, TeamsAsyncOperation]] = []
        for row in requests:
            submitted.append((row, await submit(client, row)))
            print(f"  submitted {row.name}")

        try:
            await poll_all(
                client,
                submitted,
                interval=args.interval,
                timeout=args.timeout,
                concurrency=args.concurrency,
            )
        except TimeoutError as ex:
            print(f"  {ex}")

        ready_ids = report(submitted)
        print(f"\nProvisioned {len(ready_ids)}/{len(requests)} team(s)")

        if not args.keep:
            if source_id:
                ready_ids.append(source_id)
            await remove_teams(client, ready_ids, concurrency=args.concurrency)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(130)
