"""
Retrieve only selected properties (Author) of a website

The client library queries only for those properties on the server via select and expand methods,
and the server sends only those properties to the client.
This technique reduces unnecessary data transfer between the client and the server.
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_site_url

client = ClientContext(test_site_url).with_credentials(test_client_credentials)
web = client.web.get().expand(["Author"]).execute_query()
print(web.author)
