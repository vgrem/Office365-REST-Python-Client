# Working with Files

Upload, download, copy, move, delete, share, and manage files in SharePoint
document libraries — the everyday operations for building on top of documents.

Files live inside **document libraries**, organized in **folders**. Separately,
**list items** can have **attachments** — see
[`listitems/attachments/`](../listitems/attachments/) for those.

```mermaid
graph TD
    subgraph Site
        Library["Document Library e.g. Shared Documents"]
    end

    subgraph Library
        Folder["Folder"]
        File["File"]
        Folder --> File
    end

    Library --> Folder
    Library --> File
```

---

## Authentication

SharePoint's `/_api` app-only flow does **not** accept a client secret — use a
delegated sign-in (username & password, no MFA) or a client certificate for
app-only automation. The examples here use username & password:

```python
from office365.sharepoint.client_context import ClientContext

ctx = ClientContext("https://contoso.sharepoint.com/sites/team").with_username_and_password(
    tenant="contoso.onmicrosoft.com", client_id="client_id", username="user@contoso.com", password="password"
)
```

> **`with_client_secret(...)` is a common mistake for SharePoint.** It works
> for **Microsoft Graph**, but not for `ClientContext` — use
> `with_username_and_password` (below) or `with_client_certificate(...)`
> (app-only). See [`auth/`](../auth/) for the full matrix.

## Quick start

Upload a small file, then download it back:

```python
# Upload a file (< 4 MB)
with open("./report.docx", "rb") as f:
    uploaded = ctx.web.default_document_library().root_folder.upload_file("report.docx", f.read()).execute_query()
print(f"Uploaded: {uploaded.server_relative_url}")

# Download it back
downloaded = uploaded.get_content().execute_query()
print(f"Downloaded: {len(downloaded.content)} bytes")
```

---

## Upload

| What | File | Notes |
|------|------|-------|
| Upload a small file | [`upload.py`](./upload.py) | File < 4 MB |
| Upload a large file | [`upload_large.py`](./upload_large.py) | Chunked upload session |
| Upload with a progress bar | [`upload_with_progress.py`](./upload_with_progress.py) | tqdm progress for large files |
| Upload a path or stream | `FileCollection.upload_file` | Simple request or resumable session, picked by size |
| Ensure a file exists | `Folder.ensure_file` | Deferred get-or-upload; re-runs are no-ops |
| Upload with checksum | [`upload_with_checksum.py`](./upload_with_checksum.py) | MD5 verification |
| Upload CSV data | [`upload_csv.py`](./upload_csv.py) | Data files |
| Upload JSON data | [`upload_json.py`](./upload_json.py) | Data files |
| Replace content | [`replace.py`](./replace.py) | Overwrite via binary stream |

`FileCollection.upload_file` takes a local path or an open stream and picks the
transport for you (single request at or below `chunk_size`, a resumable session
above it). `Folder.ensure_file` is the idempotent counterpart of
`Folder.upload_file`: it creates missing parent folders, then reuses the file if
it already exists (`on_conflict="skip"`, the default) or overwrites it
(`on_conflict="replace"`).

```python
# One call, sized automatically — queues the right upload for the file's size
file = target_folder.files.upload_file("./archive/big.mp4").execute_query()

# Get-or-upload: parent folders are created; a re-run is a no-op
file = target_folder.ensure_file("2026/Q1/report.txt", "hello").execute_query()
```

## Download

| What | File | Notes |
|------|------|-------|
| Download a file | [`download.py`](./download.py) | To disk |
| Download a large file | [`download_large.py`](./download_large.py) | Streaming with progress |
| Download by URL | [`download_from_url.py`](./download_from_url.py) | Absolute URL |
| Download a whole library | [`download_from_lib.py`](./download_from_lib.py) | Every file, preserving folders |
| Download most recent | [`download_recent.py`](./download_recent.py) | Latest uploaded file |
| Download a version | [`download_versions.py`](./download_versions.py) | A specific file version |
| Download with a progress bar | [`download_with_progress.py`](./download_with_progress.py) | Folder → zip, tqdm progress |
| Download files in parallel | [`download_parallel.py`](./download_parallel.py) | No manual threads or contexts |
| Read bytes in memory | [`get_content.py`](./get_content.py) | Without touching disk |

```python
# Download to a local file
with open("report.docx", "wb") as f:
    ctx.web.get_file_by_server_relative_path("Shared Documents/report.docx").download(f).execute_query()
```

## Bulk operations

The highest-leverage scripts for migrations and backups:

| What | File | Notes |
|------|------|-------|
| Upload many files in one batch | [`upload_batch.py`](./upload_batch.py) | `execute_batch`, one request per batch |
| Zip a folder incl. version history | [`download_folder_with_versions.py`](./download_folder_with_versions.py) | Current content + every previous version |

```python
# Bulk upload: queue, then flush in one batch request
for name in os.listdir("./data"):
    with open(f"./data/{name}", "rb") as f:
        target_folder.upload_file(name, f.read())  # queue
ctx.execute_batch()  # one request per batch

# Backup a folder with its full version history
with open("archive.zip", "wb") as f:
    folder.download_folder(f, include_versions=True).execute_query()
```

## Copy & Move

| What | File | Notes |
|------|------|-------|
| Copy to another folder | [`copy_file.py`](./copy_file.py) | |
| Copy and rename | [`copy_file_with_name.py`](./copy_file_with_name.py) | |
| Copy by path | [`copy_using_path.py`](./copy_using_path.py) | Server-relative paths |
| Move | [`move_file.py`](./move_file.py) | Between folders |

## Delete

| What | File | Notes |
|------|------|-------|
| Delete / recycle | [`delete.py`](./delete.py) | Permanent or recycle bin |

