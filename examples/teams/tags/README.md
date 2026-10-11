# Tags

A **tag** is a named group of team members ("Designers", "On-call") that can be
`@mentioned` in a channel without typing every name. Tags are scoped to a team,
so they are a membership feature rather than a directory object.

```python
tag = team.tags.create(display_name="Designers").execute_query()
tag.members.add(user_id="<aad-user-id>").execute_query()
```

A tag member references the user by **AAD object id**, not UPN.

## Scripts

| Script | What it does |
|---|---|
| [`lifecycle.py`](./lifecycle.py) | `create` · `list` · `assign` · `unassign` · `members` · `delete` |
| [`report.py`](./report.py) | All tags across teams + teams without tags |

## Common commands

```bash
python lifecycle.py list   --team <id>
python lifecycle.py create --team <id> --name "Designers"
python lifecycle.py assign --team <id> --tag <tag-id> --user <user-id>
python lifecycle.py members --team <id> --tag <tag-id>
python lifecycle.py delete --team <id> --tag <tag-id>

python report.py
```

## Permissions (application or delegated)

| Operation | Permissions |
|---|---|
| List tags / members | `TeamworkTag.Read.All` |
| Create / assign / unassign / delete | `TeamworkTag.ReadWrite.All` |
| List teams | `Team.ReadBasic.All` |

## Reference

- <https://learn.microsoft.com/en-us/graph/api/teamworktag-post>
- <https://learn.microsoft.com/en-us/graph/api/teamworktagmember-post>
- <https://learn.microsoft.com/en-us/graph/api/teamworktag-list>
