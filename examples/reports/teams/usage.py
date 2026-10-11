"""
Teams usage — team counts and user activity.

Two complementary views:

* **team counts** — how many public/private teams exist, and how many were
  active (had any activity) each day;
* **user activity** — unique users per activity type: team chat messages,
  private chat messages, calls and meetings.

A period with no Teams activity is normal in a small tenant; the script says so
instead of printing an empty table.

    python usage.py
    python usage.py --period D90

Requires application permission ``Reports.Read.All`` (delegated works too).

https://learn.microsoft.com/en-us/graph/api/reportroot-getteamsteamcounts
https://learn.microsoft.com/en-us/graph/api/reportroot-getteamsuseractivityusercounts
"""

from __future__ import annotations

import argparse
import csv
import io

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant


def _rows(result) -> list[dict]:
    """Decode a report result into CSV rows (the CSV carries a UTF-8 BOM)."""
    value = result.value
    text = value.decode("utf-8-sig") if isinstance(value, bytes) else (value.content or b"").decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(text)))


def _int(value) -> int:
    try:
        return int(value or 0)
    except ValueError:
        return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Teams team counts and user activity")
    parser.add_argument("--period", default="D30", help="Aggregation period: D7/D30/D90/D180 (default: D30)")
    args = parser.parse_args()

    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)
    teams = _rows(client.reports.get_teams_team_counts(args.period).execute_query())
    users = _rows(client.reports.get_teams_user_activity_user_counts(args.period).execute_query())

    if teams:
        latest = max(teams, key=lambda r: r.get("Report Date") or "")
        print(f"Teams ({latest.get('Report Date')}):")
        print(f"  public   {_int(latest.get('PublicTeams')):>5,}  ({_int(latest.get('ActivePublicTeams')):>4,} active)")
        print(
            f"  private  {_int(latest.get('PrivateTeams')):>5,}  ({_int(latest.get('ActivePrivateTeams')):>4,} active)"
        )
    else:
        print("Teams: no data for the period")

    if not users:
        print("\nUser activity: no Teams activity in the period")
        return

    print(f"\nUser activity ({args.period}) — {len(users)} day(s)")
    activity_columns = [c for c in users[0] if c not in ("Report Refresh Date", "Report Date", "Report Period")]
    totals = dict.fromkeys(activity_columns, 0)
    for row in users:
        for column in activity_columns:
            totals[column] += _int(row.get(column))
    peak = {column: max((_int(r.get(column)) for r in users), default=0) for column in activity_columns}
    for column in activity_columns:
        print(f"  {column:24s} peak {peak[column]:>5,}   total {totals[column]:>7,}")


if __name__ == "__main__":
    main()
