"""
Teamwork tags management.

Create tags, assign or unassign users, and delete tags.

Tags let users @mention a named group (e.g. "Designers") in a channel
without typing every name.

Requires delegated or application permissions:
    TeamworkTag.Read.All      List tags and members
    TeamworkTag.ReadWrite.All Create, assign, delete tags

https://learn.microsoft.com/en-us/graph/api/teamworktag-post
https://learn.microsoft.com/en-us/graph/api/teamworktagmember-post
"""

import argparse
import sys

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from office365.teams.team import Team
from office365.teams.teamwork.tags.tag import TeamworkTag
from tests.settings import client_id, client_secret, tenant


def _client() -> GraphClient:
    return GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)


def _get_team(client: GraphClient, team_id: str) -> Team:
    team = client.teams[team_id].get().execute_query()
    if team is None:
        sys.exit(f"Team not found: {team_id}")
    return team


def _get_tag(team: Team, tag_id: str) -> TeamworkTag:
    tag = team.tags[tag_id].get().execute_query()
    if tag is None:
        sys.exit(f"Tag not found: {tag_id}")
    return tag


def _resolve_user(client: GraphClient, user_ref: str):
    user = client.users[user_ref].get().execute_query()
    if user is None:
        sys.exit(f"User not found: {user_ref}")
    return user


def cmd_list(client: GraphClient, args: argparse.Namespace) -> None:
    team = _get_team(client, args.team_id)
    tags = team.tags.get().execute_query()
    print(f"Tags in '{team.display_name}' ({len(tags)}):")
    for tag in tags:
        print(f"  {tag.id:50s} {tag.display_name or '(unnamed)':25s} members={tag.member_count or 0}")


def cmd_create(client: GraphClient, args: argparse.Namespace) -> None:
    team = _get_team(client, args.team_id)
    tag = team.tags.add(displayName=args.name, description=args.description).execute_query()
    print(f"✓ Tag created: {tag.display_name} ({tag.id})")


def cmd_members(client: GraphClient, args: argparse.Namespace) -> None:
    team = _get_team(client, args.team_id)
    tag = _get_tag(team, args.tag_id)
    members = tag.members.get().execute_query()
    print(f"Members of tag '{tag.display_name}' ({len(members)}):")
    for member in members:
        print(f"  {member.id:50s} {member.display_name or '?'}")


def cmd_assign(client: GraphClient, args: argparse.Namespace) -> None:
    team = _get_team(client, args.team_id)
    tag = _get_tag(team, args.tag_id)
    user = _resolve_user(client, args.user)
    member = tag.members.add(userId=user.id).execute_query()
    print(f"✓ {user.display_name} assigned to tag '{tag.display_name}' ({member.id})")


def cmd_unassign(client: GraphClient, args: argparse.Namespace) -> None:
    team = _get_team(client, args.team_id)
    tag = _get_tag(team, args.tag_id)
    tag.members[args.member_id].delete_object().execute_query()
    print(f"✓ Member removed from tag '{tag.display_name}': {args.member_id}")


def cmd_delete(client: GraphClient, args: argparse.Namespace) -> None:
    team = _get_team(client, args.team_id)
    tag = _get_tag(team, args.tag_id)
    tag.delete_object().execute_query()
    print(f"✓ Tag deleted: {tag.display_name}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage teamwork tags")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("list", help="list tags in a team")
    p.add_argument("--team", dest="team_id", required=True, help="team id")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("create", help="create a tag")
    p.add_argument("--team", dest="team_id", required=True, help="team id")
    p.add_argument("--name", required=True, help="tag display name")
    p.add_argument("--description", default=None, help="tag description")
    p.set_defaults(func=cmd_create)

    p = sub.add_parser("members", help="list users assigned to a tag")
    p.add_argument("--team", dest="team_id", required=True, help="team id")
    p.add_argument("--tag", dest="tag_id", required=True, help="tag id")
    p.set_defaults(func=cmd_members)

    p = sub.add_parser("assign", help="assign a user to a tag")
    p.add_argument("--team", dest="team_id", required=True, help="team id")
    p.add_argument("--tag", dest="tag_id", required=True, help="tag id")
    p.add_argument("--user", required=True, help="user id or UPN")
    p.set_defaults(func=cmd_assign)

    p = sub.add_parser("unassign", help="remove a user from a tag")
    p.add_argument("--team", dest="team_id", required=True, help="team id")
    p.add_argument("--tag", dest="tag_id", required=True, help="tag id")
    p.add_argument("--member-id", required=True, help="tag member id (see 'members')")
    p.set_defaults(func=cmd_unassign)

    p = sub.add_parser("delete", help="delete a tag")
    p.add_argument("--team", dest="team_id", required=True, help="team id")
    p.add_argument("--tag", dest="tag_id", required=True, help="tag id")
    p.set_defaults(func=cmd_delete)

    return parser


def main():
    args = build_parser().parse_args()
    try:
        args.func(_client(), args)
    except ClientRequestException as ex:
        if ex.code != "Forbidden":
            raise
        print(f"✗ Tags are not readable/writable with this app ({ex.code})")
        print("  Grant TeamworkTag.ReadWrite.All (application), or the")
        print("  TeamworkTag.ReadWrite.Group resource-specific consent, then re-run.")


if __name__ == "__main__":
    main()
