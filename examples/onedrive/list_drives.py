import msal

from office365.graph_client import GraphClient
from office365.onedrive.drives.drive import Drive
from tests import settings


def acquire_token_func():
    """
    Acquire token via MSAL
    """
    authority_url = 'https://login.microsoftonline.com/{0}'.format(settings.get('default', 'tenant'))
    app = msal.ConfidentialClientApplication(
        authority=authority_url,
        client_id=settings.get('client_credentials', 'client_id'),
        client_credential=settings.get('client_credentials', 'client_secret')
    )
    token = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    return token


client = GraphClient(acquire_token_func)
drives = client.drives.get().execute_query()
for drive in drives:  # type: Drive
    print("Drive url: {0}".format(drive.web_url))
