# Working with Excel workbooks

An `.xlsx` in a drive is a **workbook** you can drive server-side — read and write
tables, ranges and formulas without downloading it. Workbook work is
session-oriented and, for some operations, asynchronous. Requires
`Files.ReadWrite`.

## Read data

```python
book = client.me.drive.root.get_by_path("report.xlsx").get().execute_query()
worksheet = book.workbook.worksheets["Sheet1"]
table = worksheet.tables["Revenue"].get().execute_query()
rows = table.rows.get().execute_query()
```

→ [`read_table.py`](./read_table.py) · [`worksheets.py`](./worksheets.py)

## Write data

```python
worksheet.range("A1:B2").set(...).execute_query()  # or add a table/row
worksheet.tables.add("Revenue", "A1:C10").execute_query()
```

→ [`tables.py`](./tables.py) · [`ranges.py`](./ranges.py) · [`formulas.py`](./formulas.py)

## Workbook sessions

Group edits into a session so the file isn't saved after every change (and to
avoid conflicts). Close the session to persist.

```python
session = book.workbook.create_session().execute_query()
# ... many edits ...
book.workbook.close_session(session.id).execute_query()
```

→ [`workbook_sessions.py`](./workbook_sessions.py)

> Some workbook actions are long-running — poll them like any other operation
> ([patterns/lro](../../patterns/lro/)).
