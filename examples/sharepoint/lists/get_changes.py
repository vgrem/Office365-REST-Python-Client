"""Retrieve changes from a SharePoint list (``GetChanges``).

Official documentation: https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api/navigation/list-operations
"""

import argparse

from office365.sharepoint.changes.query import ChangeQuery
from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, team_site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Retrieve changes from a list")
    parser.add_argument("--list-title", default="Documents", help="list title")
    args = parser.parse_args()

    ctx = ClientContext(team_site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )
    query = ChangeQuery(
        Item=True,
        Add=False,
        Update=False,
        SystemUpdate=False,
        DeleteObject=True,
        RoleAssignmentAdd=False,
        RoleAssignmentDelete=False,
    )
    changes = ctx.web.lists.get_by_title(args.list_title).get_changes(query).execute_query()
    print(f"{len(changes)} change(s):")
    for change in changes:
        print(f"  {change}")


if __name__ == "__main__":
    main()
