"""
Controlling app access on a specific SharePoint site collection

Refer for doc:
https://developer.microsoft.com/en-us/office/blogs/controlling-app-access-on-specific-sharepoint-site-collections/

"""

from examples import acquire_token_by_client_credentials
from office365.graph_client import GraphClient
from tests import test_client_credentials, test_team_site_url


def assign_site_access(site, application, roles=None, clear_existing=False):
    """
    :param office365.onedrive.sites.site.Site site: Site the permissions to grant
    :param office365.onedrive.directory.applications.Application application: Application
    :param list[str] roles: The list of roles to add
    :param bool clear_existing: Clear existing permissions first
    """
    if clear_existing:
        target_site.permissions.delete_all().execute_query()

    if roles:
        site.permissions.add(roles, application).execute_query()


client = GraphClient(acquire_token_by_client_credentials)
target_site = client.sites.get_by_url(test_team_site_url)
app = client.applications.get_by_app_id(test_client_credentials.clientId)
# assign_site_access(user_site_url, [], True)
assign_site_access(target_site, app, ["read", "write"], True)
