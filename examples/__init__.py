import msal

from tests import settings


def acquire_token_client_credentials():

    authority_url = 'https://login.microsoftonline.com/{0}'.format(settings.get('default', 'tenant'))
    app = msal.ConfidentialClientApplication(
        authority=authority_url,
        client_id=settings.get('client_credentials', 'client_id'),
        client_credential=settings.get('client_credentials', 'client_secret')
    )
    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    return result
