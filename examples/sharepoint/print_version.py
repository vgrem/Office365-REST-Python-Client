"""
Prints metadata about the site
"""

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.webs.web import Web
from tests import test_client_credentials, test_site_url

ctx = ClientContext(test_site_url).with_credentials(test_client_credentials)
result = Web.get_context_web_information(ctx).execute_query()
print(result.value.LibraryVersion)
