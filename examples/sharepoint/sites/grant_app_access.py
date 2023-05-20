"""
Controlling app access on a specific SharePoint site collection

Refer for doc:
https://developer.microsoft.com/en-us/office/blogs/controlling-app-access-on-specific-sharepoint-site-collections/

"""
import sys

from examples import acquire_token_by_client_credentials
from office365.graph_client import GraphClient
from office365.onedrive.permissions.permission import Permission
from tests import test_client_credentials, test_team_site_url


def assign_site_access(site, roles=None, clear_existing=False):
    """
    :param office365.onedrive.sites.site.Site site: Site the permissions to grant
    :param list[str] roles: The list of roles to add
    :param bool clear_existing: Clear existing permissions first
    """
    apps = client.applications.filter(f"appId eq '{test_client_credentials.clientId}'").get().execute_query()
    if len(apps) == 0:
        sys.exit("App not found")

    if clear_existing:
        pcol = target_site.permissions.get().execute_query()
        for p in pcol:  # type: Permission
            p.delete_object()
        client.execute_query()

    if roles:
        identities = [{
            "application": {
                "id": apps[0].properties["appId"],
                "displayName": apps[0].properties["displayName"]
            }
        }]
        site.permissions.add(roles=roles, grantedToIdentities=identities).execute_query()


client = GraphClient(acquire_token_by_client_credentials)
target_site = client.sites.get_by_url(test_team_site_url)
# assign_site_access(user_site_url, [], True)
assign_site_access(target_site, ["read", "write"])
