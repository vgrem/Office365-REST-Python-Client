import json
from random import randint

from office365.sharepoint.tenant.administration.tenant import Tenant
from tests import test_admin_site_url, test_site_url, test_user_credentials, test_user_principal_name_alt

alias = str(randint(0, 10000))
title = "Custom Site"
site_url = "{0}/sites/{1}".format(test_site_url, alias)

tenant = Tenant.from_url(test_admin_site_url).with_credentials(test_user_credentials)

site = tenant.create_site_sync(site_url, test_user_principal_name_alt).execute_query()
print(json.dumps(site.to_json(), indent=4))
tenant.remove_site(site_url).execute_query()  # cleanup
