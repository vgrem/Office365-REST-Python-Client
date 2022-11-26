from office365.sharepoint.tenant.administration.tenant import Tenant
from tests import test_admin_site_url, test_user_credentials

tenant = Tenant.from_url(test_admin_site_url).with_credentials(test_user_credentials)
result = tenant.get_collaboration_insights_data().execute_query()
print(result.value)
