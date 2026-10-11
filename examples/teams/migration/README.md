# Teams migration (export)

Back up Teams through the unified `MigrationJob` adapters — team structure,
members, channels, tabs, apps, messages (with replies and inline images), and
optionally channel files. The job is **resumable**: it persists what to copy (the
manifest) and what is done (the checkpoint), so `--resume` continues an
interrupted run. Import is planned next.

This is the heavier sibling of [`../export/`](../export/): use `export/` for a
quick inventory, and this toolkit when you need a portable, verifiable archive.

## Scripts

| Script | What it does |
|---|---|
| [`migrate/export_team.py`](./migrate/export_team.py) | Resumable team archive (structure, members, channels, messages, `--files`) |
| [`migrate/export_messages.py`](./migrate/export_messages.py) | Compliance message export via deferred collection adapters |

## Archive layout

```text
<output>/
  <team-id>/
    team.json                        # metadata, members, channels, tabs, apps
    messages.ndjson                  # one message/reply per line
    attachments/<channel>/<msg>_<content>.<ext>
    files/<channel>.zip              # --files
```

## Commands

```bash
# One team (repeat --team for several), with channel files
python migrate/export_team.py --team 00000000-0000-0000-0000-000000000000 --output /tmp/backup --files

# Every team in the tenant
python migrate/export_team.py --all --output /tmp/backup

# Resume an interrupted run (reloads the manifest + checkpoint)
python migrate/export_team.py --all --output /tmp/backup --resume

# Compliance message export (deferred collection adapters)
python migrate/export_messages.py --output /tmp/messages --team <team-id>
python migrate/export_messages.py --output /tmp/messages --user user@contoso.com
python migrate/export_messages.py --output /tmp/messages --tenant
python migrate/export_messages.py --output /tmp/messages --filter "createdDateTime gt 2024-01-01T00:00:00Z"
```

Channel-level members are **skipped by default** and included only with
`--channel-members`, because reading them needs `ChannelMember.Read.All`, which
many tenants do not consent. `export_messages.py` defaults to `--user`; `--team`
and `--tenant` need their own scopes, and the script explains the missing one
instead of crashing.

## Permissions (application)

| Scenario | Permissions |
|---|---|
| Structure, members, channels, tabs, apps | `Team.ReadBasic.All`, `TeamMember.Read.All` |
| Channel-level members (`--channel-members`) | `ChannelMember.Read.All` |
| Messages | `ChannelMessage.Read.All`, `Chat.Read.All`, `Teamwork.Migrate.All` |
| Channel files (`--files`) | `Files.Read.All`, `Sites.Read.All` |

## Library usage

```python
from pathlib import Path

from office365.graph_client import GraphClient
from office365.migration import MigrationJob
from office365.migration.teams import TeamsArchiveSource, TeamsArchiveTarget, TeamsExportOptions

client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)

out = Path("/tmp/backup")
job = MigrationJob(
    TeamsArchiveSource(client, ["00000000-..."], TeamsExportOptions(include_files=True)),
    TeamsArchiveTarget(out),
    manifest_path=out.with_name(out.name + ".manifest.json"),
    checkpoint_path=out.with_name(out.name + ".checkpoint.json"),
)
job.plan()
stats = job.run()
print(stats.summary(), job.verify().summary())

# Messages only — deferred collection adapters
with open("/tmp/messages.ndjson", "w") as f:
    client.teams.get_all_messages().filter("createdDateTime gt 2024-01-01T00:00:00Z").get_all().to_ndjson(
        f
    ).download_hosted_contents("/tmp/attachments").execute_query()
```

Pass **both** `manifest_path` and `checkpoint_path` for `resume()` to work: the
first restores *what to copy*, the second restores *what is done*.

## Reference

- <https://learn.microsoft.com/en-us/graph/api/team-list>
- <https://learn.microsoft.com/en-us/graph/api/channel-list-messages>
- <https://learn.microsoft.com/en-us/graph/api/resources/teamsasyncoperation>
