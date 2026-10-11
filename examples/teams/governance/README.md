# Governance

Acting on what [`../audit/`](../audit/) reports: retire idle teams, and restore
or purge soft-deleted groups. Deletion in Microsoft 365 is a **soft delete** —
a group is restorable for 30 days, then permanently removed.

!!! warning "Dry run by default"
    `inactive.py` reports candidates by default. It only archives or deletes
    when you pass `--action` **and** `--apply`.

## Scripts

| Script | What it does |
|---|---|
| [`inactive.py`](./inactive.py) | Report / archive / delete teams idle ≥ `--days` (default 90) |
| [`restore.py`](./restore.py) | List, restore, or permanently delete a deleted group |

## Common commands

```bash
# Report candidates
python inactive.py

# Archive teams idle for 90+ days
python inactive.py --days 90 --action archive --apply

# Delete one specific team
python inactive.py --days 365 --action delete --apply --team "Old team"

# Recover a group deleted by mistake
python restore.py list
python restore.py restore --id <group-id>
python restore.py purge   --id <group-id>
```

A team counts as inactive when it has no messages within `--days`; a team with
no messages at all counts as inactive from the start.

## Permissions (application)

| Operation | Permissions |
|---|---|
| Detect inactivity | `Team.ReadBasic.All`, `ChannelMessage.Read.All` |
| Archive / delete | `Group.ReadWrite.All`, `Team.ReadWrite.All` |
| List / restore deleted groups | `Directory.Read.All`, `Directory.ReadWrite.All` |

## Reference

- <https://learn.microsoft.com/en-us/graph/api/team-archive>
- <https://learn.microsoft.com/en-us/graph/api/group-delete>
- <https://learn.microsoft.com/en-us/graph/api/directory-deleteditems-list>
- <https://learn.microsoft.com/en-us/graph/api/directory-deleteditems-restore>
