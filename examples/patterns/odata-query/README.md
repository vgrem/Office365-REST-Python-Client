# OData query parameters

Shape a request so the service does the work: return fewer fields, filter and
sort server-side, expand a related facet, and page predictably. The same fluent
builders exist on every collection in the SDK.

| Example | Shows |
|---|---|
| [`query_options.py`](./query_options.py) | `$select`, `$filter`, `$orderby`, `$top`, `$expand` on a drive |

```python
items = (
    client.me.drive.root.children.select(["id", "name", "size"])
    .filter("folder eq null")
    .order_by("name")
    .top(50)
    .get()
    .execute_query()
)
```

https://learn.microsoft.com/en-us/graph/query-parameters
