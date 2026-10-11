# Working with the application folder

An app that only needs to keep *its own* files shouldn't ask for the user's whole
drive. OneDrive reserves a private **`approot`** special folder for exactly this:
with the `Files.ReadWrite.AppFolder` scope the app sees only that folder, and the
user sees it under *Apps*. Least privilege in practice.

## Reach the app folder

Special folders are named, not pathed — reach them through the `special` collection.

```python
app_folder = client.me.drive.special["approot"].get().execute_query()
print(app_folder.name, app_folder.web_url)
```

→ [`app_folder.py`](./app_folder.py)

## Store app state in it

Everything under `approot` is scoped to your app.

```python
app_folder.upload("state.json", b'{"enabled": true}').execute_query()
```

> Requires the delegated `Files.ReadWrite.AppFolder` scope (not `Files.ReadWrite`).

https://learn.microsoft.com/en-us/onedrive/developer/rest-api/concepts/special-folders-appfolder
