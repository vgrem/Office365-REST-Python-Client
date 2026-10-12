"""
Microsoft 365 usage at a glance — the five-minute tenant snapshot.

One script, four headline reports: mail volume, mailbox count, OneDrive files and
storage, and Teams. It is the fastest way to confirm ``Reports.Read.All`` works
and to get a feel for a tenant before digging into a specific report.

    python quickstart.py
    python quickstart.py --period D30

Requires application permission ``Reports.Read.All`` (delegated works too).

https://learn.microsoft.com/en-us/graph/api/resources/report
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant

GIB = 1024**3


def _latest(rows: list[dict]) -> dict:
    return max(rows, key=lambda r: r.get("Report Date") or r.get("Report Refresh Date") or "", default={})


def _int(value) -> int:
    try:
        return int(value or 0)
    except ValueError:
        return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Microsoft 365 usage snapshot")
    parser.add_argument("--period", default="D7", help="Aggregation period: D7/D30/D90/D180 (default: D7)")
    args = parser.parse_args()

    reports = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret).reports

    email = _latest(reports.get_email_activity_counts(args.period).execute_query().csv_rows())
    mailboxes = _latest(reports.get_mailbox_usage_mailbox_counts(args.period).execute_query().csv_rows())
    onedrive = _latest(reports.get_onedrive_usage_file_counts(args.period).execute_query().csv_rows())
    storage = _latest(reports.get_onedrive_usage_storage(args.period).execute_query().csv_rows())
    teams = _latest(reports.get_teams_team_counts(args.period).execute_query().csv_rows())

    print(f"Microsoft 365 snapshot ({args.period}, latest reported day)\n")
    if email:
        print(
            f"  Mail        {_int(email.get('Send')):>7,} sent  "
            f"{_int(email.get('Receive')):>7,} received   on {(email.get('Report Date') or '?')[:10]}"
        )
    if mailboxes:
        print(f"  Mailboxes   {_int(mailboxes.get('Total')):>7,} total  {_int(mailboxes.get('Active')):>7,} active")
    if onedrive:
        print(f"  OneDrive    {_int(onedrive.get('Total')):>7,} files  {_int(onedrive.get('Active')):>7,} active")
    if storage:
        print(f"  OneDrive    {float(storage.get('Storage Used (Byte)') or 0) / GIB:>7.2f} GiB stored")
    if teams:
        print(f"  Teams       {_int(teams.get('PublicTeams')):>7,} public {_int(teams.get('PrivateTeams')):>7,} private")


if __name__ == "__main__":
    main()