## Metadata & Browse

| What | File | Notes |
|------|------|-------|
| Basic properties | [`get_props.py`](./get_props.py) | Name, size, URL, timestamps |
| Extended properties | [`get_extended_props.py`](./get_extended_props.py) | Every list-item field |
| System metadata | [`get_system_metadata.py`](./get_system_metadata.py) | Author, modified-by, created |
| Check existence | [`exists.py`](./exists.py) | |
| Enumerate a library | [`get_all_items.py`](./get_all_items.py) | Files and folders |
| Enumerate a folder with >5,000 items | [`list_large_folder.py`](./list_large_folder.py) | Paged enumeration past the list view threshold |
| Recently modified | [`get_recent_files.py`](./get_recent_files.py) | |
| Pre-authorized download URL | [`get_download_link.py`](./get_download_link.py) | Time-limited link |

## Check Out & Approvals

For libraries with required check-out or content approval:

| What | File | Notes |
|------|------|-------|
| Check out / in | [`checkout_checkin.py`](./checkout_checkin.py) | Lock, edit, release |
| Checked-out files | [`get_checked_out.py`](./get_checked_out.py) | Who has files locked |
| Checkout type | [`get_checkout_type.py`](./get_checkout_type.py) | Status of one file |
| Publish / unpublish | [`publish_unpublish.py`](./publish_unpublish.py) | Submit for approval |
| Approve / deny | [`approve_deny.py`](./approve_deny.py) | Review submitted files |

### Locked files (open in Office)

A file open in Office holds a **shared lock** — different from a check-out
lock. An overwrite fails with `SPFileLockedException` (HTTP 423), because the
API cannot break a shared lock. The library makes the failure catchable and
offers opt-in remedies:

| What | File | Notes |
|------|------|-------|
| Retry / metadata / bypass delete | [`handle_locked_file.py`](./handle_locked_file.py) | `retry_on(FileLockedException)`, `update_ex(bypass_shared_lock=True)`, `delete_object(bypass_shared_lock=True)` |

### Acting on behalf of a user

SharePoint REST has no "impersonate" switch — a request runs as whoever the
access token represents, so a check-out is always attributed to the
authenticated identity:

- **As a specific user** — sign in with a delegated flow for that user
  (`with_username_and_password`, `with_interactive`, `with_device_flow`, or a
  delegated token supplied via `with_access_token`, e.g. an on-behalf-of token).
  [`checkout_checkin.py`](./checkout_checkin.py) uses this flow.
- **As the application** — app-only credentials (`with_client_certificate`) run
  as the app, not a human user, so they cannot be used to attribute a check-out
  to someone else.

To release a file another user left checked out, list it with
[`get_checked_out.py`](./get_checked_out.py) and take over the check-out
(`CheckedOutFile.takeover_checkout()`), which requires sufficient permissions.

## Sharing

| What | File | Notes |
|------|------|-------|
| Resolve a sharing link | [`get_by_sharing_link.py`](./get_by_sharing_link.py) | Link → file |
| Download via shared link | [`download_by_shared_link.py`](./download_by_shared_link.py) | Guest / anonymous link |

## Create Documents

| What | File | Notes |
|------|------|-------|
| Excel workbook | [`create_excel.py`](./create_excel.py) | |
| Word document | [`create_word.py`](./create_word.py) | |
| Wiki page | [`create_wiki.py`](./create_wiki.py) | |
| Rename a file | [`rename_page.py`](./rename_page.py) | |

## Permissions

| What | File | Notes |
|------|------|-------|
| Effective permissions | [`permissions/get.py`](./permissions/get.py) | For a file |
| Per-user permissions | [`permissions/list.py`](./permissions/list.py) | |
| Check a specific access | [`permissions/check.py`](./permissions/check.py) | Does a user have access? |
| Grant permissions | [`permissions/assign.py`](./permissions/assign.py) | Role assignment |

## Versions

| What | File | Notes |
|------|------|-------|
| List versions | [`versions/list.py`](./versions/list.py) | |
| Get by label | [`versions/get_by_label.py`](./versions/get_by_label.py) | A specific version |
| Delete / recycle versions | [`versions/delete.py`](./versions/delete.py) | Keep N / delete all; retry + timeout for large files |
| Restore a version | [`restore_version.py`](./restore_version.py) | Roll back |

## DataFrames

Read/write a file's **content** as a pandas DataFrame (CSV/XLSX/JSON/Parquet);
file metadata stays as plain properties (`file.name`, `file.length`, ...).

| What | File | Notes |
|------|------|-------|
| Write a DataFrame to a library file | [`write_dataframe.py`](./write_dataframe.py) | CSV (UTF-8 BOM) or XLSX; symmetric read via `Folder.read_dataframe` / `File.read_dataframe` |

## Audit & Compliance

| What | File | Notes |
|------|------|-------|
| Sensitivity-label baseline | [`find_label_downgrades.py`](./find_label_downgrades.py) | Purview labels (via Graph) |
| Unused files | [`find_unused_files.py`](./find_unused_files.py) | No user access in N days |
| Version storage report | [`version_storage_report.py`](./version_storage_report.py) | Version count & storage cost |

## Attachments

Attachments are files attached to **list items**, not documents in a library —
see [`listitems/attachments/`](../listitems/attachments/) for upload, download,
list, and delete operations.

---

## Related recipes

- [Upload a folder with metadata](../recipes/upload_folder_with_metadata.py) — mirror a local folder into a library, chunk-upload large files, and stamp metadata.

---

## API reference

- [SharePoint files REST API](https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api)
- [Working with files and folders REST](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/working-with-folders-and-files-with-rest)
