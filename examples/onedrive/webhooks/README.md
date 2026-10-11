# Working with change notifications

Instead of polling a drive, have Graph **push** an HTTPS notification when
something changes. Use this for near-real-time sync, and [delta
query](../../patterns/discovery/delta_sync.py) to reconcile after downtime. Requires permission
for the watched resource (e.g. `Files.Read.All`) and a **publicly reachable HTTPS**
endpoint.

## Subscribe

Name a `clientState` secret — Graph echoes it back, so you can reject spoofed
calls. Set an expiry: Graph expires subscriptions.

```python
sub = client.subscriptions.add(
    changeType="updated",
    notificationUrl="https://contoso.example/hooks/drive",
    resource="me/drive/root",
    expirationDateTime=expiry,
    clientState="verify-me",
).execute_query()
```

→ [`subscribe_to_drive.py`](./subscribe_to_drive.py)

## Renew and remove

```python
sub.set_property("expirationDateTime", new_expiry)
sub.update().execute_query()
sub.delete_object().execute_query()
```

## On your endpoint

Answer the **validation handshake** synchronously (echo `validationToken`), then
return `202` to real notifications and verify `clientState`.

> The same pattern works for other resources — see
> [`../../entraid/governance/change_notifications.py`](../../entraid/governance/change_notifications.py).

https://learn.microsoft.com/en-us/graph/change-notifications-overview
https://learn.microsoft.com/en-us/onedrive/developer/rest-api/concepts/webhooks
