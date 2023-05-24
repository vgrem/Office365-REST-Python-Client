"""
Controlling app access on a specific SharePoint site collection

Refer for doc:
https://developer.microsoft.com/en-us/office/blogs/controlling-app-access-on-specific-sharepoint-site-collections/

"""

from examples import acquire_token_by_client_credentials
from office365.graph_client import GraphClient
from tests import test_client_credentials, test_team_site_url


def assign_site_access(site, roles=None, clear_existing=False):
    """
    :param office365.onedrive.sites.site.Site site: Site the permissions to grant
    :param list[str] roles: The list of roles to add
    :param bool clear_existing: Clear existing permissions first
    """
    app = client.applications.get_by_client_id(test_client_credentials.clientId).get().execute_query()

    if clear_existing:
        target_site.permissions.delete_all().execute_query()

    if roles:
        identities = [{
            "application": {
                "id": app.properties["appId"],
                "displayName": app.properties["displayName"]
            }
        }]
        site.permissions.add(roles=roles, grantedToIdentities=identities).execute_query()


client = GraphClient(acquire_token_by_client_credentials)
target_site = client.sites.get_by_url(test_team_site_url)
# assign_site_access(user_site_url, [], True)
assign_site_access(target_site, ["read", "write"])
