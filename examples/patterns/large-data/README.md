# Large data

Streaming large payloads without loading them into memory or blocking: resumable
chunked uploads, concurrent downloads, and exporting big collections.

| Scenario | Example | Shows |
|---|---|---|
| Resumable chunked upload | [`upload_large.py`](./upload_large.py) | create an upload session, stream chunks, resume on failure |
| Concurrent downloads | [`download_parallel.py`](./download_parallel.py) | bounded parallelism over a folder's files |

Related, mechanism-first:

- event-loop-friendly upload: [`../async/upload_large_file_async.py`](../async/upload_large_file_async.py)
- sharePoint chunked upload: [`../async/upload_large_file_sp_async.py`](../async/upload_large_file_sp_async.py)
- streamed report export: [`../async/export_report_async.py`](../async/export_report_async.py)

Requires `Files.ReadWrite` (and `Sites.ReadWrite.All` for the SharePoint twin).

https://learn.microsoft.com/en-us/graph/api/driveitem-createuploadsession
