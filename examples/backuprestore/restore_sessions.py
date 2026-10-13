"""
List the restore sessions of every Backup Storage workload.

A restore session groups the artifacts to restore and tracks the asynchronous
restore job (``draft`` -> ``activating`` -> ``active`` -> ``completed``). The
``activate`` action starts a draft session; it is a no-op unless ``--apply`` is
given.

Requires delegated or application permission ``BackupRestore-Control.Read.All``
(``ReadWrite.All`` to activate). On an unlicensed tenant the call is denied and a
short license hint is printed.

https://learn.microsoft.com/en-us/graph/api/backuprestoreroot-list-restoresessions
"""

from __future__ import annotations

import argparse
from typing import Sequence

from office365.common.restore_session_base import RestoreSessionBase
from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, client_secret, tenant


def _print_sessions(label: str, sessions: Sequence[RestoreSessionBase]) -> None:
    print(f"{label} ({len(sessions)}):")
    for session in sessions:
        counts = session.restore_session_artifact_count
        print(f"  {session.id}  status={session.status}  job={session.restore_job_type}")
        print(f"      artifacts: {counts.completed}/{counts.total} completed, {counts.failed} failed")
        print(f"      created={session.created_date_time}  completed={session.completed_date_time}")


def _run(client: GraphClient, args: argparse.Namespace) -> None:
    backup = client.solutions.backup_restore
    _print_sessions(
        "OneDrive for Business restore sessions",
        list(backup.onedrive_for_business_restore_sessions.get().execute_query()),
    )
    _print_sessions("SharePoint restore sessions", list(backup.sharepoint_restore_sessions.get().execute_query()))
    _print_sessions("Exchange restore sessions", list(backup.exchange_restore_sessions.get().execute_query()))

    if args.activate:
        session = backup.restore_sessions[args.activate]
        if args.apply:
            session.activate().execute_query()
            print(f"\nActivated restore session {args.activate}.")
        else:
            print(f"\nDry run. Would POST activate for restore session {args.activate}.")


def main() -> None:
    parser = argparse.ArgumentParser(description="List (and activate) Backup Storage restore sessions")
    parser.add_argument("--activate", metavar="RESTORE_SESSION_ID", help="Activate this restore session")
    parser.add_argument("--apply", action="store_true", help="Actually activate the restore session")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    try:
        _run(client, args)
    except ClientRequestException as err:
        print("Microsoft 365 Backup Storage is not available on this tenant.")
        print("It is a paid add-on and must be enabled; see README.md -> 'Licensing'.")
        print(f"\nServer response: {err}")


if __name__ == "__main__":
    main()
