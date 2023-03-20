from examples import sample_site_url, sample_username, sample_password
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext

ctx = ClientContext(sample_site_url).with_credentials(UserCredential(sample_username, sample_password))
my_site = ctx.web.current_user.get_personal_site().execute_query()
print(my_site.url)
