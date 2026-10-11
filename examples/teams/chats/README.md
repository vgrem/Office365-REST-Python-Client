# Chats

Chats look like channels but are **not** under a team. They are first-class,
user-relative resources — `client.users["...@"].chats` — and come in three
flavours:

| Flavour | `chat_type` | Notes |
|---|---|---|
| One-on-one | `oneOnOne` | Exactly two members, no topic |
| Group | `group` | A topic is mandatory |
| Meeting | `meeting` | Created from an online meeting, not by hand |

Like channels, chats have messages and members. Unlike channels, a chat has no
`primary` channel and **no threaded replies** — chat messages are flat. Chat
commands run as the signed-in user by default; pass `--app-only` for the
application credentials.

```python
chat = (
    client.users["user@contoso.com"]
    .chats.add(chat_type="group", owner_ids=[user_id], topic="Project Falcon")
    .execute_query()
)
for message in chat.messages.get_all().execute_query():
    print(message.created_date_time, message.from_ and message.from_.user.display_name)
```

## Scripts

| Script | What it does |
|---|---|
| [`inventory.py`](./inventory.py) | A user's chats by type, with member count and last activity |
| [`lifecycle.py`](./lifecycle.py) | `create-one-on-one` · `create-group` · `members` · `add-member` · `delete` |
| [`messages.py`](./messages.py) | `send` · `list` · `export` · activity digest |

## Common commands

```bash
python inventory.py --user user@contoso.com
python inventory.py --app-only --user user@contoso.com

python lifecycle.py create-group --user user@contoso.com \
    --member other@contoso.com --topic "Project Falcon"
python lifecycle.py members --user user@contoso.com --chat <id>

python messages.py list --user user@contoso.com --chat <id>
python messages.py send --user user@contoso.com --chat <id> --text "Hello"
python messages.py export --user user@contoso.com --chat <id> --output /tmp/chat.ndjson
```

`--app-only` reads any user's chats with `Chat.Read.All`; a delegated client can
only read its own.

## Permissions

| Operation | Application | Delegated |
|---|---|---|
| Read chats | `Chat.ReadBasic.All`, `Chat.Read.All` | `Chat.ReadBasic`, `Chat.Read` |
| Create / send / manage | `Chat.ReadWrite.All`, `Chat.Create` | `Chat.ReadWrite`, `Chat.Create` |
| Delete a chat | `Chat.ManageDeletion.All` | — |

## Reference

- <https://learn.microsoft.com/en-us/graph/api/chat-list>
- <https://learn.microsoft.com/en-us/graph/api/chat-post>
- <https://learn.microsoft.com/en-us/graph/api/chatmessage-list>
- <https://learn.microsoft.com/en-us/graph/api/chatmessage-post>
