import msal

from tests import settings


def acquire_token_by_client_credentials():
    authority_url = 'https://login.microsoftonline.com/{0}'.format(settings.get('default', 'tenant'))
    app = msal.ConfidentialClientApplication(
        authority=authority_url,
        client_id=settings.get('client_credentials', 'client_id'),
        client_credential=settings.get('client_credentials', 'client_secret')
    )
    return app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])


def acquire_token_by_username_password():
    authority_url = 'https://login.microsoftonline.com/{0}'.format(settings.get('default', 'tenant'))
    app = msal.PublicClientApplication(
        authority=authority_url,
        client_id=settings.get('client_credentials', 'client_id')
    )
    return app.acquire_token_by_username_password(username=settings.get('user_credentials', "username"),
                                                  password=settings.get('user_credentials', "password"),
                                                  scopes=["https://graph.microsoft.com/.default"])
