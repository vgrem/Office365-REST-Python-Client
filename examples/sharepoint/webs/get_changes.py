"""
Returns the collection of all changes from the change log that have occurred within the scope of the site
"""
from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

client = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
changes = client.web.get_changes().execute_query()
for change in changes:
    print(change)
