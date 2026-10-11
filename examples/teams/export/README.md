# Export & import

Flat-file tooling for onboarding and inventory: write the tenant out as CSV/JSON,
and create teams from a spreadsheet. For heavy, resumable team archiving (with
messages, tabs, apps and files), use [`../migration/`](../migration/) instead.

Everything here writes to the **temp directory** by default; pass `--output` to
choose a directory (the examples never write into the repository).

```python
for team in client.teams.get_all().select(["id", "displayName"]).execute_query():
    print(team.id, team.display_name)
```

## Scripts

| Script | What it does |
|---|---|
| [`inventory.py`](./inventory.py) | Export tenant inventory to CSV + JSON (with membership counts) |
| [`memberships.py`](./memberships.py) | One row per member: `team,displayName,email,roles` |
| [`provision.py`](./provision.py) | Bulk-provision teams from CSV via `create_and_wait` |

## Common commands

```bash
python inventory.py   --output /tmp/teams_inventory
python memberships.py --output /tmp/teams_memberships.csv

# Preview, then create
python provision.py --file teams.csv --dry-run
python provision.py --file teams.csv
```

Input CSV for `provision.py`:

```csv
name,description,template
Finance,"Budgeting and reporting",standard
Marketing,"Campaign workspace",standard
```

For concurrent provisioning of a large batch, use
[`../../patterns/async/provision_teams_async.py`](../../patterns/async/provision_teams_async.py).

## Permissions (application)

| Operation | Permissions |
|---|---|
| Inventory | `Team.ReadBasic.All`, `TeamMember.Read.All`, `Directory.Read.All` |
| Memberships | `TeamMember.Read.All` |
| Provision | `Group.ReadWrite.All`, `Team.Create` |

## Reference

- <https://learn.microsoft.com/en-us/graph/api/team-list>
- <https://learn.microsoft.com/en-us/graph/api/team-list-members>
- <https://learn.microsoft.com/en-us/graph/api/team-post>
