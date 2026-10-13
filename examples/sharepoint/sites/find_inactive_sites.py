"""
Find SharePoint Online sites with no recent content modifications.

Useful for identifying obsolete or abandoned sites that can be removed
or archived. Cross-references site activity dates with owner information
for group-connected sites.

Inspired by the PowerShell script Find-ObsoleteSPOSites.PS1 from
Office 365 for IT Pros (https://github.com/12Knocksinna/Office365itpros).

Required delegated permissions:
    Sites.Read.All           Read site properties (last activity, storage)
    User.Read.All            Read user/group owner information
    Reports.Read.All         (optional) Read usage report for more accurate activity data

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/navigation/site-operations
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.tenant.administration.sites.properties import SiteProperties
from office365.sharepoint.tenant.administration.tenant import Tenant
from tests.settings import admin_site_url, cert_path, cert_thumbprint, client_id, tenant


def get_site_owner(site: SiteProperties, admin: Tenant) -> str:
    """Attempt to resolve the owner of a site.

    For group-connected sites, derives ownership from the Microsoft 365
    Group. For classic sites, falls back to site collection admins.
    """
    try:
        if site.group_owner_login_name:
            return f"Group owner: {site.group_owner_login_name}"
        if site.url is None:
            return "Unknown"
        result = admin.get_site_administrators_by_site_url(site.url).execute_query()
        emails = [a.email for a in result.value if a.email]
        if emails:
            return ", ".join(emails)
    except Exception:
        pass
    return "Unknown"


def find_inactive_sites(days_threshold: int = 90, include_channel_sites: bool = False) -> list[dict]:
    """Find sites without content modifications within *days_threshold*.

    Args:
        days_threshold: Number of days of inactivity to flag a site.
        include_channel_sites: If True, include Teams private/shared channel sites.

    Returns:
        List of dicts with site URL, title, last activity, storage, owner.
    """
    ctx = ClientContext(admin_site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    admin = Tenant(ctx)
    cutoff = datetime.now(timezone.utc) - timedelta(days=days_threshold)

    sites = admin.get_site_properties_from_sharepoint().execute_query()
    results = []

    for site in sites:
        # Skip archived sites
        if site.archive_status == "NotArchived":
            continue

        # Skip Teams channel sites unless explicitly included
        template = site.template or ""
        if not include_channel_sites and template in ("TEAMCHANNEL#0", "TEAMCHANNEL#1"):
            continue

        # Skip redirect sites (placeholders)
        if template == "REDIRECTSITE#0":
            continue

        try:
            if site.url is None:
                continue
            # Get site properties with last activity
            site_props = admin.get_site_properties_by_url(site.url).execute_query()

            last_activity = site_props.last_content_modified_date

            if last_activity is None or last_activity < cutoff:
                results.append(
                    {
                        "url": site.url,
                        "title": site.title,
                        "last_activity": last_activity,
                        "template": template,
                        "storage_used_mb": site.storage_usage or 0,
                        "storage_quota_mb": site.storage_maximum_level or 0,
                        "owner": get_site_owner(site, admin),
                    }
                )
        except Exception as e:
            print(f"  Skipping {site.url}: {e}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Find SharePoint Online sites with no recent content modifications")
    parser.add_argument("--days-threshold", type=int, default=90, help="days of inactivity to flag a site (default: 90)")
    parser.add_argument("--include-channel-sites", action="store_true", help="include Teams channel sites")
    args = parser.parse_args()

    print("Fetching SharePoint Online sites...")
    inactive = find_inactive_sites(days_threshold=args.days_threshold, include_channel_sites=args.include_channel_sites)

    if not inactive:
        print("No inactive sites found.")
        return

    print(f"\nFound {len(inactive)} sites inactive for 90+ days:\n")
    print(f"{'Site Title':40s} {'URL':50s} {'Last Activity':25s} {'Storage':10s} {'Owner'}")
    print("-" * 140)
    for s in sorted(inactive, key=lambda x: x["last_activity"]):
        storage = f"{s['storage_used_mb']} MB"
        print(
            f"{s['title'][:38]:40s} "
            f"{s['url'][:48]:50s} "
            f"{s['last_activity'].strftime('%Y-%m-%d %H:%M'):25s} "
            f"{storage:10s} "
            f"{s['owner']}"
        )


if __name__ == "__main__":
    main()
