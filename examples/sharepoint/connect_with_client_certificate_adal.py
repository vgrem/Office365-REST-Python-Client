import os
import adal

from office365.runtime.auth.token_response import TokenResponse
from office365.sharepoint.client_context import ClientContext
from settings import settings

cert_settings = {
    'client_id': '51d03106-4726-442c-86db-70b32fa7547f',
    'thumbprint': "6B36FBFC86FB1C019EB6496494B9195E6D179DDB",
    'certificate_path': '{0}/selfsigncert.pem'.format(os.path.dirname(__file__))
}


def acquire_token():
    authority_url = 'https://login.microsoftonline.com/{0}'.format(settings.get('tenant'))
    auth_ctx = adal.AuthenticationContext(authority_url)
    with open(cert_settings['certificate_path'], 'r') as file:
        key = file.read()
    json_token = auth_ctx.acquire_token_with_client_certificate(
        settings.get('url'),
        cert_settings['client_id'],
        key,
        cert_settings['thumbprint'])
    return TokenResponse(**json_token)


ctx = ClientContext(settings['url']).with_access_token(acquire_token)
current_web = ctx.web.get().execute_query()
print("{0}".format(current_web.url))
