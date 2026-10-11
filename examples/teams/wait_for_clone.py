"""
Clone a Microsoft Teams team and wait for provisioning (synchronous).

Cloning a team is asynchronous: Graph accepts the request and returns a
``teamsAsyncOperation`` that reaches ``succeeded`` once the copy is ready.
``clone_and_wait()`` chains the submission, the poll and a final ``GET`` so a
single ``execute_query()`` returns the provisioned team. For the explicit
``clone()`` + ``poll_for_status()`` form, or an awaitable version, see
``examples/patterns/lro/wait_team_clone_async.py``.

A temporary source team is created first when ``--team-id`` is omitted, so the
example is self-contained; pass ``--team-id`` to clone an existing team instead.

Requires application permissions ``Team.Create``, ``TeamSettings.ReadWrite.All``
and ``Directory.ReadWrite.All``.

https://learn.microsoft.com/en-us/graph/api/team-clone
https://learn.microsoft.com/en-us/graph/api/resources/teamsasyncoperation
"""

import argparse
import uuid

from office365.graph_client import GraphClient
from office365.teams.clonableteamparts import ClonableTeamParts
from office365.teams.visibility_type import TeamVisibilityType
from tests.settings import client_id, client_secret, tenant


def main() -> None:
    parser = argparse.ArgumentParser(description="Clone a team and wait for provisioning")
    parser.add_argument("--team-id", help="source team id; a temporary team is created when omitted")
    parser.add_argument("--keep", action="store_true", help="keep the source and cloned teams")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    tag = uuid.uuid4().hex[:6]

    if args.team_id:
        source = client.teams[args.team_id]
        created_source = False
    else:
        source = client.teams.create_and_wait(f"Clone Source {tag}").execute_query()
        created_source = True
        print(f"Source team ready: {source.display_name} ({source.id})")

    cloned = source.clone_and_wait(
        mail_nickname=f"syncclone{tag}",
        display_name=f"Sync Clone {tag}",
        parts_to_clone=ClonableTeamParts.settings,
        visibility=TeamVisibilityType.private,
    ).execute_query()
    print(f"Cloned team ready: {cloned.display_name} ({cloned.id})")

    if not args.keep:
        cloned.delete_object().execute_query()
        if created_source:
            source.delete_object().execute_query()
        print("Teams deleted.")


if __name__ == "__main__":
    main()
