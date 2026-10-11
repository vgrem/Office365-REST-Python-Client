# Apps & tabs

Three related objects, often confused:

| Object | What it is | Endpoint |
|---|---|---|
| **Catalog app** | The tenant's app store entry (built-in, store, sideloaded) | `client.app_catalogs.teams_apps` |
| **Installation** | A catalog app added to a team | `team.installed_apps` |
| **Tab** | A pinned app inside a channel | `channel.tabs` |

An app must exist in the catalog before it can be installed; a tab then pins an
installed app to a channel.

```python
app = client.app_catalogs.teams_apps.get().execute_query()
team.installed_apps.add(app.teams_app_id).execute_query()
for tab in channel.tabs.get().execute_query():
    print(tab.display_name, tab.teams_app.id)
```

## Scripts

| Script | What it does |
|---|---|
| [`catalog.py`](./catalog.py) | Inventory of the tenant app catalog |
| [`installed.py`](./installed.py) | App adoption across all teams (shadow-IT detection) |
| [`lifecycle.py`](./lifecycle.py) | `search` · `list` · `install` · `uninstall` |
| [`tabs.py`](./tabs.py) | Tabs (pinned apps) across teams → channels |

## Common commands

```bash
python catalog.py
python installed.py
python tabs.py

python lifecycle.py search --name "Planner"
python lifecycle.py install --team <id> --app <catalog-app-id>
python lifecycle.py uninstall --team <id> --app <installation-id>
```

`installed.py` also reports catalog apps that are installed **nowhere** — a cheap
way to find abandoned apps. `tabs.py` walks teams → channels → tabs, so it is
the slowest report here.

## Permissions (application)

| Operation | Permissions |
|---|---|
| Catalog | `AppCatalog.Read.All` (write: `AppCatalog.ReadWrite.All`) |
| Installed apps | `TeamsAppInstallation.Read.All` (write: `ReadWrite.All`) |
| Tabs | `Tab.Read.All` |
| List teams/channels | `Team.ReadBasic.All`, `Channel.ReadBasic.All` |

## Reference

- <https://learn.microsoft.com/en-us/graph/api/appcatalogs-list-teamsapps>
- <https://learn.microsoft.com/en-us/graph/api/teamsappinstallation-list>
- <https://learn.microsoft.com/en-us/graph/api/channel-list-tabs>
