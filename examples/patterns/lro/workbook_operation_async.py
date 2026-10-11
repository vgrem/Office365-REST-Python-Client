"""
Submit a workbook session with ``Prefer: respond-async`` and poll it if accepted.

The Excel API lets a caller opt into the long-running-operation pattern: send
``Prefer: respond-async`` and the service may answer ``202 Accepted`` with a
monitor URL instead of holding the request open. ``RespondAsyncRequest`` executes
a *fresh* query with that preference and returns a pollable
``LongRunningOperationResult`` when accepted — or ``None`` when the service
answers synchronously (which is common for a quick session creation). Either
way, the query's return type receives the session.

Requires delegated permission ``Files.ReadWrite``.

https://learn.microsoft.com/en-us/graph/api/workbook-createsession
https://learn.microsoft.com/en-us/graph/api/resources/workbookoperation
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from office365.graph_client import GraphClient
from office365.onedrive.workbooks.session_info import WorkbookSessionInfo
from office365.runtime.client_result import ClientResult
from office365.runtime.lro import OperationStatus
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.respond_async import RespondAsyncRequest
from tests.settings import client_id, password, tenant, username

SAMPLE_WORKBOOK = Path(__file__).resolve().parents[1] / "data" / "Financial Sample.xlsx"


def report(status: OperationStatus) -> None:
    pct = f"{status.percentage_complete:5.1f}%" if status.percentage_complete is not None else "  ..."
    print(f"\r  {pct}  {status.status or status.http_status}", end="", flush=True)


async def main() -> None:
    parser = argparse.ArgumentParser(description="Create a workbook session via respond-async")
    parser.add_argument("--keep", action="store_true", help="keep the uploaded workbook")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_username_and_password(client_id, username, password)
    async with client:
        uploaded = await client.me.drive.root.upload_file(str(SAMPLE_WORKBOOK)).execute_query_async()
        workbook = uploaded.workbook

        # Build a fresh createSession query and submit it with Prefer: respond-async.
        session = ClientResult(workbook.context, WorkbookSessionInfo())
        query = ServiceOperationQuery(workbook, "createSession", None, {"persistChanges": True}, None, session)
        operation = await RespondAsyncRequest(workbook.context, query, wait=5).execute_async()

        if operation is not None:
            print(f"Accepted (202); polling {operation.monitor_url} ...")
            await operation.wait_async(on_progress=report)
            print()
        else:
            print("Answered synchronously.")

        session_id = session.value.id
        if not session_id:
            parser.error("No session id returned")
        print(f"Session: {session_id}")

        await workbook.close_session(session_id).execute_query_async()
        print("Session closed.")

        if not args.keep:
            await uploaded.delete_object().execute_query_async()
            print("Workbook deleted.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(130)
