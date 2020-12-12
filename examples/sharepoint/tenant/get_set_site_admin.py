from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.tenant.administration.secondary_administrators_info import SecondaryAdministratorsInfo
from office365.sharepoint.tenant.administration.tenant import Tenant
from settings import settings, tenant_prefix

credentials = UserCredential(settings['user_credentials']['username'],
                             settings['user_credentials']['password'])


client = ClientContext(settings.get('url')).with_credentials(credentials)
target_site = client.site.get().execute_query()

admin_client = ClientContext(settings.get("admin_site_url")).with_credentials(credentials)
tenant = Tenant(admin_client)

admins = tenant.get_site_secondary_administrators(site_id=target_site.id)
admin_client.execute_query()

existing_admin_names = [admin.loginName for admin in admins]

target_user = target_site.root_web.ensure_user(f"mdoe@{tenant_prefix}.onmicrosoft.com").execute_query()
names = existing_admin_names + [target_user.login_name]
tenant.set_site_secondary_administrators(site_id=target_site.id, names=names).execute_query()

for admin in admins:  # type: SecondaryAdministratorsInfo
    print(admin.loginName)
