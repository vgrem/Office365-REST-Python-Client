import os
from office365.sharepoint.client_context import ClientContext
from tests import test_tenant, test_team_site_url, test_site_url


def create_client_default():
    cert_credentials = {
        'tenant': test_tenant,
        'client_id': '51d03106-4726-442c-86db-70b32fa7547f',
        'thumbprint': "78CA7402E8A2508A9772CB1B2E085945147D8050",
        'cert_path': '{0}/selfsigncert.pem'.format(os.path.dirname(__file__)),
    }
    return ClientContext(test_team_site_url).with_client_certificate(**cert_credentials)


def create_client_with_scopes():
    cert_credentials = {
        'tenant': test_tenant,
        'client_id': '51d03106-4726-442c-86db-70b32fa7547f',
        'thumbprint': "78CA7402E8A2508A9772CB1B2E085945147D8050",
        'cert_path': '{0}/selfsigncert.pem'.format(os.path.dirname(__file__)),
        'scopes': ['{0}/.default'.format(test_site_url)]
    }

    return ClientContext(test_team_site_url).with_client_certificate(**cert_credentials)


def create_client_with_private_key():
    cert_path = '{0}/selfsigncert.pem'.format(os.path.dirname(__file__))
    with open(cert_path, 'r') as f:
        private_key = open(cert_path).read()

    cert_credentials = {
        'tenant': test_tenant,
        'client_id': '51d03106-4726-442c-86db-70b32fa7547f',
        'thumbprint': "78CA7402E8A2508A9772CB1B2E085945147D8050",
        'private_key': private_key
    }
    return ClientContext(test_team_site_url).with_client_certificate(**cert_credentials)


#ctx = create_client_default()
#ctx = create_client_with_scopes()
ctx = create_client_with_private_key()
current_web = ctx.web.get().execute_query()
print("{0}".format(current_web.url))
