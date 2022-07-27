import os
from office365.sharepoint.client_context import ClientContext
from tests import test_tenant, test_team_site_url

cert_settings = {
    'client_id': '51d03106-4726-442c-86db-70b32fa7547f',
    'thumbprint': "78CA7402E8A2508A9772CB1B2E085945147D8050",
    'cert_path': '{0}/selfsigncert.pem'.format(os.path.dirname(__file__)),
    #'scopes': ['{0}.default'.format(test_site_url)]
}

ctx = ClientContext(test_team_site_url).with_client_certificate(test_tenant, **cert_settings)
current_web = ctx.web.get().execute_query()
print("{0}".format(current_web.url))
