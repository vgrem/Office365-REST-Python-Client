# Working with the term store

The **term store** is the managed-metadata service: a hierarchy of
**groups → sets → terms** shared across SharePoint and OneDrive for consistent
tagging. These examples build taxonomy, search it, export/import it, and clean
up. Requires `TermStore.ReadWrite.All` (`TermStore.Read.All` to read).

## Walk and create taxonomy

```python
store = client.term_store.get().execute_query()
group = store.groups.add("Departments").execute_query()
term_set = store.sets.add("Geography", group.id).execute_query()
term = store.sets.get_by_id(term_set.id).children.add("EMEA").execute_query()
```

→ [`create_terms.py`](./create_terms.py) · [`search_term.py`](./search_term.py)

## Export / import the hierarchy

Round-trip the whole taxonomy to JSON — a backup, or a promotion between tenants.

```python
tree = store.export()  # serialize groups → sets → terms
store.import_hierarchy(tree).execute_query()  # recreate it
```

→ [`export_store.py`](./export_store.py) · [`export_tree.py`](./export_tree.py) · [`import_store.py`](./import_store.py)

## Clean up

```python
for group in store.groups.get().execute_query():
    group.delete_object().execute_query()
```

→ [`clear_store.py`](./clear_store.py)
