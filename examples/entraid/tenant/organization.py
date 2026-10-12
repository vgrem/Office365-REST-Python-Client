"""
Organization settings — read and update tenant-wide configuration.

Covers the most practical tenant settings:
  - Read organization profile (name, technical contacts, privacy)
  - List organization branding (sign-in page, logo, background)
  - Read partner tenant relationships (permissions, delegations)

Requires delegated permission ``Organization.Read.All``
(``Organization.ReadWrite.All`` for updates).

https://learn.microsoft.com/en-us/graph/api/resources/organization
"""

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant


def main():
    client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)

    # -- Step 1: read organization profile --
    orgs = client.organization.get().execute_query()
    if not orgs:
        print("(no organization data)")
        return

    org = orgs[0]
    print("Organization details:\n")
    print(f"  Display name:              {org.display_name or '?'}")
    print(f"  Tenant ID:                 {org.id or '?'}")
    print(f"  City:                      {org.city or '?'}")
    print(f"  Country/region:            {org.country or '?'}")
    print(f"  Postal code:               {org.postal_code or '?'}")
    print(f"  State:                     {org.state or '?'}")
    print(f"  Street:                    {org.street or '?'}")
    print(f"  Tenant type:               {org.tenant_type or '?'}")

    if org.verified_domains:
        print(f"\n  Verified domains ({len(org.verified_domains)}):")
        for d in org.verified_domains:
            is_default = d.properties.get("isDefault", False)
            is_initial = d.properties.get("isInitial", False)
            print(
                f"    {d.properties.get('name', '?'):35s}  "
                f"{'default ' if is_default else ''}"
                f"{'initial' if is_initial else ''}"
            )

    # -- Step 2: notification contacts --
    print(f"\n  Technical notification mails:       {org.technical_notification_mails or '(none)'}")
    print(f"  Security/compliance notification:   {org.security_compliance_notification_mails or '(none)'}")
    print(f"  Marketing notification:             {org.marketing_notification_emails or '(none)'}")
    print(f"  Privacy contact:                    {org.privacy_notification_emails or '(none)'}")
    print(f"  Privacy profile URL:                {org.privacy_profile_url or '(none)'}")

    # -- Step 3: list organization branding --
    try:
        branding = org.branding.get().execute_query()
        print("\n  Branding:")
        print(f"    Locale:                       {branding.locale or '?'}")
        print(f"    Background color:             {branding.background_color or '?'}")
        print(f"    Sign-in page text:            {(branding.sign_in_page_text or '')[:60]}")
        print(f"    Username hint:                {branding.username_hint or '?'}")
        print(f"    Hide keep me signed in:       {branding.hide_keep_me_signed_in}")
        print(f"    Custom logo:                  {'Yes' if branding.logo_id else 'No'}")
    except Exception as e:
        print(f"\n  Branding: {e}")

    # -- Step 4: partner tenant relationships --
    try:
        partners = org.partner_tenant_relationships.get().execute_query()
        print(f"\n  Partner tenant relationships: {len(partners)}")
        for pt in partners:
            print(f"    {pt.properties.get('partnerTenantId', '?'):40s}  status={pt.properties.get('status', '?')}")
    except Exception:
        print("\n  (partner relationships not available)")


if __name__ == "__main__":
    main()
