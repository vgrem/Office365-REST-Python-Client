"""
Assign a sensitivity label to a SharePoint site (site-level compliance).

Applies a Microsoft Purview sensitivity label to a site, which
inherits to all documents and lists within it. Useful for applying
governance baselines (e.g. "Confidential" or "Internal") across a
set of sites.

Inspired by UpdateSPOSitesWithLabels.PS1 from Office 365 for IT Pros.

Required delegated permissions:
    Sites.ReadWrite.All         Read/write site properties
    User.ReadBasic.All          Resolve user info
    — Sensitivity label management requires Purview compliance roles

https://learn.microsoft.com/en-us/graph/api/resources/sensitivitylabel
https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api
"""

from __future__ import annotations

from office365.graph_client import GraphClient
from office365.sharepoint.client_context import ClientContext
from tests.settings import (
    cert_path,
    cert_thumbprint,
    client_id,
    client_secret,
    site_url,
    tenant,
)


def list_available_labels(client: GraphClient) -> list[dict]:
    """Fetch sensitivity labels applicable to sites/groups.

    Returns list of label dicts with id, display_name, and priority.
    """
    labels = []
    try:
        result = client.security.data_security_and_governance.sensitivity_labels.get().execute_query()
        for label in result:
            labels.append(
                {
                    "id": label.id,
                    "display_name": label.display_name or label.id,
                    "priority": label.priority or 0,
                }
            )
    except Exception as e:
        print(f"  Warning: could not fetch labels: {e}")

    return labels


def get_current_site_label(ctx: ClientContext) -> str | None:
    """Get the current sensitivity label on a SharePoint site.

    Returns the label ID as a string, or None if no label is set.
    """
    site = ctx.site.select(["SensitivityLabelId"]).get().execute_query()
    return site.sensitivity_label_id


def assign_sensitivity_label(site_url: str, label_id: str) -> bool:
    """Assign a sensitivity label to a SharePoint site.

    Args:
        site_url: Full URL of the target site.
        label_id: Immutable ID of the sensitivity label to assign.

    Returns:
        True if successful, False otherwise.
    """
    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )

    try:
        # Set the sensitivity label on the site
        site = ctx.site
        site.set_property("SensitivityLabelId", label_id)
        site.update().execute_query()
        print(f"  Label {label_id} applied to {site_url}")
        return True
    except Exception as e:
        print(f"  Error applying label: {e}")
        return False


def main():
    print("SharePoint site sensitivity label management\n")

    graph = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)

    # 1. List available labels
    print("Fetching available sensitivity labels...")
    labels = list_available_labels(graph)

    if not labels:
        print("No sensitivity labels found. Create labels in Purview first.")
        return

    print("Available labels:")
    for lbl in sorted(labels, key=lambda x: x["priority"]):
        print(f"  [{lbl['id'][:8]}...] {lbl['display_name']} (priority {lbl['priority']})")

    # 2. Check current label on the site
    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    current = get_current_site_label(ctx)
    print(f"\nCurrent label on {site_url}: {current or 'None'}")

    # 3. Apply a label (uncomment with your label ID)
    # label_to_apply = labels[0]["id"]
    # assign_sensitivity_label(site_url, label_to_apply)

    print("\nTo apply a label, uncomment the call with your label ID.")
    print("Example:")
    print('  assign_sensitivity_label("https://contoso.sharepoint.com/sites/team", label_id)')


if __name__ == "__main__":
    main()
