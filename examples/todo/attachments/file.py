"""
Attach a file to a Microsoft To Do task.

Small files (<= 3 MB) are posted directly; larger ones (up to 25 MB) use an
upload session with chunked ``PUT`` requests. ``TodoTask.upload_attachment``
picks the right path automatically.

    python attachments.py --list-id AAMk... --task-id AAMk... --file ./report.pdf

Requires delegated permission ``Tasks.ReadWrite``.

https://learn.microsoft.com/en-us/graph/api/todotask-post-attachments
https://learn.microsoft.com/en-us/graph/api/taskfileattachment-createuploadsession
"""

import argparse

from office365.graph_client import GraphClient
from tests.settings import client_id, password, tenant, username


def main():
    parser = argparse.ArgumentParser(description="Attach a file to a To Do task")
    parser.add_argument("--list-id", required=True, help="todoTaskList id")
    parser.add_argument("--task-id", required=True, help="todoTask id")
    parser.add_argument("--file", required=True, help="path to the file to attach")
    parser.add_argument("--name", default=None, help="attachment display name (default: file name)")
    parser.add_argument("--content-type", default=None, help="MIME type, e.g. application/pdf")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    task = client.me.todo.lists[args.list_id].tasks[args.task_id].get().execute_query()

    attachment = task.upload_attachment(
        args.file,
        name=args.name,
        content_type=args.content_type,
        progress=lambda p: print(f"  uploaded {p.done}/{p.total} bytes"),
    )
    print(f"Attached '{attachment.name}' ({attachment.size} bytes) to '{task.title}'")


if __name__ == "__main__":
    main()
