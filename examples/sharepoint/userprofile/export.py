"""
Exports user profile data.
"""
from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_site_url

client = ClientContext(test_site_url).with_credentials(test_client_credentials)
users = (
    client.site.root_web.site_users.filter("IsHiddenInUI eq false")
    .get()
    .top(10)
    .execute_query()
)

exported_data = {}
for user in users:
    exported_data[user.login_name] = client.people_manager.get_properties_for(
        user.login_name
    )
client.execute_batch()
print(exported_data)
