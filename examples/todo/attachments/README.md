# Attachments and linked resources

Tasks can carry two kinds of related content: **file attachments** uploaded to
the task, and **linked resources** that point back at the email, chat, or web
page the task came from.

## [File attachments](file.py)

Attaches a small file (generated in memory, or `--file` if given), lists the
attachments, decodes the base64 `contentBytes` into the temp directory, and
removes the attachment.

```python
attachment = task.upload_attachment(b"...", "note.txt", "text/plain")
stored = task.attachments[attachment.id].get().execute_query()
raw = base64.b64decode(stored.content_bytes or "")
```

!!! warning "3 MB inline limit"
    The service only accepts simple (inline) attachments up to **3 MB**. Upload
    sessions for larger files are not currently supported, so the script stops
    with a message instead of attempting one.

## [Linked resources](linked_resources.py)

Links an Outlook email to a task, lists it, and removes it again.
`applicationName` identifies the partner app; `webUrl` and `externalId` point at
the item.

```python
task.linked_resources.add(
    applicationName="Outlook",
    displayName="Quote from the vendor",
    webUrl="https://outlook.office.com/mail/id/AAMkExample",
).execute_query()
```

!!! note "One linked resource per task"
    The service (in the tenant tested) rejects a second linked resource on the
    same task with *"Linked Resource already exists."*, so the script links a
    single source item and clears any existing links first.

Both scripts need the delegated permission **`Tasks.ReadWrite`**.
