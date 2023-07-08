import os

import msal

from tests import load_settings

settings = load_settings()

# aliases
sample_client_id = settings.get('client_credentials', 'client_id')
sample_client_secret = settings.get('client_credentials', 'client_secret')
sample_user_principal_name = settings.get('users', 'test_user1')
sample_user_principal_name_alt = settings.get('users', 'test_user2')
sample_tenant_prefix = settings.get('default', 'tenant_prefix')
sample_tenant_name = settings.get('default', 'tenant')
sample_thumbprint = settings.get('certificate_credentials', 'thumbprint')
sample_cert_path = '{0}/selfsigncert.pem'.format(os.path.dirname(__file__))
sample_site_url = settings.get('default', 'site_url')
sample_username = settings.get('user_credentials', "username")
sample_password = settings.get('user_credentials', "password")


def acquire_token_by_username_password():
    authority_url = 'https://login.microsoftonline.com/{0}'.format(sample_tenant_name)
    app = msal.PublicClientApplication(
        authority=authority_url,
        client_id=sample_client_id
    )
    return app.acquire_token_by_username_password(username=settings.get('user_credentials', "username"),
                                                  password=settings.get('user_credentials', "password"),
                                                  scopes=["https://graph.microsoft.com/.default"])

