# Working with lists & document libraries

A **list** is tabular data with custom columns; a **document library** is a list
that also acts as a drive. You can reach a library's content as `DriveItem`s *or*
as list items with columns. These examples create throwaway lists and clean up.
Requires `Sites.ReadWrite.All`.

## Create a list with columns

```python
site = client.sites.root
lib = site.lists.add("Projects", ListTemplateType.genericList).execute_query()
lib.columns.add_text("Category").execute_query()
lib.columns.add_number("Budget").execute_query()
```

→ [`create_list.py`](./create_list.py) · [`columns.py`](./columns.py)

## Items: create, read, update, delete

```python
item = lib.items.add(Title="Alpha", Budget=50000).execute_query()
rows = lib.items.expand(["fields"]).get().execute_query()
item.set_property("fields", item.fields).update().execute_query()
```

→ [`manage_items.py`](./manage_items.py)

## Query efficiently

Filter, sort, select and page — server-side (see [OData query parameters](../../patterns/odata-query/)).

```python
rows = (
    lib.items.filter("fields/Budget gt 75000")
    .expand(["fields"])
    .select(["id", "fields/Budget"])
    .top(20)
    .get()
    .execute_query()
)
```

→ [`query_items.py`](./query_items.py)

## A library as a drive

```python
root = lib.drive.root.get().execute_query()
root.upload("readme.txt", b"hello").execute_query()
```

→ [`library.py`](./library.py) · bulk: [`import_export.py`](./import_export.py)
