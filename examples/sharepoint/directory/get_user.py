from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.directory.directory_session import DirectorySession
from tests import test_site_url, test_user_credentials

client = ClientContext(test_site_url).with_credentials(test_user_credentials)
session = DirectorySession(client)
whoami = session.me.get().execute_query()
print(whoami.properties['principalName'])
