# Notebooks

A **notebook** is the root of the OneNote tree and the only resource created
without a parent. Its name must be unique for the signed-in user. Requires
`Notes.ReadWrite` (`Notes.Create` is enough to create), `Notes.Read` to only
list.

## Create one

The name must be unique; pass a timestamped `--name` to keep reruns from
colliding. Graph has **no delete-notebook operation**, so create these
deliberately.

```python
notebook = client.me.onenote.notebooks.add("Project X").execute_query()
print(notebook.links.oneNoteWebUrl.href)
```

→ [`create.py`](./create.py)

## List your recent ones

`getRecentNotebooks` returns the notebooks you opened most recently — the fastest
way to build a "jump back in" list without walking the tree.

```python
recent = client.me.onenote.notebooks.get_recent_notebooks(True).execute_query()
for item in recent.value:
    print(item.displayName, item.lastAccessedTime)
```

→ [`recent.py`](./recent.py)

## Provision one from a template

Lay down the same sections and starter pages every time. The script is
idempotent — an existing section is reused by name, and its starter page is only
added when the section is still empty — so running it again changes nothing.

```python
section = notebook.sections.first_or_none("displayName eq 'Meeting Notes'").execute_query()
if not section.is_loaded:
    section = notebook.sections.add(displayName="Meeting Notes").execute_query()
section.pages.add(presentation_file="<html><head><title>Meeting Notes</title></head><body/></html>").execute_query()
```

→ [`provision.py`](./provision.py)
