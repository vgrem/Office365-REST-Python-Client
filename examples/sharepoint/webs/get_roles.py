"""
Lists web roles
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_site_url

client = ClientContext(test_site_url).with_credentials(test_client_credentials)
role_defs = client.web.role_definitions.get().execute_query()
for role_def in role_defs:
    print(role_def)
