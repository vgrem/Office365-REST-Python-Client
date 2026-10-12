# Users

Manage users in SharePoint: who has access to a site, current user info,
tenant-wide search, site groups, and OneDrive details.

---

## Prerequisites

| Requirement | Description | Reference |
|---|---|---|
| **Read access** to the site | Required to list users. **Site Owner** to add users. | [SharePoint admin roles](https://learn.microsoft.com/en-us/sharepoint/sharepoint-admin-role) |

---

## Examples

### Current user

| Operation | File | Required role |
|---|---|---|
| Get current user | [`whoami.py`](./whoami.py) | Any authenticated user |
| Get current user (async) | [`whoami_async.py`](./whoami_async.py) | Any authenticated user |
| Get my personal site | [`get_my_site.py`](./get_my_site.py) | Any authenticated user |

### List and search

| Operation | File | Required role |
|---|---|---|
| List site users | [`list_site_users.py`](./list_site_users.py) | Read access |
| List site groups and members | [`list_site_groups.py`](./list_site_groups.py) | Read access |
| Search tenant users | [`search_tenant_users.py`](./search_tenant_users.py) | Read access (admin context) |

### Manage and OneDrive

| Operation | File | Required role |
|---|---|---|
| Add / ensure a site user | [`add_user.py`](./add_user.py) | Site Owner |
| Get OneDrive quota max | [`get_onedrive_quota.py`](./get_onedrive_quota.py) | Read access |

---

## Quick start

```python
from office365.sharepoint.client_context import ClientContext

ctx = ClientContext("https://contoso.sharepoint.com/sites/team").with_client_certificate(
    "contoso.onmicrosoft.com", client_id="client_id", thumbprint="thumbprint", cert_path="./cert.pem"
)

# Get current user
me = ctx.web.current_user.get().execute_query()
print(f"Hello, {me.title}  ({me.login_name})")

# List all site users
users = ctx.web.site_users.get().execute_query()
for u in users:
    print(f"  {u.title}  ({u.login_name})")
```

---

## API reference

- [SharePoint users and groups REST API](https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api)
