import uuid

from office365.sharepoint.client_context import ClientContext
from tests import test_site_url, test_client_credentials

client = ClientContext(test_site_url).with_credentials(test_client_credentials)
owner = client.web.site_users.get_by_id(12)
site_url = "{0}/sites/{1}".format(test_site_url, uuid.uuid4().hex)
result = client.site_manager.create("Comm Site", site_url, owner).execute_query()
print(result.value.SiteUrl)
