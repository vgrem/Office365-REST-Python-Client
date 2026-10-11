"""
Team lifecycle and settings management.

Covers the most common team administration operations:
  create       Create a team (standard template, async)
  update       Rename or re-describe a team
  settings     Toggle fun / member / messaging / guest settings
  archive      Archive a team
  unarchive    Restore an archived team
  delete       Delete a team

Requires delegated or application permissions:
    Team.Create               Create teams
    TeamSettings.ReadWrite.All Update teams and settings
    Team.ReadWrite.All         Archive / unarchive
    Directory.ReadWrite.All    Delete teams

https://learn.microsoft.com/en-us/graph/api/team-post
https://learn.microsoft.com/en-us/graph/api/team-archive
"""

import argparse
import sys
import time

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from office365.teams.fun_settings import TeamFunSettings
from office365.teams.guest_settings import TeamGuestSettings
from office365.teams.members.settings import TeamMemberSettings
from office365.teams.messaging_settings import TeamMessagingSettings
from office365.teams.team import Team
from tests.settings import client_id, client_secret, tenant, user_principal


def _client() -> GraphClient:
    return GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)


def _get_team(client: GraphClient, team_id: str) -> Team:
    team = client.teams[team_id].get().execute_query()
    if team is None:
        sys.exit(f"Team not found: {team_id}")
    return team


def _apply_team_update(operation, attempts: int = 3, delay: int = 20) -> None:
    """Run an archive/unarchive operation, retrying Teams' serialized team updates."""
    for attempt in range(1, attempts + 1):
        try:
            operation().execute_query()
            return
        except ClientRequestException as ex:
            if "Another update to this team is ongoing" not in str(ex) or attempt == attempts:
                raise
            print(f"  Team update still in progress, retrying in {delay}s ({attempt}/{attempts - 1})...")
            time.sleep(delay)


def cmd_create(client: GraphClient, args: argparse.Namespace) -> None:
    team = client.teams.create_and_wait(args.name, args.description, owners=[args.owner]).execute_query()
    print(f"✓ Team created: {team.display_name} ({team.id})")


def cmd_update(client: GraphClient, args: argparse.Namespace) -> None:
    team = _get_team(client, args.team_id)
    if args.name:
        team.set_property("displayName", args.name)
    if args.description is not None:
        team.set_property("description", args.description)
    if args.classification is not None:
        team.set_property("classification", args.classification)
    team.update().execute_query()
    print(f"✓ Team updated: {team.display_name}")


def cmd_settings(client: GraphClient, args: argparse.Namespace) -> None:
    team = _get_team(client, args.team_id)
    updated = False

    fun = {}
    if args.allow_giphy is not None:
        fun["allowGiphy"] = args.allow_giphy
    if args.allow_stickers is not None:
        fun["allowStickersAndMemes"] = args.allow_stickers
    if fun:
        team.set_property("funSettings", TeamFunSettings(**fun))
        updated = True

    member = {}
    if args.allow_create_update_channels is not None:
        member["allowCreateUpdateChannels"] = args.allow_create_update_channels
    if args.allow_delete_channels is not None:
        member["allowDeleteChannels"] = args.allow_delete_channels
    if member:
        team.set_property("memberSettings", TeamMemberSettings(**member))
        updated = True

    messaging = {}
    if args.allow_user_edit_messages is not None:
        messaging["allowUserEditMessages"] = args.allow_user_edit_messages
    if args.allow_user_delete_messages is not None:
        messaging["allowUserDeleteMessages"] = args.allow_user_delete_messages
    if args.allow_user_chat is not None:
        messaging["allowUserChat"] = args.allow_user_chat
    if messaging:
        team.set_property("messagingSettings", TeamMessagingSettings(**messaging))
        updated = True

    guest = {}
    if args.guest_create_update_channels is not None:
        guest["allowCreateUpdateChannels"] = args.guest_create_update_channels
    if args.guest_delete_channels is not None:
        guest["allowDeleteChannels"] = args.guest_delete_channels
    if guest:
        team.set_property("guestSettings", TeamGuestSettings(**guest))
        updated = True

    if not updated:
        sys.exit("No settings provided. Pass at least one --allow-*/--guest-* flag.")
    team.update().execute_query()
    print(f"✓ Team settings updated: {team.display_name}")


def cmd_archive(client: GraphClient, args: argparse.Namespace) -> None:
    team = _get_team(client, args.team_id)
    _apply_team_update(team.archive)
    print(f"✓ Team archived: {team.display_name}")


def cmd_unarchive(client: GraphClient, args: argparse.Namespace) -> None:
    team = _get_team(client, args.team_id)
    _apply_team_update(team.unarchive)
    print(f"✓ Team unarchived: {team.display_name}")


def cmd_delete(client: GraphClient, args: argparse.Namespace) -> None:
    team = _get_team(client, args.team_id)
    team.delete_object(permanent_delete=args.permanent).execute_query()
    verb = "permanently deleted" if args.permanent else "deleted"
    print(f"✓ Team {verb}: {team.display_name}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage Teams lifecycle and settings")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("create", help="create a team (standard template)")
    p.add_argument("--name", required=True, help="team display name")
    p.add_argument("--description", default=None, help="team description")
    p.add_argument(
        "--owner",
        default=user_principal,
        help="UPN or id of the owning user (required in application context)",
    )
    p.set_defaults(func=cmd_create)

    p = sub.add_parser("update", help="update team name, description, or classification")
    p.add_argument("--team", dest="team_id", required=True, help="team id")
    p.add_argument("--name", default=None, help="new display name")
    p.add_argument("--description", default=None, help="new description")
    p.add_argument("--classification", default=None, help="new classification")
    p.set_defaults(func=cmd_update)

    p = sub.add_parser("settings", help="toggle team settings")
    p.add_argument("--team", dest="team_id", required=True, help="team id")
    p.add_argument(
        "--allow-giphy", action=argparse.BooleanOptionalAction, default=None, help="allow Giphy in fun settings"
    )
    p.add_argument(
        "--allow-stickers", action=argparse.BooleanOptionalAction, default=None, help="allow stickers and memes"
    )
    p.add_argument(
        "--allow-create-update-channels",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="members may create/update channels",
    )
    p.add_argument(
        "--allow-delete-channels",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="members may delete channels",
    )
    p.add_argument(
        "--allow-user-edit-messages",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="members may edit messages",
    )
    p.add_argument(
        "--allow-user-delete-messages",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="members may delete messages",
    )
    p.add_argument("--allow-user-chat", action=argparse.BooleanOptionalAction, default=None, help="members may chat")
    p.add_argument(
        "--guest-create-update-channels",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="guests may create/update channels",
    )
    p.add_argument(
        "--guest-delete-channels", action=argparse.BooleanOptionalAction, default=None, help="guests may delete channels"
    )
    p.set_defaults(func=cmd_settings)

    p = sub.add_parser("archive", help="archive a team")
    p.add_argument("--team", dest="team_id", required=True, help="team id")
    p.set_defaults(func=cmd_archive)

    p = sub.add_parser("unarchive", help="restore an archived team")
    p.add_argument("--team", dest="team_id", required=True, help="team id")
    p.set_defaults(func=cmd_unarchive)

    p = sub.add_parser("delete", help="delete a team")
    p.add_argument("--team", dest="team_id", required=True, help="team id")
    p.add_argument("--permanent", action="store_true", help="permanently delete (no recycle bin)")
    p.set_defaults(func=cmd_delete)

    return parser


def main():
    args = build_parser().parse_args()
    args.func(_client(), args)


if __name__ == "__main__":
    main()
