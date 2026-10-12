# Shared mailboxes

A shared mailbox is just another mailbox addressed by its UPN. Read it, send
from it, or send *as* it. Part of the [Outlook tour](../README.md), which has the
shared-mailbox model and permissions.

| What | File | Notes |
|------|------|-------|
| Read a shared mailbox | [`access_mailbox.py`](./access_mailbox.py) | Messages and folders by UPN |
| Send as the shared mailbox | [`send_as.py`](./send_as.py) | `From` is the shared mailbox |
| Find shared mailboxes | [`list_shared_mailboxes.py`](./list_shared_mailboxes.py) | By convention — Graph has no endpoint |
| Shared-mailbox report | [`report.py`](./report.py) | Tenant inventory |
