# Reports

Reporting walks the plans you can access (`me/planner/plans`) and their tasks —
no writes. Both scripts are read-only and require `Tasks.ReadWrite` or
`Group.Read.All`.

## Overdue and due-soon tasks

Groups the incomplete tasks past (or close to) their due date by assignee:

```bash
python overdue.py --days-ahead 7
```

→ [`overdue.py`](./overdue.py)

## Progress dashboard

A per-task and aggregate breakdown by percent complete and priority:

```bash
python ../tasks/progress_report.py
```

→ [`../tasks/progress_report.py`](../tasks/progress_report.py)
