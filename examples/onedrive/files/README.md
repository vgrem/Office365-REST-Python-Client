# Working with files

A file is a `DriveItem` with a `file` facet. You upload bytes into it, download
bytes out of it, and change its *metadata* (name, parent, permissions) without
touching the content. The scripts here run on throwaway files and clean up, so
they're safe to re-run. Requires `Files.ReadWrite` (some readers need `Files.Read`).

## Address a file

Four ways to name a `DriveItem` — by path, by id, by enumerating the parent, or
through a special folder. Names are **case-preserving but matched
case-insensitively**; ids are stable.

```python
drive = client.me.drive
drive.root.get_by_path("Reports/Q1.txt").get().execute_query()  # by path
drive.items[item_id].get().execute_query()  # by id
drive.root.children.get().execute_query()  # enumerate
drive.special["Documents"].get().execute_query()  # special folder
```

→ [`addressing.py`](./addressing.py)

## Upload and download

Upload small files in one call; the round-trip below is the base pattern every
other operation builds on. Large files use a resumable session — see
[`../patterns/large-data/upload_large.py`](../../patterns/large-data/upload_large.py).

```python
uploaded = client.me.drive.root.upload_file("report.txt").execute_query()
with open("download.txt", "wb") as f:
    uploaded.download(f).execute_query()
```

→ [`upload_download.py`](./upload_download.py) · [`download_json.py`](./download_json.py)

## Ensure a file exists (idempotent)

Get-or-create without racing the server — handy in provisioning code.

```python
item = client.me.drive.root.get_by_path("config/settings.json").get().execute_query()
```

→ [`ensure_file.py`](./ensure_file.py)

## Copy, move, rename, version, delete

Copy is a **long-running** operation (see [patterns/lro](../../patterns/lro/));
move/rename are a single `parentReference` patch.

```python
copied = item.copy(name="report (copy).txt", parent=folder).execute_query().wait_for_item()
item.move(folder)  # or rename via .set_property("name", ...).update()
item.delete_object().execute_query()
```

→ [`manage.py`](./manage.py) · [`lifecycle.py`](./lifecycle.py) (check-out/in) · [`recycle_bin.py`](./recycle_bin.py)

## Share: links vs invitations

A **sharing link** grants access to whoever holds the URL (audience: `anonymous`
or `organization`); an **invitation** grants access to named people and can email
them. Use a link when you don't know the recipients, an invitation when you do.

```python
shared = item.create_link("view", "organization").execute_query()  # link
print(shared.link.webUrl)

item.invite(["someone@contoso.com"], roles=["read"], send_invitation=True).execute_query()
```

→ [`sharing_links.py`](./sharing_links.py) · [`sharing_invitations.py`](./sharing_invitations.py) · advanced lifecycle under [`../../sharepoint/sharing/`](../../sharepoint/sharing/)

## Custom metadata

Tag a file with your own columns through its backing `listItem`.

```python
fields = item.list_item.fields.get().execute_query()
fields.set_property("Category", "Finance")
fields.update().execute_query()
```

→ [`custom_metadata.py`](./custom_metadata.py)

## Search, discover, sync

Keyword search, largest files, what's shared, and a **delta** feed to keep a
local cache in sync.

```python
for item in root.children.select(["id", "name"]).filter("size gt 0").top(50).get().execute_query():
    ...
```

→ [`search.py`](./search.py) · [`largest_files.py`](./largest_files.py) · [`find_shared.py`](./find_shared.py) · [`delta_sync.py`](../../patterns/discovery/delta_sync.py) · [`analytics.py`](./analytics.py)
