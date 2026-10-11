# Working with drives

A **drive** holds items and reports quota. Every user and every site has one; a
document library is a drive too. These examples explore, search and report across
drives — mostly readers. Requires `Files.Read.All` (and `Sites.Read.All` for
site drives).

## Reach a drive

A drive is reached through its owner, so you address people by **user principal
name** and sites by **server-relative path** or **URL** — no opaque ids needed:

```python
client.me.drive  # the signed-in user's OneDrive
client.users["ada@contoso.com"].drive  # another user's drive, by UPN
client.sites.get_by_path("/sites/marketing").drive  # a site's library, by path
client.sites.get_by_url("https://contoso.sharepoint.com/sites/marketing").drive  # by URL
```

→ [`user_drive.py`](./user_drive.py)

## Browse and search

```python
root = client.me.drive.root
recent = root.recent().execute_query()
hits = root.search("quarterly").execute_query()
```

→ [`explore.py`](./explore.py) · [`search_across_drives.py`](../../patterns/discovery/search_across_drives.py) (across all drives) · [`export_user_drive.py`](./export_user_drive.py)

## Storage & reporting

```python
drive = client.me.drive.get().execute_query()
used, total = drive.quota.used, drive.quota.total
```

→ [`storage_report.py`](./storage_report.py) (tenant-wide, paged)
