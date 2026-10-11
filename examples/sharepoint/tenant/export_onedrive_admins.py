"""
Export the site collection admins of every OneDrive (personal site) to CSV.

Audits which admins have access to which user OneDrives — useful after
restructures, for least-privilege reviews, and security audits. Read-only.

Requires delegated permission ``Sites.FullControl.All`` (or a SharePoint /
Global admin account) on the admin site.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/tenant/administrator-sitecollections-get
"""

import argparse
import tempfile
from pathlib import Path
from urllib.parse import urlparse

from office365.runtime.converters.csv_writer import write_records
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.tenant.administration.tenant import Tenant
from tests.settings import admin_site_url, client_id, password, tenant, username

COLUMNS = ["Url", "Title", "SiteCollectionAdmin", "SiteCollectionAdminName"]


def is_onedrive_url(url: str) -> bool:
    """Whether a site URL belongs to a OneDrive (personal site) host."""
    host = urlparse(url).netloc.lower()
    return host.endswith("-my.sharepoint.com") or "/personal/" in url


def main():
    parser = argparse.ArgumentParser(description="Export OneDrive site collection admins to CSV")
    parser.add_argument(
        "--output", default=str(Path(tempfile.gettempdir()) / "onedrive_admins.csv"), help="output CSV file"
    )
    args = parser.parse_args()

    ctx = ClientContext(admin_site_url).with_username_and_password(
        tenant=tenant, client_id=client_id, username=username, password=password
    )
    admin = Tenant(ctx)

    sites = admin.get_site_properties_from_sharepoint().execute_query()
    onedrives = [s for s in sites if s.url and is_onedrive_url(s.url)]
    print(f"OneDrive sites: {len(onedrives)}")

    # queue one GetSiteAdministrators query per site and run them in a single batch
    results = [admin.get_site_administrators(s.get_property("SiteId")) for s in onedrives]
    ctx.execute_batch()

    records = []
    for s, result in zip(onedrives, results):
        for info in result.value:
            records.append(
                {
                    "Url": s.url,
                    "Title": s.title or "",
                    "SiteCollectionAdmin": info.email or info.loginName or "",
                    "SiteCollectionAdminName": info.name or "",
                }
            )

    with open(args.output, "w", newline="") as f:
        write_records(records, f, columns=COLUMNS)

    print(f"✓ Exported {len(records)} admin assignment(s) to {args.output}")


if __name__ == "__main__":
    main()
