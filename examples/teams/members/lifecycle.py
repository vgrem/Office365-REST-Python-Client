"""
Team membership management.

Add, remove, and re-role team members (owners / members).

Requires delegated or application permissions:
    TeamMember.Read.All     List members
    TeamMember.ReadWrite.All Add, re-role, remove members

https://learn.microsoft.com/en-us/graph/api/team-list-members
https://learn.microsoft.com/en-us/graph/api/conversationmember-add
"""

import argparse
import sys

from office365.graph_client import GraphClient
from office365.teams.team import Team
from tests.settings import client_id, client_secret, tenant

ROLES = {"owner", "member", "guest"}


def _client() -> GraphClient:
    return GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)


def _get_team(client: GraphClient, team_id: str) -> Team:
    team = client.teams[team_id].get().execute_query()
    if team is None:
        sys.exit(f"Team not found: {team_id}")
    return team


def _resolve_user(client: GraphClient, user_ref: str):
    user = client.users[user_ref].get().execute_query()
    if user is None:
        sys.exit(f"User not found: {user_ref}")
    return user


def cmd_list(client: GraphClient, args: argparse.Namespace) -> None:
    team = _get_team(client, args.team_id)
    members = team.members.get().execute_query()
    print(f"Members of '{team.display_name}' ({len(members)}):")
    for member in members:
        roles = ", ".join(member.roles) if member.roles else "-"
        email = member.properties.get("email", "-")
        print(f"  {member.id:50s} {member.display_name or '?':25s} {email:40s} roles=[{roles}]")


def cmd_add(client: GraphClient, args: argparse.Namespace) -> None:
    team = _get_team(client, args.team_id)
    user = _resolve_user(client, args.upn)
    member = team.members.add(user=user, roles=[args.role]).execute_query()
    print(f"✓ {user.display_name} added to '{team.display_name}' as {args.role} ({member.id})")


def cmd_set_role(client: GraphClient, args: argparse.Namespace) -> None:
    team = _get_team(client, args.team_id)
    member = team.members[args.member_id]
    member.set_property("roles", [args.role]).update().execute_query()
    print(f"✓ Member role set to '{args.role}': {args.member_id}")


def cmd_remove(client: GraphClient, args: argparse.Namespace) -> None:
    team = _get_team(client, args.team_id)
    member = team.members[args.member_id]
    member.delete_object().execute_query()
    print(f"✓ Member removed from '{team.display_name}': {args.member_id}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage team members")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("list", help="list team members")
    p.add_argument("--team", dest="team_id", required=True, help="team id")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("add", help="add a member (or owner) by UPN")
    p.add_argument("--team", dest="team_id", required=True, help="team id")
    p.add_argument("--upn", required=True, help="user principal name")
    p.add_argument("--role", choices=sorted(ROLES), default="member", help="role to assign (default member)")
    p.set_defaults(func=cmd_add)

    p = sub.add_parser("set-role", help="change a member's role")
    p.add_argument("--team", dest="team_id", required=True, help="team id")
    p.add_argument("--member-id", required=True, help="member id (see 'list')")
    p.add_argument("--role", choices=sorted(ROLES), required=True, help="new role")
    p.set_defaults(func=cmd_set_role)

    p = sub.add_parser("remove", help="remove a member")
    p.add_argument("--team", dest="team_id", required=True, help="team id")
    p.add_argument("--member-id", required=True, help="member id (see 'list')")
    p.set_defaults(func=cmd_remove)

    return parser


def main():
    args = build_parser().parse_args()
    args.func(_client(), args)


if __name__ == "__main__":
    main()
