"""Search a keyword across all drives in the tenant.

Runs ``drive.search`` once per drive (personal OneDrive and SharePoint
document libraries) and aggregates the matches. Note this issues one request
per drive, so it can be slow on large tenants - use ``--max-drives`` to cap it.

Requires application permissions ``Files.Read.All`` and ``Sites.Read.All``.

https://learn.microsoft.com/en-us/graph/api/driveitem-search
"""

import argparse

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant


def main():
    parser = argparse.ArgumentParser(description="Search a keyword across all tenant drives")
    parser.add_argument("query", help="search term")
    parser.add_argument("--max-drives", type=int, default=0, help="max drives to scan, 0 = all (default: 0)")
    args = parser.parse_args()

    client = (
        GraphClient(tenant=tenant)
        .with_client_secret(client_id, client_secret)
        .require_application_permission("Files.Read.All", "Sites.Read.All")
    )

    drives = client.drives.get().execute_query()
    if args.max_drives > 0:
        drives = list(drives)[: args.max_drives]

    found = 0
    for drive in drives:
        drive_name = drive.properties.get("name") or drive.id or "?"
        for item in drive.search(args.query).execute_query():
            found += 1
            print(f"  {drive_name}: {item.name}  ({item.size or 0:,} bytes)")

    print(f"\n{found} match(es) for '{args.query}' across {len(drives)} drive(s)")


if __name__ == "__main__":
    main()
