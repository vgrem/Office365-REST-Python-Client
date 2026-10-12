# Plans

A **plan** is the top-level container: it belongs to a Microsoft 365 group and
holds the board's buckets and tasks. Each plan also has a **details** object that
stores up to 25 category labels (the color tags shown on tasks). Creating a plan
requires **`Group.ReadWrite.All`**.

## Create, rename and delete

A plan is created for a group. Deleting it removes its buckets and tasks too, and
needs the plan's latest etag — the library sends it for you.

```python
group = client.groups.filter("groupTypes/any(a:a eq 'unified')").top(1).get().execute_query()[0]
plan = client.planner.plans.add("Sprint 7", group).execute_query()
plan.title = "Sprint 7 (renamed)"
plan.update().execute_query()
plan.delete_object().execute_query()
```

→ [`lifecycle.py`](./lifecycle.py)

## Category labels

The plan details hold the category labels (`category1` … `category25`).

```python
details = plan.details.get().execute_query()
details.category_descriptions = PlannerCategoryDescriptions(category1="Urgent", category2="Client")
details.update().execute_query()
```

→ [`details.py`](./details.py)

## Provision a whole plan

`provision.py` combines everything: create the plan, label its categories, add
buckets, then create tasks with priorities, category tags and assignments — the
"sprint setup" pattern.

→ [`provision.py`](./provision.py)
