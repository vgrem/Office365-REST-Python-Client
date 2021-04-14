from office365.sharepoint.sites.site import Site
from office365.sharepoint.tenant.administration.secondary_administrators_info import SecondaryAdministratorsInfo
from office365.sharepoint.tenant.administration.tenant import Tenant
from tests import test_user_credentials, test_site_url, test_admin_site_url, test_user_principal_name_alt

tenant = Tenant.from_url(test_admin_site_url).with_credentials(test_user_credentials)

target_site = Site.from_url(test_site_url).with_credentials(test_user_credentials).get().execute_query()
admins = tenant.get_site_secondary_administrators(site_id=target_site.id)
tenant.execute_query()

existing_admin_names = [admin.loginName for admin in admins]

target_user = target_site.root_web.ensure_user(test_user_principal_name_alt).execute_query()
names = existing_admin_names + [target_user.login_name]
tenant.set_site_secondary_administrators(site_id=target_site.id, names=names).execute_query()

for admin in admins:  # type: SecondaryAdministratorsInfo
    print(admin.loginName)
