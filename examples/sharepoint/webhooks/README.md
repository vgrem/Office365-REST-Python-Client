# SharePoint Webhook Subscriptions

Webhooks let your app receive HTTP callbacks when items change in a
SharePoint list. Subscriptions are scoped to a single list and expire
after 180 days.

---

## Prerequisites

| Requirement | Description | Reference |
|---|---|---|
| **Site Owner** role on the target list | Required to add, update, and remove webhook subscriptions. | [SharePoint admin roles](https://learn.microsoft.com/en-us/sharepoint/sharepoint-admin-role) |
| **Public HTTPS endpoint** | A publicly accessible URL that receives the POST notifications. | [Webhook notification format](https://learn.microsoft.com/en-us/sharepoint/dev/apis/webhooks/overview/sharepoint-webhooks#notification-format) |

---

## How webhooks work

```mermaid
sequenceDiagram
    participant App as Your App
    participant SP as SharePoint List
    participant Webhook as Your Webhook Endpoint

    App->>SP: 1. Create subscription
    SP-->>App: Subscription ID + expiry

    Note over SP,Webhook: When list items change...

    SP->>Webhook: 2. POST change notification
    Webhook-->>SP: 200 OK (verify token)
    Webhook->>SP: 3. GET change logs
    SP-->>Webhook: Changed item details

    App->>SP: 4. Renew before 180 days
    App->>SP: 5. Delete subscription (cleanup)
```

---

## Examples

| Step | Operation | File | Required role | API reference |
|---|---|---|---|---|
| **1** | Add — subscribe to list change notifications | [`add_subscription.py`](./add_subscription.py) | Site Owner on list | [Create subscription](https://learn.microsoft.com/en-us/sharepoint/dev/apis/webhooks/overview/sharepoint-webhooks) |
| **2** | List — enumerate subscriptions on a list | [`get_subscriptions.py`](./get_subscriptions.py) | Read access | [List subscriptions](https://learn.microsoft.com/en-us/sharepoint/dev/apis/webhooks/overview/sharepoint-webhooks) |
| **3** | Renew — extend expiration date | [`set_expiration.py`](./set_expiration.py) | Site Owner on list | [Update subscription](https://learn.microsoft.com/en-us/sharepoint/dev/apis/webhooks/overview/sharepoint-webhooks) |
| **4** | Remove — unsubscribe from notifications | [`remove_subscription.py`](./remove_subscription.py) | Site Owner on list | [Delete subscription](https://learn.microsoft.com/en-us/sharepoint/dev/apis/webhooks/overview/sharepoint-webhooks) |

---

## Quick start

```python
from datetime import datetime, timedelta, timezone

from office365.sharepoint.client_context import ClientContext

ctx = ClientContext("https://contoso.sharepoint.com/sites/team").with_client_certificate(
    "contoso.onmicrosoft.com", client_id="client_id", thumbprint="thumbprint", cert_path="./cert.pem"
)

target_list = ctx.web.lists.get_by_title("Documents")

# Subscribe (SharePoint requires an explicit expiration, max 180 days)
expiration = datetime.now(timezone.utc) + timedelta(days=30)
sub = target_list.subscriptions.add(
    "https://your-app.azurewebsites.net/webhook/notifications", expiration
).execute_query()
print(f"Subscribed: {sub.id} (expires: {sub.expiration_datetime})")
```

---

## API reference

- [SharePoint webhooks overview](https://learn.microsoft.com/en-us/sharepoint/dev/apis/webhooks/overview/sharepoint-webhooks)
- [SharePoint list webhooks reference](https://learn.microsoft.com/en-us/sharepoint/dev/apis/webhooks/overview/sharepoint-list-webhooks)