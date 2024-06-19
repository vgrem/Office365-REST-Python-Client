"""
Gets the people who are following the specified user.
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_site_url, test_user_principal_name

client = ClientContext(test_site_url).with_credentials(test_client_credentials)
user = client.site.root_web.site_users.get_by_email(test_user_principal_name)

result = client.people_manager.get_followers_for(user).execute_query()
for follower in result:
    print(follower)
