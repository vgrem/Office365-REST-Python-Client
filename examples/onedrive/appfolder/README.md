# Application folder

A private, app-scoped sandbox inside a user's drive — the least-privilege way for
an app to store its own files (`Files.ReadWrite.AppFolder`).

| Scenario | File | Permission |
|---|---|---|
| Use the `approot` special folder | [`app_folder.py`](./app_folder.py) | `Files.ReadWrite.AppFolder` |

Reach the folder through the `special` collection:

```python
app_folder = client.me.drive.special["approot"].get().execute_query()
```

https://learn.microsoft.com/en-us/onedrive/developer/rest-api/concepts/special-folders-appfolder
