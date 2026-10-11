# Audit

Read-only reports for the questions a Teams administrator asks most often:
*who is in this tenant's teams, which teams are unused, and what did we lose?*

These scripts never change state — they only read and print. For anything that
touches teams, see [`../governance/`](../governance/), where destructive actions
are a dry run until `--apply` is passed.

## Scripts

| Script | What it does |
|---|---|
| [`inventory.py`](./inventory.py) | Tenant-wide inventory: owners, member/guest counts, visibility, archive state |
| [`empty.py`](./empty.py) | Teams with no channels, and channels that exist but are silent |
| [`lifecycle.py`](./lifecycle.py) | Archived teams and recently deleted (restorable) groups |

## Common commands

```bash
python inventory.py
python empty.py
python lifecycle.py
```

`empty.py` separates "no channels" (a failed provisioning) from "channels but no
messages" (possibly just seasonal), because the first is safe to delete and the
second is a judgement call.

## Permissions (application)

| Report | Permissions |
|---|---|
| Inventory | `Team.ReadBasic.All`, `TeamMember.Read.All` |
| Empty teams | `Team.ReadBasic.All`, `Channel.ReadBasic.All`, `ChannelMessage.Read.All` |
| Lifecycle | `Team.ReadBasic.All`, `Directory.Read.All` |

## Reference

- <https://learn.microsoft.com/en-us/graph/api/team-list>
- <https://learn.microsoft.com/en-us/graph/api/team-list-members>
- <https://learn.microsoft.com/en-us/graph/api/directory-deleteditems-list>
