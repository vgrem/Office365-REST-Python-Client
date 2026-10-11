"""
Clone a Microsoft Teams team and await provisioning without blocking the loop.

Team creation and cloning are asynchronous Graph operations: the request is
accepted with ``202 Accepted`` and a ``teamsAsyncOperation`` you poll until its
status is ``succeeded``. ``clone()`` returns that operation; after
``execute_query_async()`` submits it, ``poll_for_status_async()`` polls off the
event loop — a transient ``404`` (the operation is briefly unavailable) is
treated as a polling gap, not a failure.

A temporary source team is created first when ``--team-id`` is omitted, so the
example is self-contained; pass ``--team-id`` to clone an existing team instead.

Requires delegated permissions ``Team.Create`` and ``TeamSettings.ReadWrite.All``.

https://learn.microsoft.com/en-us/graph/api/team-clone
https://learn.microsoft.com/en-us/graph/api/resources/teamsasyncoperation
"""

from __future__ import annotations

import argparse
import asyncio
import sys
import uuid

from office365.graph_client import GraphClient
from office365.teams.clonableteamparts import ClonableTeamParts
from office365.teams.operations.async_status import TeamsAsyncOperationStatus
from office365.teams.visibility_type import TeamVisibilityType
from tests.settings import client_id, password, tenant, username


async def main() -> None:
    parser = argparse.ArgumentParser(description="Clone a team and await provisioning")
    parser.add_argument("--team-id", help="source team id; a temporary team is created when omitted")
    parser.add_argument("--keep", action="store_true", help="keep the source and cloned teams")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    tag = uuid.uuid4().hex[:6]
    async with client:
        if args.team_id:
            source = client.teams[args.team_id]
            created_source = False
        else:
            source = await client.teams.create_and_wait(f"LRO Source {tag}").execute_query_async()
            created_source = True
            print(f"Source team ready: {source.display_name} ({source.id})")

        # Submit the clone and poll the teamsAsyncOperation to completion.
        operation = await source.clone(
            mail_nickname=f"lroclone{tag}",
            display_name=f"LRO Clone {tag}",
            parts_to_clone=ClonableTeamParts.settings,
            visibility=TeamVisibilityType.private,
        ).execute_query_async()
        print(f"Clone submitted; polling {operation.resource_path} ...")

        await operation.poll_for_status_async(
            timeout_sec=600,
            polling_interval=15,
            success_callback=lambda op: print(f"Clone succeeded: {op.target_resource_id}"),
            failure_callback=lambda op: print(f"Clone failed: {op.error}"),
        )
        if operation.status != TeamsAsyncOperationStatus.succeeded:
            return

        cloned = await client.teams[operation.target_resource_id].get().execute_query_async()
        print(f"Cloned team ready: {cloned.display_name} ({cloned.id})")

        if not args.keep:
            await cloned.delete_object().execute_query_async()
            if created_source:
                await source.delete_object().execute_query_async()
            print("Teams deleted.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(130)
