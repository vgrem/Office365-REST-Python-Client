# Examples

Practical examples demonstrating how to use the `office365-rest-python-client`
library across Microsoft 365 and Entra ID services.

---

## Overview

| Directory | Product / API | Covers |
|---|---|---|
| [`auth/`](./auth/) | Graph authentication | Client secret, certificate, interactive, device code, ROPC, GCC High |
| [`patterns/`](./patterns/) | **Cross-cutting patterns** | Long-running operations, async, large data, reliability — mechanism-first, reused across products |
| [`patterns/lro/`](./patterns/lro/) | **Long-running operations** | Wait (sync/async), resume from a token, a monitor CLI — the Graph async pattern |
| [`patterns/async/`](./patterns/async/) | **Async / await** | Async twins, concurrency, batching, streaming export, credentials, transports |
| [`admin/`](./admin/) | **Microsoft 365 Admin** | Service health, tenant settings, profile cards |
| [`sharepoint/`](./sharepoint/) | **Microsoft SharePoint** | Lists, items, files, folders, search, permissions, sites, taxonomy, webhooks |
| [`onedrive/`](./onedrive/) | **Microsoft OneDrive** | Files, folders, drives, sharing, search, Excel workbooks |
| [`teams/`](./teams/) | **Microsoft Teams** | Lifecycle, channels, messages, members, apps, tabs |
| [`outlook/`](./outlook/) | **Outlook / Exchange Online** | Mail (send, draft, folders, rules, search), events, calendars |
| [`onenote/`](./onenote/) | **Microsoft OneNote** | Notebooks, sections, section groups, pages |
| [`planner/`](./planner/) | **Microsoft Planner** | Plans, buckets, tasks, assignments, details |
| [`entraid/`](./entraid/) | **Microsoft Entra ID** | Users, groups, applications, roles, policies, identity |
| [`defender/`](./defender/) | **Microsoft Defender** | Advanced hunting, incidents, alerts, secure score |
| [`intune/`](./intune/) | **Microsoft Intune** | Devices, compliance, configuration profiles, remote actions |
| [`booking/`](./booking/) | **Microsoft Bookings** | Businesses, services, appointments |
| [`communications/`](./communications/) | **Cloud Communications** | Calls, online meetings, presence |
| [`purview/`](./purview/) | **Microsoft Purview** | eDiscovery, retention labels, subject rights requests |
| [`reports/`](./reports/) | M365 usage reports | Email, mailbox, OneDrive, SharePoint, Teams, M365 app, Office activations, MFA, Copilot |
| [`insights/`](./insights/) | Graph Insights API | Shared documents, trending content |
| [`security/`](./security/) | **Microsoft Graph Security** | Alerts, incidents, secure score |
| [`backuprestore/`](./backuprestore/) | **M365 Backup Storage** | Backup and restore |
| [`todo/`](./todo/) | **Microsoft To Do** | Task lists and tasks |
| [`data/`](./data/) | Sample data | Files used by other examples (JSON, CSV, XLSX, images) |

---

## Quick start

Every script here is runnable from a repository checkout:

```bash
cp .env.example .env                                  # fill in the credentials you need
uv run python -m tests.doctor                          # confirm what is configured
uv run python examples/auth/with_client_secret.py
```

Examples authenticate through the same central loader as the tests
(`tests/settings.py`, which reads `.env`) and reuse the test credentials. See
[README-dev.md](../README-dev.md) for the full local setup, the authentication
flow matrix and the certificate recipe.

```python
from office365.graph_client import GraphClient

client = GraphClient(tenant="contoso.onmicrosoft.com").with_client_secret("client_id", "client_secret")

me = client.me.get().execute_query()
print(f"Signed in as: {me.display_name}")
```

See [`auth/`](./auth/) for all supported authentication flows, and
[`sharepoint/auth/`](./sharepoint/auth/) for the SharePoint-specific guidance
(app-only automation uses a **certificate**, not a client secret).

---

## Related

- [Microsoft Graph API documentation](https://learn.microsoft.com/en-us/graph/api/overview)
- [SharePoint REST API documentation](https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api)
- [Office 365 REST Python Client on GitHub](https://github.com/vgrem/office365-rest-python-client)
