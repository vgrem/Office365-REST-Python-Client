"""Export curated user profile properties for all site users to a CSV file.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/people-rest-api
"""

import argparse
import csv
import tempfile
from pathlib import Path

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant

# Well-known user profile property names exported from UserProfileProperties
PROFILE_KEYS = ["PreferredName", "Department", "JobTitle", "Office", "Manager", "WorkEmail", "PictureURL"]


def main():
    parser = argparse.ArgumentParser(description="Export user profile properties to CSV")
    parser.add_argument(
        "--output",
        default=str(Path(tempfile.gettempdir()) / "profile_export.csv"),
        help="output CSV path (default: profile_export.csv)",
    )
    parser.add_argument("--limit", type=int, default=0, help="max users to export, 0 = all (default: 0)")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )

    users = ctx.site.root_web.site_users.get_all().execute_query()
    if args.limit > 0:
        users = list(users)[: args.limit]

    profiles = []
    for user in users:
        if user.login_name:
            profiles.append(ctx.people_manager.get_properties_for(user.login_name))
    ctx.execute_batch()

    columns = ["AccountName", "DisplayName", "Email"] + PROFILE_KEYS
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for p in profiles:
            props = p.user_profile_properties or {}
            row = {
                "AccountName": p.account_name or props.get("AccountName", ""),
                "DisplayName": p.display_name or props.get("PreferredName", ""),
                "Email": p.email or props.get("WorkEmail", ""),
            }
            row.update({key: str(props.get(key, "") or "") for key in PROFILE_KEYS})
            writer.writerow(row)

    print(f"Exported {len(profiles)} profiles to {args.output}")


if __name__ == "__main__":
    main()
