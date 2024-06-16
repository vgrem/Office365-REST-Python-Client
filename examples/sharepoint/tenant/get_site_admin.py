"""
Gets site collection administrators
"""

from office365.sharepoint.sites.site import Site
from office365.sharepoint.tenant.administration.tenant import Tenant
from tests import test_admin_site_url, test_site_url, test_user_credentials

tenant = Tenant.from_url(test_admin_site_url).with_credentials(test_user_credentials)

target_site = (
    Site.from_url(test_site_url)
    .with_credentials(test_user_credentials)
    .get()
    .execute_query()
)
result = tenant.get_site_secondary_administrators(
    site_id=target_site.id
).execute_query()
for admin in result.value:
    print(admin.loginName)
