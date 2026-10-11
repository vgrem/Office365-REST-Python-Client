# Working with folders

A folder is a `DriveItem` with a `folder` facet and a `children` collection.
Create, navigate, walk and move trees — every example uses throwaway folders and
cleans up. Requires `Files.ReadWrite` (`Files.Read` to only list).

## Create and navigate

```python
root = client.me.drive.root
docs = root.create_folder("Docs").execute_query()
docs = docs.get().execute_query()  # load it
nested = docs.create_folder("2024/Q1").execute_query()
item = root.get_by_path("Docs/2024/Q1").get().execute_query()
```

→ [`manage.py`](./manage.py) · [`create_nested.py`](./create_nested.py)

## List a tree

`children` pages automatically as you iterate; recurse to walk everything.

```python
def walk(item):
    for child in item.children.get().execute_query():
        yield child
        if child.is_folder:
            yield from walk(child)
```

→ [`list_recursive.py`](./list_recursive.py)

## Upload / download a whole tree

```python
root.upload_folder("local-dir").execute_query()  # up
root.download("local-dir.zip").execute_query()  # down (zip)
```

→ [`upload_folder.py`](./upload_folder.py) · [`download_folder.py`](./download_folder.py) · parallel: [`../../patterns/large-data/download_parallel.py`](../../patterns/large-data/download_parallel.py)

## Move, rename, delete

```python
folder.move(destination).execute_query()
folder.set_property("name", "renamed").update().execute_query()
folder.delete_object().execute_query()
```

→ [`move_delete.py`](./move_delete.py)
