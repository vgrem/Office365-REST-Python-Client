"""
Organization settings — read tenant-wide configuration.

Covers the most practical tenant settings:
  - Organization profile (name, addresses, technical contacts)
  - Verified domains
  - Organization branding (sign-in page)

Requires application permission ``Organization.Read.All`` (``Directory.Read.All``
also covers it).

Reference:
    https://learn.microsoft.com/en-us/graph/api/resources/organization
"""

from __future__ import annotations

import argparse

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.settings import client_id, client_secret, tenant


def _client() -> GraphClient:
    return GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()

    client = _client().require_application_permission("Directory.Read.All")
    org = client.organization.get().execute_query()[0]

    print("Organization:")
    print(f"  {org.display_name}  id={org.id}  type={org.tenant_type or '?'}")
    print(f"  {org.street or '?'}, {org.postal_code or '?'} {org.city or '?'}, {org.state or '?'} {org.country or '?'}")
    print(f"  technical contacts: {', '.join(org.technical_notification_mails) or '(none)'}")

    print(f"\nVerified domains ({len(org.verified_domains)}):")
    for domain in org.verified_domains:
        flags = " ".join(name for name, on in (("default", domain.isDefault), ("initial", domain.isInitial)) if on)
        print(f"  {domain.name:35s}  {flags}")

    try:
        branding = org.branding.get().execute_query()
    except ClientRequestException as e:
        print(f"\nBranding not available: {e}")
    else:
        print("\nBranding:")
        print(
            f"  background={branding.background_color or '?'}  "
            f"banner logo={branding.banner_logo_relative_url or '(none)'}"
        )
        print(f"  sign-in text: {(branding.sign_in_page_text or '')[:60]}  hint: {branding.username_hint_text or '?'}")


if __name__ == "__main__":
    main()
