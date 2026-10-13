# Licensing

Examples for working with Microsoft 365 licenses via Graph API —
SKU inventory, license assignment, service plan management, and usage reports.

---

## Prerequisites

| Permission | Description | Reference |
|---|---|---|
| `User.Read.All` | Read users and their license assignments | [User permissions](https://learn.microsoft.com/en-us/graph/permissions-reference#user-permissions) |
| `Organization.Read.All` | Read subscribed SKUs | [Organization permissions](https://learn.microsoft.com/en-us/graph/permissions-reference#organization-permissions) |
| `User.ReadWrite.All` | Assign and remove licenses | [User permissions](https://learn.microsoft.com/en-us/graph/permissions-reference#user-permissions) |

---

## Patterns

| Scenario | File |
|---|---|
| **List available licenses (SKUs) with their service plans** | [`list_skus.py`](./list_skus.py) |
| License inventory and unlicensed user report | [`report.py`](./report.py) |
| License assignment and SKU switch | [`assign.py`](./assign.py) |
| **Bulk assign licenses from CSV** | [`bulk_assign_license.py`](./bulk_assign_license.py) |
| **Disable a service plan within a license** | [`modify_service_plans.py`](./modify_service_plans.py) |
| **Remove a license from a user** | [`remove.py`](./remove.py) |
| **Find all users with a specific SKU** | [`find_licensed.py`](./find_licensed.py) |
| **Full license usage report** | [`usage_report.py`](./usage_report.py) |
| **Get the current user's license details** | [`get_licenses.py`](./get_licenses.py) |
| **Check a required SKU is present (require_license)** | [`check_license.py`](./check_license.py) |

---

## Quick start

```python
from office365.graph_client import GraphClient

client = GraphClient(tenant="contoso.onmicrosoft.com").with_client_secret("client_id", "client_secret")

skus = client.subscribed_skus.get().execute_query()
for s in skus:
    print(f"{s.sku_part_number}")
```

---

## Official docs

- [License management API](https://learn.microsoft.com/en-us/graph/api/resources/license)
- [Subscribed SKU API](https://learn.microsoft.com/en-us/graph/api/resources/subscribedsku)
- [Assign license API](https://learn.microsoft.com/en-us/graph/api/user-assignlicense)
