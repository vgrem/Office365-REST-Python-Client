# Discovery & change tracking

Keeping a local view of a drive in sync — the two patterns Microsoft recommends
for large tenants: **delta** (changes since a token) and **search** (find by
keyword across everything). Both page automatically as you iterate.

| Scenario | Example | Shows |
|---|---|---|
| Incremental sync | [`delta_sync.py`](./delta_sync.py) | full delta, persist the returned token, replay it to fetch only changes |
| Keyword search at scale | [`search_across_drives.py`](./search_across_drives.py) | one `search` per drive, aggregated (cap drives with `--max-drives`) |

## Delta in one snippet

The delta link is opaque — persist it and replay it; never build it.

```python
changes, delta_link = client.me.drive.root.delta().execute_query()
# next run:
changes, delta_link = client.me.drive.root.delta(delta_link).execute_query()
```

Delta is also the right recovery path after [webhooks](../../onedrive/webhooks/) notifications
were missed.

Requires `Files.Read` (delta) or `Files.Read.All` + `Sites.Read.All` (tenant search).

https://learn.microsoft.com/en-us/graph/api/driveitem-delta
https://learn.microsoft.com/en-us/graph/api/driveitem-search
