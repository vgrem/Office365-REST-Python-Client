"""
Any usage report, in one tool — explore the Reports API.

Every Microsoft 365 usage report is a CSV behind the same endpoint shape. This
script is a generic explorer over all of them: pick a report and a period, print
it as a table, and optionally save the raw CSV. When you find a report you use
regularly, reach for its dedicated example instead.

    python usage_reports.py --list
    python usage_reports.py --report mailbox_usage_detail --period D7
    python usage_reports.py --report team_counts --csv

Requires application permission ``Reports.Read.All`` (delegated works too).

https://learn.microsoft.com/en-us/graph/api/resources/report
"""

from __future__ import annotations

import argparse
import csv
import io
import tempfile
from pathlib import Path

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant

# Report name -> Reports API method. Day-based report methods take a period.
REPORTS = {
    "email_activity_counts": "get_email_activity_counts",
    "email_activity_user_counts": "get_email_activity_user_counts",
    "email_activity_user_detail": "get_email_activity_user_detail",
    "email_app_usage_apps_user_counts": "get_email_app_usage_apps_user_counts",
    "email_app_usage_user_counts": "get_email_app_usage_user_counts",
    "email_app_usage_user_detail": "get_email_app_usage_user_detail",
    "mailbox_usage_storage": "get_mailbox_usage_storage",
    "mailbox_usage_detail": "get_mailbox_usage_detail",
    "mailbox_usage_mailbox_counts": "get_mailbox_usage_mailbox_counts",
    "mailbox_usage_quota_status_mailbox_counts": "get_mailbox_usage_quota_status_mailbox_counts",
    "m365_app_user_counts": "get_m365_app_user_counts",
    "m365_app_user_detail": "get_m365_app_user_detail",
    "office365_activation_counts": "get_office365_activation_counts",
    "office365_activations_user_counts": "get_office365_activations_user_counts",
    "onedrive_activity_file_counts": "get_onedrive_activity_file_counts",
    "onedrive_activity_user_counts": "get_onedrive_activity_user_counts",
    "onedrive_activity_user_detail": "get_onedrive_activity_user_detail",
    "onedrive_usage_file_counts": "get_onedrive_usage_file_counts",
    "onedrive_usage_storage": "get_onedrive_usage_storage",
    "sharepoint_activity_pages": "get_sharepoint_activity_pages",
    "sharepoint_activity_user_counts": "get_sharepoint_activity_user_counts",
    "sharepoint_activity_user_detail": "get_sharepoint_activity_user_detail",
    "sharepoint_site_usage_detail": "get_sharepoint_site_usage_detail",
    "sharepoint_site_usage_site_counts": "get_sharepoint_site_usage_site_counts",
    "teams_team_counts": "get_teams_team_counts",
    "teams_user_activity_counts": "get_teams_user_activity_counts",
    "teams_user_activity_user_counts": "get_teams_user_activity_user_counts",
}

# Reports that don't take a period argument.
NO_PERIOD = {"office365_activation_counts"}


def _content(result) -> bytes:
    """Extract the CSV bytes from a report result (raw bytes or Report.content)."""
    value = result.value
    if isinstance(value, bytes):
        return value
    return value.content or b""


def _print_table(rows: list[dict], limit: int) -> None:
    if not rows:
        print("(no rows)")
        return
    columns = list(rows[0].keys())
    print("\t".join(columns))
    for row in rows[:limit]:
        print("\t".join(str(row.get(column) or "") for column in columns))


def main() -> None:
    parser = argparse.ArgumentParser(description="Download and parse any Graph CSV usage report")
    parser.add_argument("--report", choices=sorted(REPORTS), default="email_activity_counts", help="Report to fetch")
    parser.add_argument("--period", default="D30", help="Report period: D7/D30/D90/D180 (default: D30)")
    parser.add_argument("--limit", type=int, default=20, help="Rows to print (default: 20)")
    parser.add_argument(
        "--csv",
        nargs="?",
        const="",
        metavar="PATH",
        help="Write the raw CSV (default: a file in the temp directory)",
    )
    parser.add_argument("--list", action="store_true", help="List available reports and exit")
    args = parser.parse_args()

    if args.list:
        for name in sorted(REPORTS):
            print(name)
        return

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    method = getattr(client.reports, REPORTS[args.report])
    result = method().execute_query() if args.report in NO_PERIOD else method(args.period).execute_query()

    raw = _content(result)
    rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    print(f"{args.report} ({args.period}) — {len(rows)} row(s):\n")
    _print_table(rows, args.limit)

    if args.csv is not None:
        target = Path(args.csv) if args.csv else Path(tempfile.gettempdir()) / f"{args.report}_{args.period}.csv"
        target.write_bytes(raw)
        print(f"\nWrote {target}")


if __name__ == "__main__":
    main()
