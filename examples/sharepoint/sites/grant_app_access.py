"""
Controlling app access on a specific SharePoint site collection

Refer:
https://developer.microsoft.com/en-us/office/blogs/controlling-app-access-on-specific-sharepoint-site-collections/

"""
import json

from office365.graph_client import GraphClient
from tests import test_client_credentials, test_team_site_url
from tests.graph_case import acquire_token_by_client_credentials


def assign_site_access(site, application, roles=None, clear_existing=False):
    """
    :param office365.onedrive.sites.site.Site site: Site the permissions to grant
    :param office365.onedrive.directory.applications.Application application: Application
    :param list[str] roles: The list of roles to add
    :param bool clear_existing: Clear existing permissions first
    """
    if clear_existing:
        print("Clearing existing permissions...")
        target_site.permissions.delete_all().execute_query()

    if roles:
        print("Granting {0} permissions for application {1}".format(roles, application.app_id))
        site.permissions.add(roles, application).execute_query()

    result = site.permissions.get().execute_query()
    print("Current permissions: {0}".format(json.dumps(result.to_json(), indent=4)))


client = GraphClient(acquire_token_by_client_credentials)
target_site = client.sites.get_by_url(test_team_site_url)
app = client.applications.get_by_app_id(test_client_credentials.clientId)
# assign_site_access(user_site_url, [], True)
assign_site_access(target_site, app, ["read", "write"], True)
