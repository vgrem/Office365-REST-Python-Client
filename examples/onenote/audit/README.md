# Auditing the hierarchy

Content discovery, inventory and migration planning all start with the same
question: what is in the tenant, and where? OneNote makes you walk for it —
notebooks contain section groups (which nest), section groups contain sections,
and sections contain pages. This script walks a bounded slice and can emit JSON.
Reads only; requires `Notes.Read`.

## Walk the tree

Recurse through section groups, then read a bounded number of pages per section:

```python
def walk(container):
    for section in container.sections.get().execute_query():
        yield section
    for group in container.section_groups.get().execute_query():
        yield from walk(group)
```

→ [`structure.py`](./structure.py)

```bash
python structure.py --limit 5 --pages 20 --json
```

`--json` writes the tree to `onenote_structure.json` in the temp directory, ready
to feed into a report or a migration script.
