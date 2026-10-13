"""
Add an alert on a list for the current user.

.. note::
   Microsoft 365's ``SP.AlertCreationInformation`` type does **not** expose the list
   association (there is no ``List`` property in the server CSDL), so creating a
   list alert over the REST API fails server-side with a schema error. This example
   demonstrates the documented call and degrades gracefully when the server rejects
   it. Use the SharePoint UI or CSOM/PnP PowerShell to create alerts instead.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api
"""

import argparse

from office365.runtime.client_request_exception import ClientRequestException
from office365.sharepoint.client_context import ClientContext
from tests.settings import client_id, password, site_url, tenant, username


def main():
    parser = argparse.ArgumentParser(description="Add an alert on a list for the current user")
    parser.add_argument("--list-title", default="Documents", help="title of the target list")
    parser.add_argument("--title", default="My Alert", help="alert title")
    args = parser.parse_args()

    ctx = ClientContext(site_url).with_username_and_password(
        tenant=tenant, client_id=client_id, username=username, password=password
    )
    target_list = ctx.web.lists.get_by_title(args.list_title)
    try:
        target_list.add_alert(args.title).execute_query()
        print(f"Alert created on list '{args.list_title}'")
    except ClientRequestException as e:
        print(f"Could not create the alert over REST: {e}")
        print(
            "Hint: the SharePoint REST API does not expose the list association on "
            "SP.AlertCreationInformation; create alerts with CSOM/PnP PowerShell instead."
        )


if __name__ == "__main__":
    main()
