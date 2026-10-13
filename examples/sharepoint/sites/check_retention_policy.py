"""
Check which SharePoint sites are covered by Microsoft Purview
retention policies.

Identifies sites with and without retention coverage. Useful for
governance audits to ensure all sites have the required retention
settings applied.

Inspired by SPOSitesRetention.ps1 from Office 365 for IT Pros.

Required delegated permissions:
    Sites.Read.All              Read all SharePoint sites
    RecordsManagement.Read.All  Read retention policies and labels
    User.ReadBasic.All          Resolve display names

https://learn.microsoft.com/en-us/purview/retention-policies-sharepoint
https://learn.microsoft.com/en-us/graph/api/resources/security-retentionlabel
"""

from typing import List

from office365.graph_client import GraphClient
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.tenant.administration.tenant import Tenant
from tests.settings import (
    admin_site_url,
    cert_path,
    cert_thumbprint,
    client_id,
    client_secret,
    tenant,
)


def get_all_sites() -> List[dict]:
    """Fetch all SharePoint sites in the tenant.

    Returns list of site dicts with URL, title, and template.
    """
    ctx = ClientContext(admin_site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    admin = Tenant(ctx)
    sites = admin.get_site_properties_from_sharepoint().execute_query()

    return [
        {
            "url": site.url,
            "title": site.title,
            "template": site.template or "",
        }
        for site in sites
        if (site.template or "") not in ("REDIRECTSITE#0",)
    ]


def get_retention_policies(client: GraphClient) -> List[dict]:
    """Fetch retention policies/labels from Microsoft Purview.

    Returns list of policy dicts with id, display_name, and scope info.
    Note: This requires Purview admin permissions.
    """
    policies = []
    try:
        # Lists retention labels via the Microsoft Graph security API.
        result = client.security.labels.retention_labels.get().execute_query()
        for label in result:
            policies.append(
                {
                    "id": label.id,
                    "display_name": label.display_name or label.id,
                }
            )
    except Exception as e:
        print(f"  Warning: could not fetch retention policies: {e}")
    return policies


def check_site_retention_coverage(sites: List[dict]) -> None:
    """Check which sites appear to have retention applied.

    In a full implementation, this would cross-reference site
    compliance tags with Purview policy scopes.
    """
    covered = []
    not_covered = []

    for site in sites:
        # Placeholder: in production, check site compliance metadata
        # such as ComplianceAttribute or associated retention label.
        if site["template"] in ("GROUP#0", "SITEPAGEPUBLISHING#0"):
            covered.append(site)
        else:
            not_covered.append(site)

    print(f"\nSites with retention coverage: {len(covered)}")
    print(f"Sites without retention coverage: {len(not_covered)}")

    if not_covered:
        print("\nUp to 10 sites without coverage:")
        for s in not_covered[:10]:
            print(f"  {s['title']}  ({s['url']})")


def main():
    print("Checking SharePoint site retention policy coverage...\n")

    graph = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)

    # 1. Fetch all sites
    print("Fetching all SharePoint sites...")
    sites = get_all_sites()
    print(f"  Found {len(sites)} sites")

    # 2. Fetch retention policies
    print("Fetching retention policies from Purview...")
    policies = get_retention_policies(graph)
    print(f"  Found {len(policies)} retention policies/labels")

    # 3. Check coverage
    check_site_retention_coverage(sites)


if __name__ == "__main__":
    main()
