"""Set the external sharing capability for a site.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/sharing-rest-api
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.tenant.administration.sharing_capabilities import SharingCapabilities
from office365.sharepoint.tenant.administration.tenant import Tenant
from tests.settings import admin_site_url, cert_path, cert_thumbprint, client_id, site_url, tenant

CAPABILITIES = {
    "disabled": SharingCapabilities.Disabled,
    "external-users": SharingCapabilities.ExternalUserSharingOnly,
    "anyone": SharingCapabilities.ExternalUserAndGuestSharing,
    "existing-guests": SharingCapabilities.ExistingExternalUserSharingOnly,
}

SHARING_LABELS = {
    SharingCapabilities.Disabled: "Disabled",
    SharingCapabilities.ExternalUserSharingOnly: "Authenticated external only",
    SharingCapabilities.ExternalUserAndGuestSharing: "Anyone (links + guests)",
    SharingCapabilities.ExistingExternalUserSharingOnly: "Existing guests only",
}


def sharing_label(capability) -> str:
    if capability is None:
        return "Unknown"
    return SHARING_LABELS.get(capability, str(capability))


def main():
    parser = argparse.ArgumentParser(description="Set the external sharing capability for a site")
    parser.add_argument("--site-url", default=site_url, help="site collection URL")
    parser.add_argument(
        "--capability",
        choices=sorted(CAPABILITIES),
        default="external-users",
        help="sharing capability to apply",
    )
    args = parser.parse_args()

    ctx = ClientContext(admin_site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    tenant_admin = Tenant(ctx)
    props = tenant_admin.get_site_properties_by_url(args.site_url).execute_query()
    print(f"Current: {sharing_label(props.sharing_capability)}")

    props.sharing_capability = CAPABILITIES[args.capability]
    props.update_ex().execute_query()
    print(f"Updated: {sharing_label(props.sharing_capability)}")


if __name__ == "__main__":
    main()
