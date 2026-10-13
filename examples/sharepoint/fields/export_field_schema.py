"""
Export list field definitions (name, type, flags, group) to CSV or JSON.

Useful for documenting or migrating a list schema.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api
"""

import argparse
import csv
import json
import os
import tempfile

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Export field definitions")
    parser.add_argument("--list-title", default="Documents", help="List to export")
    parser.add_argument("--format", choices=["csv", "json"], default="csv")
    parser.add_argument("--output", default=None, help="Output file path (default: temp dir)")
    args = parser.parse_args()
    if args.output is None:
        args.output = os.path.join(tempfile.gettempdir(), f"field_schema.{args.format}")

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    fields = ctx.web.lists.get_by_title(args.list_title).fields.get().execute_query()

    rows = [
        {
            "InternalName": f.internal_name,
            "Title": f.title,
            "Type": f.type_display_name,
            "Required": f.properties.get("Required", False),
            "Hidden": f.hidden,
            "Group": f.group,
        }
        for f in fields
    ]

    if args.format == "csv":
        fieldnames = ["InternalName", "Title", "Type", "Required", "Hidden", "Group"]
        with open(args.output, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    else:
        with open(args.output, "w", encoding="utf-8") as fh:
            json.dump(rows, fh, indent=2, default=str)

    print(f"Exported {len(rows)} fields to {args.output}")


if __name__ == "__main__":
    main()
