# SharePoint Alerts

Examples for managing SharePoint alerts — list, create, and remove
alerts on lists and document libraries.

Alerts are associated with the **current user**, not with the list
directly.

> [!WARNING]
> SharePoint's REST API does **not** expose the list association on
> `SP.AlertCreationInformation` (the server CSDL has no `List` property), so
> creating a list alert over REST fails server-side with a schema error. The
> `add_alert.py` example demonstrates the documented call and degrades
> gracefully; use the SharePoint UI or CSOM/PnP PowerShell to create alerts
> instead.

---

## Prerequisites

| Permission | Description |
|---|---|
| `Sites.Read.All` | List alerts |
| `Sites.ReadWrite.All` | Create and remove alerts |

---

## Examples

| Scenario | File |
|---|---|
| List alerts for the current user | [`list_alerts.py`](./list_alerts.py) |
| Add an alert on a list | [`add_alert.py`](./add_alert.py) |
| Remove an alert by ID (dry run; `--apply` to delete) | [`remove_alert.py`](./remove_alert.py) |

---

## Official docs

- [SharePoint alerts REST API](https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api)
