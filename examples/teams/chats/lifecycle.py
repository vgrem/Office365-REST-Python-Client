"""
Create and manage chats.

Covers the common chat lifecycle:
  create-one-on-one   Create a 1:1 chat between two users
  create-group        Create a group chat with a topic
  members             List chat members
  add-member          Add a member to a chat
  delete              Delete a chat

Use --app-only for application context; chat commands run as the signed-in
user (delegated) by default.

Requires delegated or application permissions ``Chat.Create``,
``Chat.ReadWrite.All``.

https://learn.microsoft.com/en-us/graph/api/chat-post
"""

import argparse
import sys
from typing import List

from office365.directory.users.user import User
from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from office365.teams.chats.type import ChatType
from tests.settings import client_id, client_secret, password, tenant, username

MIN_GROUP_MEMBERS = 2


def _client(app_only: bool = False) -> GraphClient:
    if app_only:
        return GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    return GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)


def _resolve_user(client: GraphClient, user_ref: str) -> User:
    user = client.users[user_ref].get().execute_query()
    if user is None:
        sys.exit(f"User not found: {user_ref}")
    return user


def _resolve_users(client: GraphClient, refs) -> List[User]:
    users = []
    for ref in refs:
        users.append(_resolve_user(client, ref))
    return users


def cmd_create_one_on_one(client: GraphClient, args: argparse.Namespace) -> None:
    user1 = _resolve_user(client, args.user1)
    user2 = _resolve_user(client, args.user2)
    if not user1.id or not user2.id:
        sys.exit("Could not resolve user ids.")
    chat = client.chats.add(ChatType.oneOnOne, owner_ids=[user1.id, user2.id]).execute_query()
    print(f"✓ 1:1 chat created: {chat.id}")


def cmd_create_group(client: GraphClient, args: argparse.Namespace) -> None:
    members = _resolve_users(client, args.members)
    if len(members) < MIN_GROUP_MEMBERS:
        sys.exit(f"A group chat needs at least {MIN_GROUP_MEMBERS} members.")
    owner_ids = [m.id for m in members if m.id]
    chat = client.chats.add(ChatType.group, owner_ids=owner_ids, topic=args.topic).execute_query()
    print(f"✓ Group chat created: {chat.id}  topic={chat.topic or '-'}")


def cmd_members(client: GraphClient, args: argparse.Namespace) -> None:
    chat = client.chats[args.chat_id].get().execute_query()
    members = chat.members.get().execute_query()
    print(f"Members of chat {args.chat_id} ({len(members)}):")
    for member in members:
        email = member.properties.get("email", "-")
        roles = ", ".join(member.roles) if member.roles else "-"
        print(f"  {member.display_name or '?':25s} {email:40s} roles=[{roles}]")


def cmd_add_member(client: GraphClient, args: argparse.Namespace) -> None:
    chat = client.chats[args.chat_id].get().execute_query()
    user = _resolve_user(client, args.user)
    chat.members.add(user=user, roles=[args.role]).execute_query()
    print(f"✓ {user.display_name} added to chat {args.chat_id} as {args.role}")


def cmd_delete(client: GraphClient, args: argparse.Namespace) -> None:
    chat = client.chats[args.chat_id].get().execute_query()
    try:
        chat.delete_object().execute_query_retry()
    except ClientRequestException as ex:
        print(f"✗ Deleting a chat requires the Chat.ManageDeletion.All scope ({ex.code}).")
        return
    print(f"✓ Chat deleted: {args.chat_id}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage Teams chats")
    parser.add_argument("--app-only", action="store_true", help="app-only credentials (default: signed-in user)")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("create-one-on-one", help="create a 1:1 chat")
    p.add_argument("--user1", required=True, help="first user id or UPN")
    p.add_argument("--user2", required=True, help="second user id or UPN")
    p.set_defaults(func=cmd_create_one_on_one)

    p = sub.add_parser("create-group", help="create a group chat")
    p.add_argument("--members", nargs="+", required=True, help="user ids or UPNs (at least two)")
    p.add_argument("--topic", default=None, help="group chat topic")
    p.set_defaults(func=cmd_create_group)

    p = sub.add_parser("members", help="list chat members")
    p.add_argument("--chat", dest="chat_id", required=True, help="chat id")
    p.set_defaults(func=cmd_members)

    p = sub.add_parser("add-member", help="add a member to a chat")
    p.add_argument("--chat", dest="chat_id", required=True, help="chat id")
    p.add_argument("--user", required=True, help="user id or UPN")
    p.add_argument("--role", default="owner", help="member role: owner or guest (default owner)")
    p.set_defaults(func=cmd_add_member)

    p = sub.add_parser("delete", help="delete a chat")
    p.add_argument("--chat", dest="chat_id", required=True, help="chat id")
    p.set_defaults(func=cmd_delete)

    return parser


def main():
    args = build_parser().parse_args()
    args.func(_client(args.app_only), args)


if __name__ == "__main__":
    main()
