"""
Creates a modern site

https://learn.microsoft.com/en-us/sharepoint/dev/apis/site-creation-rest#create-a-modern-site
"""
from office365.sharepoint.client_context import ClientContext
from tests import (
    create_unique_name,
    test_admin_credentials,
    test_team_site_url,
    test_user_principal_name_alt,
)

client = ClientContext(test_team_site_url).with_credentials(test_admin_credentials)
owner = client.web.site_users.get_by_email(test_user_principal_name_alt)
site_alias = create_unique_name("commsite")
print("Creating a modern site: {0} ...".format(site_alias))
site = client.create_modern_site("Comm Site", site_alias, owner).execute_query()
print("Site has been created at url: {0}".format(site.url))

print("Cleaning up resources...")
site.delete_object().execute_query()
