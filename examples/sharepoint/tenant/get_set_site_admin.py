from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.tenant.administration.secondary_administrators_info import SecondaryAdministratorsInfo
from office365.sharepoint.tenant.administration.tenant import Tenant
from settings import settings

credentials = UserCredential(settings['user_credentials']['username'],
                             settings['user_credentials']['password'])


client = ClientContext(settings.get("team_site_url")).with_credentials(credentials)
target_site = client.site.get().execute_query()

admin_client = ClientContext(settings.get("admin_site_url")).with_credentials(credentials)
tenant = Tenant(admin_client)

admins = tenant.get_site_secondary_administrators(site_id=target_site.id)
admin_client.execute_query()

emails = settings.get("test_accounts")
tenant.set_site_secondary_administrators(site_id=target_site.id, emails=emails).execute_query()

for admin in admins:  # type: SecondaryAdministratorsInfo
    print(admin.get_property('loginName'))
