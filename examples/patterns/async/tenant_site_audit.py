"""
Audit every site collection concurrently (async).

Fetches the tenant's site collections once, then fans out one
``getSitePropertiesByUrl`` call per site with a bounded number of requests in
flight. This removes the N+1 sequential loop of the synchronous counterpart
(``examples/sharepoint/sites/find_inactive_sites.py``): each site is inspected
without waiting for the previous one to finish.

A ``ClientContext`` drains its own pending-query queue on every call, so each
task works on its own clone. The clone shares the parent's credentials and HTTP
connection pool, so the whole run uses a single token and one session.

Requires a tenant administrator (the app needs ``Sites.Read.All`` on the admin
site).

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/navigation/site-operations
"""

from __future__ import annotations

import argparse
import asyncio
import time
from datetime import datetime, timedelta, timezone

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.tenant.administration.sites.properties import SiteProperties
from office365.sharepoint.tenant.administration.tenant import Tenant
from tests.settings import admin_site_url, cert_path, cert_thumbprint, client_id, tenant


async def find_inactive_sites(
    days_threshold: int = 90,
    concurrency: int = 8,
    include_channel_sites: bool = False,
) -> list[dict]:
    """Return sites whose content has not changed within *days_threshold* days.

    Args:
        days_threshold: Number of days of inactivity to flag a site.
        concurrency: Maximum number of sites inspected at the same time.
        include_channel_sites: Include Teams private/shared channel sites.
    """
    ctx = ClientContext(admin_site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    sites = await Tenant(ctx).get_site_properties_from_sharepoint().execute_query_async()
    cutoff = datetime.now(timezone.utc) - timedelta(days=days_threshold)
    sem = asyncio.Semaphore(concurrency)

    async def inspect(site: SiteProperties) -> dict | None:
        template = getattr(site, "template", "") or ""
        if site.url is None or template == "REDIRECTSITE#0":
            return None
        if getattr(site, "archive_status", None) != "NotArchived":
            return None
        if not include_channel_sites and template.startswith("TEAMCHANNEL"):
            return None

        # one request per clone; the semaphore bounds in-flight requests
        async with sem:
            clone = ctx.clone(admin_site_url)
            props = await Tenant(clone).get_site_properties_by_url(site.url).execute_query_async()

        last_activity = getattr(props, "last_content_modified_date", None)
        if last_activity is None or last_activity >= cutoff:
            return None
        return {
            "url": site.url,
            "title": site.title,
            "template": template,
            "last_activity": last_activity,
            "storage_used_mb": getattr(site, "storage_usage_current", 0),
            "storage_quota_mb": getattr(site, "storage_quota", 0),
        }

    # return_exceptions isolates a failing site instead of cancelling the batch
    results = await asyncio.gather(*(inspect(s) for s in sites), return_exceptions=True)

    rows: list[dict] = []
    for site, result in zip(sites, results):
        if isinstance(result, Exception):
            print(f"  skipped {site.url}: {result}")
        elif result is not None:
            rows.append(result)
    return rows


async def main() -> None:
    parser = argparse.ArgumentParser(description="Find inactive SharePoint sites concurrently")
    parser.add_argument("--days-threshold", type=int, default=90, help="days of inactivity (default: 90)")
    parser.add_argument("--concurrency", type=int, default=8, help="sites inspected at a time (default: 8)")
    parser.add_argument("--include-channel-sites", action="store_true", help="include Teams channel sites")
    args = parser.parse_args()

    print("Fetching SharePoint Online sites...")
    started = time.perf_counter()
    inactive = await find_inactive_sites(
        days_threshold=args.days_threshold,
        concurrency=args.concurrency,
        include_channel_sites=args.include_channel_sites,
    )
    elapsed = time.perf_counter() - started

    if not inactive:
        print(f"No inactive sites found ({elapsed:.1f}s).")
        return

    print(f"\nFound {len(inactive)} sites inactive for {args.days_threshold}+ days ({elapsed:.1f}s):\n")
    print(f"{'Site Title':40s} {'URL':50s} {'Last Activity':25s} {'Storage':10s}")
    print("-" * 130)
    for s in sorted(inactive, key=lambda x: x["last_activity"]):
        print(
            f"{(s['title'] or '')[:38]:40s} "
            f"{s['url'][:48]:50s} "
            f"{s['last_activity'].strftime('%Y-%m-%d %H:%M'):25s} "
            f"{str(s['storage_used_mb']) + ' MB':10s}"
        )


asyncio.run(main())
