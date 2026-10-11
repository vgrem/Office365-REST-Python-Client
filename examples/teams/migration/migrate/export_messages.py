"""
Export messages for compliance/backup using the deferred collection adapters.

    python migrate/export_messages.py --output ./messages --team <team-id>
    python migrate/export_messages.py --output ./messages --user user@contoso.com
    python migrate/export_messages.py --output ./messages --tenant
    python migrate/export_messages.py --output ./messages --filter "createdDateTime gt 2024-01-01T00:00:00Z"

Scope defaults to ``--user`` (the configured test user); pass ``--team`` for a
team's channels or ``--tenant`` for tenant-wide channel messages.

Writes ``messages.ndjson`` and (unless ``--no-attachments``) inline images under
``attachments/``. Everything is deferred: the single ``execute_query()`` pages
through the results and writes the files.

Requires application permission Teamwork.Migrate.All (plus the matching read
permissions for the chosen scope).
"""

import argparse
import tempfile
from pathlib import Path

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, client_secret, tenant, user_principal


def _scope_hint(args) -> str:
    if args.tenant:
        return "Tenant-wide channel messages need Teamwork.Migrate.All (and ChannelMessage.Read.All)."
    if args.team:
        return "Channel messages need ChannelMessage.Read.All."
    return "User chat messages need Chat.Read.All or Chat.ReadWrite.All."


def main():
    parser = argparse.ArgumentParser(description="Export Teams messages to NDJSON")
    parser.add_argument("--output", default=str(Path(tempfile.gettempdir()) / "teams_messages"), help="output directory")
    parser.add_argument("--team", default=None, help="team id (all channel messages)")
    parser.add_argument("--user", default=user_principal, help=f"user id/UPN (default: {user_principal})")
    parser.add_argument("--tenant", action="store_true", help="tenant-wide channel messages (overrides --user)")
    parser.add_argument("--filter", default=None, help="OData $filter, e.g. a date range")
    parser.add_argument("--no-attachments", action="store_true", help="skip hosted contents")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)

    if args.team:
        messages = client.teams[args.team].channels.get_all_messages()
    elif args.tenant:
        messages = client.teams.get_all_messages()
    else:
        messages = client.users[args.user].chats.get_all_messages()
    if args.filter:
        messages.filter(args.filter)

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    try:
        with open(out / "messages.ndjson", "w", encoding="utf-8") as f:
            chain = messages.get_all().to_ndjson(f)
            if not args.no_attachments:
                chain.download_hosted_contents(out / "attachments")
            chain.execute_query()
    except ClientRequestException as ex:
        if ex.code not in ("Forbidden", "UnknownError"):
            raise
        print(f"✗ {_scope_hint(args)}\n  ({ex.code}: {str(ex)[:200]})")
        return

    print(f"Exported {len(messages)} messages to {out / 'messages.ndjson'}")


if __name__ == "__main__":
    main()
