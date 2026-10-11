"""
Manage channel lifecycle: list, create, update, delete, and channel email.

Channel membership type is set at creation and cannot be changed later.

Requires delegated or application permissions:
    Channel.ReadBasic.All        List channels
    Channel.Create               Create channels
    ChannelSettings.ReadWrite.All  Update channels and email
    Channel.Delete.All           Delete channels
    Team.ReadBasic.All           Resolve team by id

https://learn.microsoft.com/en-us/graph/api/channel-list
https://learn.microsoft.com/en-us/graph/api/channel-post
"""

import argparse

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.http.prefer import prefer_include_unknown_enum_members
from office365.teams.channels.channel import Channel
from office365.teams.team import Team
from tests.settings import client_id, client_secret, tenant

MEMBERSHIP_TYPES = {"standard", "private"}


def _client() -> GraphClient:
    return GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)


def _get_team(client: GraphClient, team_id: str) -> Team:
    return client.teams[team_id].get().execute_query()


def _get_channel(team: Team, channel_id: str) -> Channel:
    return team.channels[channel_id].get().execute_query()


def cmd_list(client: GraphClient, args: argparse.Namespace) -> None:
    team = _get_team(client, args.team_id)
    qry = team.channels.get()
    # `shared` is an evolvable enum member: ask Graph to return it instead of unknownFutureValue
    client.before_execute(prefer_include_unknown_enum_members)
    channels = qry.execute_query()
    print(f"Channels in '{team.display_name}' ({len(channels)}):")
    for ch in channels:
        archived = "archived" if ch.is_archived else "active  "
        membership = "unknown" if ch.membership_type.value == "2" else ch.membership_type.value
        print(f"  {ch.id:50s} {ch.display_name or '(unnamed)':30s} {membership:9s} {archived} email={ch.email or '-'}")


def cmd_create(client: GraphClient, args: argparse.Namespace) -> None:
    team = _get_team(client, args.team_id)
    channel = team.channels.add(
        display_name=args.name,
        description=args.description,
        membership_type=args.type,
    ).execute_query()
    print(f"✓ Channel created: {channel.display_name} ({channel.id})")


def cmd_update(client: GraphClient, args: argparse.Namespace) -> None:
    team = _get_team(client, args.team_id)
    channel = _get_channel(team, args.channel_id)
    if args.name:
        channel.set_property("displayName", args.name)
    if args.description is not None:
        channel.set_property("description", args.description)
    channel.update().execute_query()
    print(f"✓ Channel updated: {channel.display_name}")


def cmd_delete(client: GraphClient, args: argparse.Namespace) -> None:
    team = _get_team(client, args.team_id)
    channel = _get_channel(team, args.channel_id)
    channel.delete_object().execute_query()
    print(f"✓ Channel deleted: {channel.display_name}")


def _delegated_only(action: str, ex: ClientRequestException) -> None:
    """Channel email is a user-context (delegated) feature."""
    print(f"✗ {action} needs a delegated client ({ex.code})")
    print("  Graph rejects channel email provisioning in application-only context;")
    print("  sign in as a user to exercise these two commands.")


def cmd_provision_email(client: GraphClient, args: argparse.Namespace) -> None:
    team = _get_team(client, args.team_id)
    channel = _get_channel(team, args.channel_id)
    try:
        result = channel.provision_email().execute_query()
    except ClientRequestException as ex:
        _delegated_only("provision-email", ex)
        return
    print(f"✓ Email provisioned: {result.value}")


def cmd_remove_email(client: GraphClient, args: argparse.Namespace) -> None:
    team = _get_team(client, args.team_id)
    channel = _get_channel(team, args.channel_id)
    try:
        channel.remove_email().execute_query()
    except ClientRequestException as ex:
        _delegated_only("remove-email", ex)
        return
    print(f"✓ Email removed from: {channel.display_name}")


def cmd_primary(client: GraphClient, args: argparse.Namespace) -> None:
    team = _get_team(client, args.team_id)
    primary = team.primary_channel.get().execute_query()
    print(f"Primary channel: {primary.display_name} ({primary.id})")


def _add_team_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--team", dest="team_id", required=True, help="team id")


def _add_channel_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--channel", dest="channel_id", required=True, help="channel id")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage Teams channel lifecycle")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("list", help="list channels in a team")
    _add_team_arg(p)
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("create", help="create a channel")
    _add_team_arg(p)
    p.add_argument("--name", required=True, help="channel display name")
    p.add_argument(
        "--type",
        choices=sorted(MEMBERSHIP_TYPES),
        default="standard",
        help="membership type (set once, cannot be changed)",
    )
    p.add_argument("--description", default=None, help="optional channel description")
    p.set_defaults(func=cmd_create)

    p = sub.add_parser("update", help="update channel name or description")
    _add_team_arg(p)
    _add_channel_arg(p)
    p.add_argument("--name", default=None, help="new display name")
    p.add_argument("--description", default=None, help="new description")
    p.set_defaults(func=cmd_update)

    p = sub.add_parser("delete", help="delete a channel")
    _add_team_arg(p)
    _add_channel_arg(p)
    p.set_defaults(func=cmd_delete)

    p = sub.add_parser("provision-email", help="provision an email address for a channel")
    _add_team_arg(p)
    _add_channel_arg(p)
    p.set_defaults(func=cmd_provision_email)

    p = sub.add_parser("remove-email", help="remove a channel email address")
    _add_team_arg(p)
    _add_channel_arg(p)
    p.set_defaults(func=cmd_remove_email)

    p = sub.add_parser("primary", help="show the primary (General) channel")
    _add_team_arg(p)
    p.set_defaults(func=cmd_primary)

    return parser


def main():
    args = build_parser().parse_args()
    args.func(_client(), args)


if __name__ == "__main__":
    main()
