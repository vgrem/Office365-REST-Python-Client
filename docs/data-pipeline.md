# Data pipeline

Move tabular data between Microsoft 365 and the Python data stack (pandas, CSV,
Parquet, SQL, ...). The same surface works on every collection — SharePoint
lists, Entra users/groups, Teams, OneDrive drives — and shares its engine with
the [migration toolkit](https://github.com/vgrem/office365-rest-python-client/tree/master/office365/migration).

## The model

| Object | Meaning | Import | Export |
|---|---|---|---|
| **Collection** (list, users, ...) | a *table* | `from_*` / `queue_*` | `to_*` / `export_to` |
| **File / Folder** | a *blob* (content) | `read_dataframe` | `write_dataframe` |

Two rules keep the names predictable:

- **`from_*` is streaming** (returns an `ImportResult` — bounded, resumable,
  idempotent); **`queue_*` is deferred** queue-all (run with `execute_query()`).
- Collections use `to_*`/`from_*`; files/folders use `read_*`/`write_*` and act on
  a file's **content** (metadata stays as plain properties).

## Quick start

```python
import pandas as pd
from office365.sharepoint.client_context import ClientContext

ctx = ClientContext(site_url).with_username_and_password(tenant, client_id, username, password)
lst = ctx.web.lists.ensure_list("Stocks").execute_query()

# DataFrame -> list (streaming, bounded, resumable, idempotent)
lst.from_dataframe(pd.read_csv("stocks.csv", chunksize=2000), key=["Name", "date"]).execute_batch(concurrency=5)

# list -> DataFrame
df = lst.to_dataframe().execute_query().value
```

## Formats

`csv`, `tsv`, `json` (array), `ndjson`, `excel`, `parquet`, `orc`, `feather`,
`dataframe` — plus `from_sql`/`to_sql` and `from_duckdb`/`to_duckdb` for
databases. Optional dependencies are extras: `[pandas]`, `[excel]`, `[parquet]`,
`[sql]`, `[duckdb]`.

Every reader/writer accepts a **path**, a `PathLike` or an open **file object**:

```python
lst.from_csv("stocks.csv")  # path
lst.from_csv(open("stocks.csv"))  # file object
lst.to_parquet("stocks.parquet").execute_query()
```

Streaming databases (bounded memory):

```python
lst.from_sql("postgresql://...", query="SELECT * FROM stocks", chunksize=5000).execute_batch(concurrency=5)

lst.from_duckdb(duckdb.connect("analytics.db"), query="SELECT * FROM stocks").execute_batch(concurrency=5)
```

## Idempotency

Pass a natural `key` to make an import duplicate-proof: a SHA-256 hash of the
key column(s) is stored in a `MigrationKey` column (created automatically) and
already-present rows are skipped (`on_conflict="skip"`) or updated
(`on_conflict="update"`). The key is checked on **every** run — fresh or resumed —
so a replayed or overlapping chunk never duplicates.

```python
lst.from_dataframe(df, key=["region", "date"], on_conflict="update").execute_batch()
```

For long runs, add a `checkpoint`: the committed cursor is persisted after each
chunk and a source **signature** (format, chunk size, key columns) is recorded.
If the signature changes between runs, the chunk skip is discarded and the source
is re-scanned — the key keeps it duplicate-free.

```python
lst.from_dataframe(
    pd.read_csv("stocks.csv", chunksize=2000),
    key=["Name", "date"],
    checkpoint="stocks.run.json",
    on_error="collect",
    dead_letter="stocks.bad.jsonl",
).execute_batch(concurrency=5)
```

## Typed columns

`List.from_dataframe`/`from_records` provision columns from the dtypes, or from an
explicit `schema={column: FieldType}`. A `FieldType` also drives **value
coercion** (multi-choice, lookup, user, URL, geolocation, ...):

```python
from office365.sharepoint.fields.type import FieldType

lst.from_dataframe(
    df,
    schema={
        "Status": FieldType.Choice,
        "Tags": FieldType.MultiChoice,  # "a; b" or a list
        "Owner": FieldType.User,  # email or {LookupId}
        "Link": FieldType.URL,  # "https://..." or (url, description)
    },
)
```

## Files (document libraries)

```python
folder = ctx.web.lists.get_by_title("Documents").root_folder

# DataFrame -> library file (content)
folder.write_dataframe("stocks.csv", df).execute_query()

# library file -> DataFrame (content)
df = folder.read_dataframe("stocks.csv").execute_query().value
df = file.read_dataframe(format="parquet").execute_query().value

# library file -> list (streaming, idempotent)
lst.from_file("Shared Documents/stocks.csv", key=["Name", "date"]).execute_batch()
```

CSV is written UTF-8 with a BOM so Excel keeps the columns.

## Streaming export

Export a large list without loading it all:

```python
lst.export_to("stocks.csv", page_size=2000).execute_query()  # CSV/TSV/NDJSON/JSON
```

`page_size` streams appendable formats page by page; other formats fall back to a
whole-collection write.

From `async` code the same export is awaitable — each page is fetched and written
on the worker pool, so the event loop stays free ([async guide](async.md#streaming-export)):

```python
await lst.export_to_async("stocks.csv", page_size=2000)
```

## Errors & verification

- `on_error="collect"` records a failing chunk and continues. With a
  `dead_letter` path the chunk is executed record-by-record, so each failing row
  is appended as `{"row", "error", "record"}` for remediation.
- Verify a keyed import against the target:

```python
report = lst.verify(df, key=["Name", "date"])
assert report.ok, report.summary()  # counts + missing keys
```

## Migration parity

The streaming import and the migration toolkit share the engine (`keyed_queue`,
`UpsertTarget`, `Progress`, `OperationStats`) and one `VerificationReport`:

```python
result = lst.from_dataframe(df, key=["id"])
result.run(concurrency=5)  # == execute_batch
report = result.verify(df, key=["id"])
```

### Async

The import terminals gain awaitable twins — the same chunking, checkpointing,
dead-letter and `progress` semantics, only the wait differs:

```python
result = lst.from_dataframe(df, key=["id"])
await result.execute_query_async()  # sequential, awaited
await result.execute_batch_async(concurrency=5)  # server-side batches
await result.run_async(concurrency=5)  # == execute_batch_async
```

`async for chunk in result:` mirrors the sync iteration for callers that drive
execution themselves.
