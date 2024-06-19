"""
Creates and returns an anonymous link that can be used to access a document without needing to authenticate
"""

import datetime
from datetime import timedelta

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

client = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
file_url = "Shared Documents/Financial Sample.xlsx"
file = client.web.get_file_by_server_relative_path(file_url)
expires = datetime.datetime.now() + timedelta(minutes=120)
result = file.create_anonymous_link_with_expiration(expires).execute_query()
print(result.value)
