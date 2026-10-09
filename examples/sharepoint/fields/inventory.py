"""
Field inventory: site columns (web scope) and list columns.

Surfaces the type, required, and hidden state admins need when planning
schema changes or migrations.

Requires read access to the site.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


def _flags(field) -> str:
    flags = []
    if field.properties.get("Required", False):
        flags.append("required")
    if field.hidden:
        flags.append("hidden")
    return ", ".join(flags)


def print_fields(fields, scope: str) -> None:
    print(f"{scope} ({len(fields)}):")
    for field in fields:
        print(f"  {field.internal_name or '?':35s} {field.type_display_name or '?':18s} {_flags(field)}")


def main():
    parser = argparse.ArgumentParser(description="List site columns and list columns")
    parser.add_argument("--list-title", default="Documents", help="list whose columns to list")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    print_fields(ctx.web.fields.get().execute_query(), "Site columns (web scope)")
    print_fields(
        ctx.web.lists.get_by_title(args.list_title).fields.get().execute_query(),
        f"List columns ({args.list_title})",
    )


if __name__ == "__main__":
    main()
