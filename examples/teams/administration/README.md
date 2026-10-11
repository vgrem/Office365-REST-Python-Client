# Teams administration

Creating, configuring, archiving and deleting teams — the operations an admin
runs on a team as a whole. Teams creation is the one part of the Teams API that
is genuinely asynchronous: Graph accepts the request, returns a
`teamsAsyncOperation`, and the team exists only once that operation reaches
`succeeded`.

`create_and_wait()` wraps the whole dance — submit, poll, final `GET` — so one
`execute_query()` gives you a provisioned team.

```python
team = client.teams.create_and_wait(
    display_name="Finance",
    description="Budgeting and reporting",
    owners=["owner@contoso.com"],  # required when creating app-only
).execute_query()
print(team.id, team.display_name)
```

## Scripts

| Script | What it does |
|---|---|
| [`lifecycle.py`](./lifecycle.py) | `create` · `update` · `settings` · `archive` · `unarchive` · `delete` |
| [`clone.py`](./clone.py) | Clone a team (`clone_and_wait`) — copies the structure you select |
| [`settings_audit.py`](./settings_audit.py) | Compare every team's settings against a policy baseline |

## Common commands

```bash
python lifecycle.py create --name "Finance" --owner owner@contoso.com
python lifecycle.py update  --team <id> --name "Finance EMEA"
python lifecycle.py settings --team <id> --allow-guest false
python lifecycle.py archive  --team <id>
python lifecycle.py delete   --team <id>

python clone.py --team-id <source-id> --display-name "Finance (copy)" --keep
python settings_audit.py
```

`archive` is fire-and-forget in the API, and the Teams backend serialises
updates, so the example retries `Another update to this team is ongoing` before
giving up. `settings_audit.py` compares only the fields the listing endpoint
returns and skips `None` values, so it reports real drift rather than noise.

## Permissions (application)

| Operation | Permissions |
|---|---|
| Create / delete | `Group.ReadWrite.All`, `Team.Create` |
| Update & settings | `TeamSettings.ReadWrite.All` |
| Archive / unarchive | `Team.ReadWrite.All` |
| Clone | `Team.Create`, `TeamSettings.ReadWrite.All`, `Directory.ReadWrite.All` |
| Read settings | `TeamSettings.Read.All`, `Team.ReadBasic.All` |

## Reference

- <https://learn.microsoft.com/en-us/graph/api/team-post>
- <https://learn.microsoft.com/en-us/graph/api/team-archive>
- <https://learn.microsoft.com/en-us/graph/api/team-clone>
