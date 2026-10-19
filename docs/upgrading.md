# Upgrading from 2.x

3.0.0 regenerated the model surface with PEP 8 names and full type hints. The OData
wire contract did not change: the same JSON keys go out and come back. What changed is
the **Python** name you use to reach them.

This page covers the migration. The exhaustive per-release detail stays in the
[CHANGELOG](https://github.com/vgrem/office365-rest-python-client/blob/master/CHANGELOG.md).

## Property names are snake_case

Every model property that used to be camelCase is now snake_case — **628 properties**
across the SharePoint, Graph, and security models.

| 2.x | 3.x |
|---|---|
| `file.serverRelativeUrl` | `file.server_relative_url` |
| `file.timeCreated` | `file.time_created` |
| `file.modifiedBy` | `file.modified_by` |
| `folder.timeLastModified` | `folder.time_last_modified` |
| `folder.listItemAllFields` | `folder.list_item_all_fields` |
| `list.contentTypes` | `list.content_types` |
| `web.allProperties` | `web.all_properties` |
| `item.roleAssignments` | `item.role_assignments` |
| `drive_item.createdDateTime` | `drive_item.created_date_time` |
| `drive_item.parentReference` | `drive_item.parent_reference` |

The rule is mechanical: take the OData key from the API documentation, lowercase its
first letter, and put `_` before every capital.

```
ServerRelativeUrl  ->  server_relative_url
TimeLastModified   ->  time_last_modified
ListItemAllFields  ->  list_item_all_fields
```

```python
# 2.x
print(file.serverRelativeUrl, file.timeCreated)

# 3.x
print(file.server_relative_url, file.time_created)
```

## The wire names still work

Only the Python attribute moved. Everything that talks to SharePoint by key keeps the
API's own casing:

```python
file.properties["ServerRelativeUrl"]  # raw payload value
file.get_property("ServerRelativeUrl")  # resolves to file.server_relative_url
file.ensure_property("ServerRelativeUrl")  # request the wire name explicitly

list_obj.items.select(["Id", "ServerRelativeUrl"])  # $select / $expand take wire names
```

`get_property()` is the general-purpose way out: it maps any API key to whichever
Python property now carries it, so a mixed 2.x/3.x codebase can pass wire names around.

## Let your type checker find the renames

The renamed properties are ordinary typed properties, not `__getattr__` lookups, so a
type checker lists every stale access for you — the old name is a real error, and the
new one type-checks cleanly. Run it over your codebase after upgrading and work through
the report:

```python
from office365.sharepoint.files.file import File

file = File(ctx)
print(file.serverRelativeUrl)
```

```
error: Cannot access attribute "serverRelativeUrl" for class "File"
  Attribute "serverRelativeUrl" is unknown (reportAttributeAccessIssue)
```

## Other breaking changes in 3.0.0

- **Python 3.8+** — Python 2 support was dropped.
- **Legacy SAML/ACS auth retired** — `with_user_credentials()` now raises `RuntimeError`
  for SharePoint Online; use `with_username_and_password()` (MSAL ROPC) or
  `with_client_credentials()`. See [Authentication](auth/index.md).
- **USGovernment GCC endpoints corrected** — they previously pointed at the wrong URLs.
- **Some model classes were renamed or removed** while regenerating the schema — see the
  `Removed` section of the 3.0.0 changelog entry.

## Breaking changes after 3.0.0

### 3.4.0: `MigrationItem.author_id` / `editor_id` moved to `Principal.user_id`

The migration API used to carry the source's numeric user ids on the item:

```python
item.author_id  # 7  — the source's AuthorId
item.editor_id  # 12
```

They are now on the resolved principal, which is where the rest of the identity
already lived:

```python
item.author.user_id  # 7
item.editor.user_id  # 12
```

`item.author` / `item.editor` are not new (the adapters have filled them since
authorship landed), so code that reads a login name or a PUID is unaffected. What
breaks is constructing a `MigrationItem(author_id=…, editor_id=…)` — that is now a
`TypeError` — and reading the two attributes, which no longer exist. An unresolved
author is `None`, so guard accordingly:

```python
user_id = item.author.user_id if item.author else None
```

The numeric id is **site-local**: it identified a user inside the site it came from
and is never written to the target. The `ItemReport` CSV/JSON keeps its
`author_id`/`editor_id` columns, now populated from the principal.

## Staying on 2.x

3.x did not ship camelCase aliases, so 2.x-style attribute access does not work on 3.x —
that is a `AttributeError`, not a warning. If a codebase cannot be migrated yet, pin the
last 2.x release:

```
office365-rest-python-client==2.6.2
```
