# Entra ID Devices

Registered-device inventory for Entra ID join types and sign-in activity.

| What | File | Notes |
|------|------|-------|
| Stale device report | [`stale_report.py`](./stale_report.py) | Registered devices without a sign-in in the last 180 days |

`stale_report.py` walks `client.devices` and compares
`approximate_last_signin_datetime` against a cutoff. It complements the richer
device data in the [`intune`](../../intune/README.md) tour, which covers
compliance, hardware and remote actions for Intune-managed devices.

```python
cutoff = datetime.now(timezone.utc) - timedelta(days=180)
for device in client.devices.get().execute_query():
    if device.approximate_last_signin_datetime and device.approximate_last_signin_datetime < cutoff:
        print(device.display_name, device.operating_system)
```

## Sharp edges

- **`approximate_last_signin_datetime` can be `None`** for devices that never
  signed in; the report skips those rather than assuming they are stale.
- **Entra-registered is not the same as Intune-managed.** This service lists the
  directory device object; use `client.device_management.managed_devices` for
  management state.

---

## API reference

- [device resource](https://learn.microsoft.com/en-us/graph/api/resources/device)
