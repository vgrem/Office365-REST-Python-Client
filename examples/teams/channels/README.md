# Channels

A channel is where a team's work actually happens. Every team has a **General**
channel (its `primary` channel, which cannot be deleted); other channels are
created as needed. Messages are posted to a channel, and threaded **replies**
are supported only here (not in chats).

A channel's **membership type** — `standard`, `private` or `shared` — is fixed
at creation:

- **standard** — everyone in the team.
- **private** — a subset of the team.
- **shared** — members of *other* teams, added without making them guests.

```python
channel = team.channels.add("Project Falcon", description="Delivery").execute_query()
messages = channel.messages.get_all().top(20).execute_query()
print(channel.id, channel.membership_type, len(messages))
```

Two practical notes:

- **App-only creation of a private/shared channel needs an owner.** Pass
  `owners=[...]`; Graph returns `400` when a channel must have one and none is
  given.
- **Private/shared creation is asynchronous.** Graph answers `202 Accepted`
  with a `teamsAsyncOperation`; `ChannelCollection.add()` follows the operation
  and then `GET`s the finished channel, so `channel.id` is populated when
  `execute_query()` returns.

## Scripts

| Script | What it does |
|---|---|
| [`lifecycle.py`](./lifecycle.py) | `list` · `create` · `update` · `delete` · `primary` · channel email |
| [`messages.py`](./messages.py) | `send` · `reply` · `list` · per-channel activity digest |
| [`inventory.py`](./inventory.py) | Cross-team channel inventory (flags private/shared) |
| [`inactive.py`](./inactive.py) | Channels that have gone quiet |
| [`shared.py`](./shared.py) | Create a shared channel, share it, check access |

## Common commands

```bash
python lifecycle.py list   --team <id>
python lifecycle.py create --team <id> --name "Project Falcon" --membership private
python lifecycle.py update --team <id> --channel <id> --name "Falcon v2"
python lifecycle.py delete --team <id> --channel <id>

python messages.py list --team <id> --channel <id> --top 20
python messages.py digest --team <id>
python inventory.py
python inactive.py --days 90
```

## Permissions (application)

| Operation | Permissions |
|---|---|
| List channels | `Channel.ReadBasic.All`, `Team.ReadBasic.All` |
| Create | `Channel.Create` |
| Update / channel email | `ChannelSettings.ReadWrite.All` |
| Delete | `Channel.Delete.All` |
| Read messages | `ChannelMessage.Read.All` |
| Send messages | `ChannelMessage.Send.All` (or delegated `ChannelMessage.ReadWrite`) |
| Shared channels | `ChannelMember.Read.All` / `ReadWrite.All` |

Reading channel messages is fine app-only; **sending** is a user action, so the
`send`/`reply` commands print the missing scope instead of failing when only the
read-only application token is available. The same applies to shared-channel
membership (`ChannelMember.*`).

## Reference

- <https://learn.microsoft.com/en-us/graph/api/team-list-channels>
- <https://learn.microsoft.com/en-us/graph/api/channel-post>
- <https://learn.microsoft.com/en-us/graph/api/channel-list-messages>
- <https://learn.microsoft.com/en-us/graph/api/resources/channel?view=graph-rest-1.0#shared-channels>
