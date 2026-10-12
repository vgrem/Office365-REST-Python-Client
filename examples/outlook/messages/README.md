# Outlook messages

Mail is the deepest Outlook resource: send, reply, move and delete; walk folders
and paginate; tag with categories; and export the lot. Part of the
[Outlook tour](../README.md), which explains the model, permissions and the
shared `send_mail` / draft idioms.

| What | File | Notes |
|------|------|-------|
| Send a message | [`send.py`](./send.py) | Subject, body, recipients |
| Reply / forward / move / copy | [`lifecycle.py`](./lifecycle.py) | The full message lifecycle |
| Folders | [`folders.py`](./folders.py) | Create, navigate, empty, mark read |
| Search | [`search.py`](./search.py) | KQL and `$filter` (mutually exclusive) |
| Paginate | [`pagination.py`](./pagination.py) | `$top` + `$skip` over thousands |
| Inbox rules | [`inbox_rules.py`](./inbox_rules.py) | Automate handling |
| Categories | [`categories.py`](./categories.py) | Master colour labels |
| Mailbox settings | [`mailbox_settings.py`](./mailbox_settings.py) | Automatic replies (OOF) |
| Mail tips | [`mail_tips.py`](./mail_tips.py) | Pre-flight OOF / size checks |
| Attachments | [`attachments.py`](./attachments.py) | Add, list, download |
| Send with a large attachment | [`send_with_large_attachment.py`](./send_with_large_attachment.py) | Upload session |
| Large messages | [`large_messages.py`](./large_messages.py) | Over a size threshold |
| Export a folder to CSV | [`export_folder_csv.py`](./export_folder_csv.py) | Data pipeline |
| Export a folder to JSON | [`export_json.py`](./export_json.py) | Data pipeline |
| Export MIME (`.eml`) | [`export_mime.py`](./export_mime.py) | One message |
| Export attachments | [`export_attachments.py`](./export_attachments.py) | Folder → local disk |
| Export a folder concurrently | [`export_mail_async.py`](./export_mail_async.py) | Async |
| Archive old messages | [`archive_old.py`](./archive_old.py) | Moves into "Archive" |
| Clean up old messages | [`cleanup_old.py`](./cleanup_old.py) | Dry-run first |
