"""
Remove an alert by ID.

The current user's alerts are listed first so you can pick an ID, or pass
``--alert-id`` explicitly.

https://learn.microsoft.com/en-us/sharepoint/dev/apis/rest-api
"""

import argparse

from office365.sharepoint.client_context import ClientContext
from tests.settings import cert_path, cert_thumbprint, client_id, site_url, tenant


def main():
    parser = argparse.ArgumentParser(description="Remove an alert by ID")
    parser.add_argument("--site-url", default=site_url, help="target site URL")
    parser.add_argument("--alert-id", default="", help="ID of the alert to remove")
    parser.add_argument("--apply", action="store_true", help="actually delete (default: dry run)")
    args = parser.parse_args()

    ctx = ClientContext(args.site_url).with_client_certificate(
        tenant, client_id=client_id, thumbprint=cert_thumbprint, cert_path=cert_path
    )

    alerts = ctx.web.current_user.alerts.get().execute_query()
    if not alerts:
        print("No alerts found for the current user.")
        return

    alert_id = args.alert_id or alerts[0].id
    if not alert_id:
        print("The alert has no ID property; pass --alert-id explicitly.")
        return

    if not args.apply:
        print(f"Would remove alert {alert_id} (pass --apply to delete).")
        return

    ctx.web.current_user.alerts.get_by_id(str(alert_id)).delete_object().execute_query()
    print(f"Alert removed: {alert_id}")


if __name__ == "__main__":
    main()
