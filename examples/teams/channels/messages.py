"""
Channel messaging: send, reply, list, and a team-wide activity digest.

The digest subcommand summarizes the most recent message activity per
channel, useful for spotting active vs stale channels.

Reading messages needs the application permission ``ChannelMessage.Read.All``.
Posting is a user action: Graph requires ``ChannelMessage.Send.All``
(application) or a delegated client granted ``ChannelMessage.ReadWrite``, so
``send``/``reply`` explain the missing scope instead of failing when the
read-only application token is used.

https://learn.microsoft.com/en-us/graph/api/channel-list-messages
"""

import argparse
from datetime import datetime, timezone

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from office365.teams.chats.messages.message import ChatMessage
from office365.teams.team import Team
from tests.settings import client_id, client_secret, tenant


def _client() -> GraphClient:
    return GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)


def _get_team(client: GraphClient, team_id: str) -> Team:
    return client.teams[team_id].get().execute_query()


def _get_channel(team: Team, channel_id: str):
    return team.channels[channel_id].get().execute_query()


def _fmt_author(message: ChatMessage) -> str:
    sender = message.from_
    user = sender.user if sender else None
    return str(user.displayName or "?") if user else "?"


def _fmt_time(dt) -> str:
    if isinstance(dt, datetime):
        return dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M")
    return str(dt or "?")


def _explain_write_failure(action: str, ex: ClientRequestException) -> None:
    """Posting messages needs a write scope the read-only app token lacks."""
    print(f"✗ Could not {action} the message ({ex.code})")
    print("  Graph requires ChannelMessage.Send.All (application) or a delegated")
    print("  client granted ChannelMessage.ReadWrite — the app registration used here")
    print("  only has ChannelMessage.Read.All. Reading with 'list'/'digest' works.")


def cmd_send(client: GraphClient, args: argparse.Namespace) -> None:
    team = _get_team(client, args.team_id)
    channel = _get_channel(team, args.channel_id)
    try:
        message = channel.messages.add(args.content).execute_query()
    except ClientRequestException as ex:
        _explain_write_failure("send", ex)
        return
    print(f"✓ Message sent to '{channel.display_name}': {message.id}")


def cmd_reply(client: GraphClient, args: argparse.Namespace) -> None:
    team = _get_team(client, args.team_id)
    channel = _get_channel(team, args.channel_id)
    message = channel.messages[args.message_id]
    try:
        reply = message.replies.add(args.content).execute_query()
    except ClientRequestException as ex:
        _explain_write_failure("reply to", ex)
        return
    print(f"✓ Reply added: {reply.id}")


def cmd_list(client: GraphClient, args: argparse.Namespace) -> None:
    team = _get_team(client, args.team_id)
    channel = _get_channel(team, args.channel_id)
    messages = channel.messages.order_by("createdDateTime desc").top(args.top).get().execute_query()
    print(f"Recent messages in '{channel.display_name}' ({len(messages)}):")
    for message in messages:
        preview = (message.body.content or "").replace("\n", " ")[:70]
        print(f"  {_fmt_time(message.created_datetime)}  {_fmt_author(message):20s}  {preview}")


def cmd_digest(client: GraphClient, args: argparse.Namespace) -> None:
    team = _get_team(client, args.team_id)
    channels = team.channels.get().execute_query()
    print(f"Channel activity digest for '{team.display_name}' ({len(channels)} channels):")
    for channel in channels:
        messages = channel.messages.top(args.limit).get().execute_query()
        if not messages:
            print(f"  {channel.display_name or '(unnamed)':30s} no messages")
            continue
        latest = messages[0]
        print(
            f"  {channel.display_name or '(unnamed)':30s} {len(messages):3d} recent  "
            f"last={_fmt_time(latest.created_datetime)}  by {_fmt_author(latest)}"
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Channel messaging and activity")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("send", help="send a message to a channel")
    p.add_argument("--team", dest="team_id", required=True, help="team id")
    p.add_argument("--channel", dest="channel_id", required=True, help="channel id")
    p.add_argument("--content", required=True, help="message text")
    p.set_defaults(func=cmd_send)

    p = sub.add_parser("reply", help="reply to a channel message")
    p.add_argument("--team", dest="team_id", required=True, help="team id")
    p.add_argument("--channel", dest="channel_id", required=True, help="channel id")
    p.add_argument("--message", dest="message_id", required=True, help="message id to reply to")
    p.add_argument("--content", required=True, help="reply text")
    p.set_defaults(func=cmd_reply)

    p = sub.add_parser("list", help="list recent messages in a channel")
    p.add_argument("--team", dest="team_id", required=True, help="team id")
    p.add_argument("--channel", dest="channel_id", required=True, help="channel id")
    p.add_argument("--top", type=int, default=10, help="number of messages (default 10)")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("digest", help="recent activity per channel in a team")
    p.add_argument("--team", dest="team_id", required=True, help="team id")
    p.add_argument("--limit", type=int, default=1, help="recent messages considered per channel (default 1)")
    p.set_defaults(func=cmd_digest)

    return parser


def main():
    args = build_parser().parse_args()
    args.func(_client(), args)


if __name__ == "__main__":
    main()
