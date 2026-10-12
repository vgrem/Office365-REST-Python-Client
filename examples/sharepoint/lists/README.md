# Lists

A **list** is a container for rows of data, like a database table.
A **document library** is a special kind of list that also stores files.
Every list has a title and a unique ID (GUID).

---

## Prerequisites

| Requirement | Description | Reference |
|---|---|---|
| **Site Owner** or **Member** role | Required to create, update, and delete lists. Read access for browsing. | [SharePoint admin roles](https://learn.microsoft.com/en-us/sharepoint/sharepoint-admin-role) |

---

## How lists work

```mermaid
graph TD
    Site["SharePoint Site"]
    Site --> List["List"]
    Site --> Lib["Document Library"]
    List --> Fields["Fields (Columns)"]
    List --> Items["List Items"]
    Lib --> Files["Files"]
    Lib --> Fields
```

---

## Examples

### Create and manage

| Operation | File | Required role | API reference |
|---|---|---|---|
| Create a list | [`create.py`](./create.py) | Member on site | [Lists REST API](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/working-with-lists-and-list-items-with-rest) |
| Update list properties | [`update_list.py`](./update_list.py) | Member on site | [Lists REST API](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/working-with-lists-and-list-items-with-rest) |
| Delete a list | [`delete.py`](./delete.py) | Member on site | [Lists REST API](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/working-with-lists-and-list-items-with-rest) |
| Save as template | [`save_as_template.py`](./save_as_template.py) | Member on site | [Lists REST API](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/working-with-lists-and-list-items-with-rest) |
| Clear all items | [`clear.py`](./clear.py) | Member on site | [Lists REST API](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/working-with-lists-and-list-items-with-rest) |
| Show or hide columns | [`show_hide_columns.py`](./show_hide_columns.py) | Member on site | [Lists REST API](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/working-with-lists-and-list-items-with-rest) |

### Read and browse

| Operation | File | Required role | API reference |
|---|---|---|---|
| Read list properties | [`read_properties.py`](./read_properties.py) | Read access | [Lists REST API](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/working-with-lists-and-list-items-with-rest) |
| Read list schema | [`read_schema.py`](./read_schema.py) | Read access | [Lists REST API](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/working-with-lists-and-list-items-with-rest) |
| Read all lists on site | [`read_all.py`](./read_all.py) | Read access | [Lists REST API](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/working-with-lists-and-list-items-with-rest) |
| Read with paging | [`read_paged.py`](./read_paged.py) | Read access | [Lists REST API](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/working-with-lists-and-list-items-with-rest) |
| Read with progress bar | [`read_with_progress.py`](./read_with_progress.py) | Read access | [Lists REST API](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/working-with-lists-and-list-items-with-rest) |
| Get list storage size | [`read_lib_size.py`](./read_lib_size.py) | Read access | [Lists REST API](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/working-with-lists-and-list-items-with-rest) |
| Get changes (change log) | [`get_changes.py`](./get_changes.py) | Read access | [Lists REST API](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/working-with-lists-and-list-items-with-rest) |
| Get data as stream | [`get_data_as_stream.py`](./get_data_as_stream.py) | Read access | [Lists REST API](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/working-with-lists-and-list-items-with-rest) |
| Export a large list to JSONL (async, resumable) | [`export_large_list_async.py`](./export_large_list_async.py) | Read access | [Lists REST API](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/working-with-lists-and-list-items-with-rest) |
| Export list metadata (XML) | [`export_list.py`](./export_list.py) | Read access | [Lists REST API](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/working-with-lists-and-list-items-with-rest) |
| Export data as records / CSV / NDJSON / Excel | [`export_records.py`](./export_records.py) | Read access | Data pipeline |
| Query a large list (indexed + paged CAML, >5k rows) | [`query_large_list.py`](./query_large_list.py) | Read access | [Lists REST API](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/working-with-lists-and-list-items-with-rest) |

### Import, filter, and query

| Operation | File | Required role | API reference |
|---|---|---|---|
| Import from CSV | [`import_csv.py`](./import_csv.py) | Member on list | [Lists REST API](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/working-with-lists-and-list-items-with-rest) |
| Import from JSON file (round trip) | [`import_export_json_file.py`](./import_export_json_file.py) | Member on list | [Lists REST API](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/working-with-lists-and-list-items-with-rest) |
| ETL pipeline (extract/transform/load) | [`data_pipeline.py`](./data_pipeline.py) | Member on list | [Lists REST API](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/working-with-lists-and-list-items-with-rest) |
| Bulk create (sequential batches) | [`import_list.py`](./import_list.py) | Member on list | [Lists REST API](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/working-with-lists-and-list-items-with-rest) |
| Import from GitHub into library | [`import_lib.py`](./import_lib.py) | Member on library | [Lists REST API](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/working-with-lists-and-list-items-with-rest) |
| Filter with OData | [`read_items_with_filter.py`](./read_items_with_filter.py) | Read access | [Lists REST API](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/working-with-lists-and-list-items-with-rest) |
| Filter with CAML | [`read_items_with_caml_query.py`](./read_items_with_caml_query.py) | Read access | [Lists REST API](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/working-with-lists-and-list-items-with-rest) |
| Filter list collection | [`filter.py`](./filter.py) | Read access | [Lists REST API](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/working-with-lists-and-list-items-with-rest) |
| Parallel import (concurrent batches) | [`import_list_parallel.py`](./import_list_parallel.py) | Member on list | [Lists REST API](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/working-with-lists-and-list-items-with-rest) |

### Pandas DataFrame

| Operation | File | Required role | Notes |
|---|---|---|---|
| Import DataFrame | [`from_dataframe.py`](./from_dataframe.py) | Member on list | Columns provisioned from dtypes |
| Import large DataFrame (fast) | [`from_dataframe_large.py`](./from_dataframe_large.py) | Member on list | Chunked memory slices + `execute_batch` concurrency |
| Import a library file (CSV/XLSX) | [`from_file.py`](./from_file.py) | Member on list | Downloads + streams; idempotent with `--key` |
| Export list to DataFrame | [`export_dataframe.py`](./export_dataframe.py) | Read access | `to_dataframe()` |

Requires `pip install office365-rest-python-client[pandas]`.

---

## Quick start

```python
from office365.sharepoint.client_context import ClientContext

ctx = ClientContext("https://contoso.sharepoint.com/sites/team").with_client_certificate(
    "contoso.onmicrosoft.com", client_id="client_id", thumbprint="thumbprint", cert_path="./cert.pem"
)

# Read all lists on the site
all_lists = ctx.web.lists.get().execute_query()
for l in all_lists:
    print(f"  {l.title}  (ID: {l.id})")

# Get a specific list by title
target = ctx.web.lists.get_by_title("Documents").get().execute_query()
print(f"Items: {target.item_count}, Fields: {len(target.fields)}")
```

---

## Related recipes

- [Provision a project workspace](../recipes/provision_project_workspace.py) — a document library with typed columns plus a task list and starter rows.

---

## API reference

- [Working with lists, SharePoint REST API](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/working-with-lists-and-list-items-with-rest)
