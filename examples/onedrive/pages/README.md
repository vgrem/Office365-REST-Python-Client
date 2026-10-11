# Working with site pages

A **site page** is a modern page: a title area, a layout of sections, and web
parts placed on a canvas. Pages have a publishing lifecycle (draft → check in →
publish). These examples cover that lifecycle and the web-part model, and clean
up after themselves. Requires `Sites.ReadWrite.All` (`Sites.Read.All` to read).

## The page lifecycle

```python
site = client.sites.get_by_path("/sites/marketing").get().execute_query()
page = site.pages.add("Announcement", "hello world").execute_query()
page.publish().execute_query()
page.delete_object().execute_query()
```

→ [`manage.py`](./manage.py) · [`list_pages.py`](./list_pages.py) (with publishing state)

## Check in and publish

```python
page.checkout().execute_query()
page.set_property("title", "Updated").update().execute_query()
page.checkin("edited").execute_query()
page.publish().execute_query()
```

→ [`publish_flow.py`](./publish_flow.py)

## Web parts & layout

Inspect (or build) the canvas: sections, columns and the web parts inside them.

```python
for section in page.canvas_layout.horizontal_sections:
    for column in section.columns:
        for part in column.webparts:
            print(part.web_part_type, part.data)
```

→ [`webparts.py`](./webparts.py)
