# Webhooks & change notifications

Push instead of poll: Graph POSTs an HTTPS notification when drive content
changes. Use this for near-real-time sync; use
[delta query](../files/delta_query.py) to reconcile after downtime.

| Scenario | File | Permission |
|---|---|---|
| Subscribe a webhook to drive changes, renew, remove | [`subscribe_to_drive.py`](./subscribe_to_drive.py) | `Files.Read.All` |

Your endpoint must answer the **validation handshake** (echo `validationToken`)
synchronously, then respond `202` to real notifications. Pass a `clientState`
secret and reject notifications whose value doesn't match.

The same pattern works for other resources: [`entraid/governance/change_notifications.py`](../../entraid/governance/change_notifications.py).

https://learn.microsoft.com/en-us/graph/change-notifications-overview
https://learn.microsoft.com/en-us/onedrive/developer/rest-api/concepts/webhooks
