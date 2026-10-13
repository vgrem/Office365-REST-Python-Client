# Microsoft Entra ID Change Notifications

Create and manage Microsoft Graph **subscriptions** (webhooks) so your app is
notified when directory resources change. Part of the
[Entra ID guided tour](../README.md).

A subscription needs an HTTPS notification endpoint that answers Graph's
validation request, so the example lists existing subscriptions by default and
only creates one with `--apply`.

---

## Examples

| Scenario | File | Permission |
|---|---|---|
| List, create, renew and delete subscriptions | [`change_notifications.py`](./change_notifications.py) | Depends on `--resource` (e.g. `User.Read.All`) |

---

## Official docs

- [Change notifications API](https://learn.microsoft.com/en-us/graph/api/resources/webhooks)
- [Subscription resource](https://learn.microsoft.com/en-us/graph/api/resources/subscription)
