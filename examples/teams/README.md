# Microsoft Teams

Practical, operationally-named examples for the Teams lifecycle — administration,
governance, management, cleanup, and bulk export/import. All scripts are flat in
this folder and follow console-print style.

> Note: team creation in Graph is **asynchronous**. Use
> `client.teams.create_and_wait(name).execute_query()` (waits and loads the team)
> or `client.teams.create(name).execute_query()` and poll the returned
> `TeamsAsyncOperation` yourself.

## Administration & lifecycle

| Script | What it does |
|---|---|
| [`teams_lifecycle.py`](./teams_lifecycle.py) | Create, update settings, archive/unarchive, and delete a team |
| [`prune_inactive_teams.py`](./prune_inactive_teams.py) | Report, archive, or delete teams idle >= `--days` (default 180); dry-run by default (`--apply`) |
| [`import_teams.py`](./import_teams.py) | Bulk-provision teams from a CSV (`name,description?,template?`) via `create_and_wait` |
| [`../patterns/async/provision_teams_async.py`](../patterns/async/provision_teams_async.py) | Provision many teams concurrently (create/clone, bounded parallel polling) — async twin of `import_teams.py` |
| [`wait_for_clone.py`](./wait_for_clone.py) | Clone a team and wait for the `teamsAsyncOperation` to finish |
| [`export_teams.py`](./export_teams.py) | Export the tenant Teams inventory to CSV/JSON (owners/members/guests counts) |
| [`members_lifecycle.py`](./members_lifecycle.py) | Add/remove team members and owners |
| [`teams_export_membership.py`](./teams_export_membership.py) | Export all team memberships to CSV |

```bash
python prune_inactive_teams.py                 # candidates idle >= 180 days
python prune_inactive_teams.py --days 90 --action archive --apply
python import_teams.py --file teams.csv
python export_teams.py --output /tmp
```

## Migration (export)

| Script | What it does |
|---|---|
| [`migration/migrate/export_team.py`](./migration/migrate/export_team.py) | Resumable team archive via `MigrationJob` adapters: structure, members, channels, tabs, apps, messages, inline images (`--files` adds channel files) |
| [`migration/migrate/export_messages.py`](./migration/migrate/export_messages.py) | Compliance message export via deferred collection adapters (`to_ndjson` + `download_hosted_contents`) |

See [`migration/README.md`](./migration/README.md) for the archive layout and permissions.

## Audit & governance

| Script | What it does |
|---|---|
| [`teams_inventory.py`](./teams_inventory.py) | Tenant-wide report: owners, member/guest counts, visibility, archive state |
| [`teams_settings_audit.py`](./teams_settings_audit.py) | Scan team settings for policy compliance |
| [`teams_guest_audit.py`](./teams_guest_audit.py) | Find all teams with external guest users |
| [`teams_lifecycle_audit.py`](./teams_lifecycle_audit.py) | Lifecycle report: archived and recently deleted teams |
| [`teams_orphan_owners.py`](./teams_orphan_owners.py) | Teams without owners (orphaned) |
| [`find_empty_teams.py`](./find_empty_teams.py) | Cleanup candidates: teams with no channels or no messages |
| [`find_excessive_admins.py`](./find_excessive_admins.py) | Security risk: teams with too many owners |
| [`archive_inactive_teams.py`](./archive_inactive_teams.py) | Report archiving candidates (inactive teams) |
| [`channels_inactive.py`](./channels_inactive.py) | Inactive channels based on last message date |
| [`restore_deleted_team.py`](./restore_deleted_team.py) | List, restore, or permanently delete deleted groups/teams |

## Apps & tags

| Script | What it does |
|---|---|
| [`apps_catalog.py`](./apps_catalog.py) | Inventory of the tenant Teams app catalog |
| [`apps_installed.py`](./apps_installed.py) | App adoption across all teams |
| [`apps_lifecycle.py`](./apps_lifecycle.py) | Install, uninstall, and inspect apps in a team |
| [`apps_tabs.py`](./apps_tabs.py) | Pinned apps/tabs across all teams |
| [`tags_lifecycle.py`](./tags_lifecycle.py) | Create, update, and delete teamwork tags |
| [`tags_report.py`](./tags_report.py) | All tags across teams (member counts, teams without tags) |

## Channels & chats

| Script | What it does |
|---|---|
| [`channels_inventory.py`](./channels_inventory.py) | Cross-team channel inventory and audit |
| [`channels_lifecycle.py`](./channels_lifecycle.py) | Channel lifecycle: create, update, delete, channel email |
| [`channels_messages.py`](./channels_messages.py) | Channel messaging: send, reply, list, team-wide activity digest |
| [`channels_shared.py`](./channels_shared.py) | Shared channels: create, share with another team, verify access |
| [`chats_inventory.py`](./chats_inventory.py) | A user's chats (list/pagination) |
| [`chats_lifecycle.py`](./chats_lifecycle.py) | Create and manage chats |
| [`chats_messages.py`](./chats_messages.py) | Chat messaging: send, reply, list, export, digest |

## Meetings & analytics

| Script | What it does |
|---|---|
| [`online_meetings.py`](./online_meetings.py) | Create online meetings with join links |
| [`usage_report.py`](./usage_report.py) | Team counts and user activity over periods |
| [`call_records.py`](./call_records.py) | Teams call quality analytics |

## Typical workflow (bulk onboarding → governance → cleanup)

```python
from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant

client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)

# provision (async + wait for readiness)
team = client.teams.create_and_wait("Finance", "Budgeting and reporting").execute_query()
print(team.id, team.display_name)

# ...later, governance...
# prune_inactive_teams.py --days 180 --action archive --apply
# export_teams.py --output /tmp
```
