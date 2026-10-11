# Working with drives

A **drive** holds items and reports quota. Every user and every site has one; a
document library is a drive too. These examples explore, search and report across
drives — mostly readers. Requires `Files.Read.All` (and `Sites.Read.All` for
site drives).

## Reach a drive

```python
client.me.drive  # the signed-in user's OneDrive
client.users["id"].drive  # another user's drive
client.sites["id"].drive  # a site's default document library
```

→ [`user_drive.py`](./user_drive.py)

## Browse and search

```python
root = client.me.drive.root
recent = root.recent().execute_query()
hits = root.search("quarterly").execute_query()
```

→ [`explore.py`](./explore.py) · [`search_all.py`](./search_all.py) (across all drives) · [`export_user_drive.py`](./export_user_drive.py)

## Storage & reporting

```python
drive = client.me.drive.get().execute_query()
used, total = drive.quota.used, drive.quota.total
```

→ [`storage_report.py`](./storage_report.py) (tenant-wide, paged)
