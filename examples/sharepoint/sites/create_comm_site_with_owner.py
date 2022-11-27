import uuid

from office365.sharepoint.client_context import ClientContext
from tests import test_team_site_url, test_user_principal_name_alt, test_admin_credentials

client = ClientContext(test_team_site_url).with_credentials(test_admin_credentials)
owner = client.web.site_users.get_by_email(test_user_principal_name_alt)
site_alias = "commsite_{0}".format(uuid.uuid4().hex)
site = client.create_modern_site("Comm Site", site_alias, owner).execute_query()
print("Site has been created at url: {0}".format(site.url))
