"""
Enumerate across all lists in a site
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_site_url

client = ClientContext(test_site_url).with_credentials(test_client_credentials)
# lists = client.web.get_lists().execute_query()
lists = client.web.lists.get_all().execute_query()
for lst in lists:
    print(lst.title)
