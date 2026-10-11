"""
Get a site by its server-relative path (no full URL required).

Requires delegated permission ``Sites.Read.All``.

https://learn.microsoft.com/en-us/graph/api/site-getbypath
"""

import argparse

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant


def main():
    parser = argparse.ArgumentParser(description="Get a site by its server-relative path")
    parser.add_argument("--path", required=True, help="Server-relative path (e.g. /sites/project)")
    args = parser.parse_args()

    client = (
        GraphClient(tenant=tenant)
        .with_client_secret(client_id, client_secret)
        .require_application_permission("Sites.Read.All")
    )

    path = args.path.strip()
    site = client.sites.get_by_path(path).execute_query()
    print(f"Site: {site.display_name}  ({site.web_url})")


if __name__ == "__main__":
    main()
