"""
Add an existing field link to a content type.

SharePoint Online's REST API is restrictive here: ``POST`` to a content type's
``FieldLinks`` collection only succeeds for a column that is already reachable
from the content type's parent (typically a field the parent content type
defines). A brand-new site column cannot be attached over REST — the server
answers ``Column '<name>' does not exist``. This example therefore attempts the
documented call, **re-reads the links and reports whether it actually took
effect**, so it never silently pretends a link was created. Use CSOM, PnP
PowerShell or the content type hub to attach a genuinely new column.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/csom/contenttype
"""

import argparse

from office365.runtime.client_request_exception import ClientRequestException
from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Add a field link to a content type")
    parser.add_argument("--name", required=True, help="Content type name")
    parser.add_argument("--field", required=True, help="Field internal name or title")
    parser.add_argument(
        "--keep", action="store_true", help="Keep the content type (default: delete only if created here)"
    )
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    existing = ctx.web.content_types.find_by_name(args.name)
    existing.execute_query()
    created = not existing.is_loaded
    ct = ctx.web.ensure_content_type(name=args.name).execute_query()

    try:
        field = ctx.web.fields.get_by_internal_name_or_title(args.field).get().execute_query()
    except ClientRequestException as e:
        raise SystemExit(f"Field '{args.field}' was not found on the site: {e}") from e
    internal_name = field.internal_name

    current = {link.field_internal_name for link in ct.field_links.get().execute_query()}
    if internal_name in current:
        print(f"Field already linked: {internal_name}")
    else:
        try:
            ct.field_links.add(internal_name).execute_query()
        except ClientRequestException as e:
            print(f"Could not link '{internal_name}': {e}")

        # Re-read: SharePoint Online rejects attaching a brand-new column.
        updated = {link.field_internal_name for link in ct.field_links.get().execute_query()}
        if internal_name in updated:
            print(f"Field added to content type: {internal_name}")
        else:
            print(
                f"Note: '{internal_name}' is still not linked. SharePoint Online's REST API can only link a "
                "column that is already reachable from the content type's parent; attaching a brand-new column "
                "requires CSOM or PnP PowerShell. Nothing was changed."
            )

    print(f"Field links: {len(ct.field_links.get().execute_query())}")

    if created and not args.keep:
        ct.delete_object().execute_query()
        print("  (content type removed after demo)")


if __name__ == "__main__":
    main()
