# Navigation

Manage the site navigation structure — top navigation bar, Quick Launch,
and hierarchical menu nodes.

---

## Prerequisites

| Requirement | Description | Reference |
|---|---|---|
| **Site Owner** or **Designer** role | Required to add, update, or delete navigation nodes. Read access for browsing. | [SharePoint permissions](https://learn.microsoft.com/en-us/sharepoint/sharepoint-admin-role) |

---

## Getting started

```python
from office365.sharepoint.client_context import ClientContext

ctx = ClientContext("https://contoso.sharepoint.com/sites/team").with_client_certificate(
    "contoso.onmicrosoft.com", client_id="client_id", thumbprint="thumbprint", cert_path="./cert.pem"
)

# Read top navigation
nav = ctx.web.navigation.top_navigation_bar.get().execute_query()
for node in nav:
    print(f"  {node.title}  → {node.url}")

# Read Quick Launch
ql = ctx.web.navigation.quick_launch.get().execute_query()
for node in ql:
    print(f"  {node.title}  → {node.url}")
```

---

## Read

| What | File | Notes |
|------|------|-------|
| **Top navigation bar** | [`list_top_nav.py`](./list_top_nav.py) | All nodes in the top nav |
| **Quick Launch** | [`list_quick_launch.py`](./list_quick_launch.py) | All nodes in the Quick Launch |
| **Export to JSON** | [`export_to_json.py`](./export_to_json.py) | Recursive top-nav tree (with sub-menus) as JSON, via `get_all_nodes` + `to_json` |

## Create

| What | File | Notes |
|------|------|-------|
| **Add child node** | [`add_child_node.py`](./add_child_node.py) | Add a sub-menu under an existing Quick Launch node |

## Copy

| What | File | Notes |
|------|------|-------|
| **Copy top navigation** | [`copy_navigation.py`](./copy_navigation.py) | Rebuild a site's top nav from a source site (recursive, idempotent) |

## Export

| What | File | Notes |
|------|------|-------|
| **Export to CSV** | [`export_to_csv.py`](./export_to_csv.py) | Flat Quick Launch + top nav via `get_all_nodes` + `to_records` |

---

## API reference

- [SharePoint navigation API](https://learn.microsoft.com/en-us/sharepoint/dev/apis/navigation-api-reference)
