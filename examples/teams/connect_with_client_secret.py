import msal

from settings import settings
from office365.graph_client import GraphClient


def acquire_token_msal():
    """
    Acquire token via MSAL

    """
    authority_url = 'https://login.microsoftonline.com/{0}'.format(settings['tenant'])
    app = msal.ConfidentialClientApplication(
        authority=authority_url,
        client_id=settings['client_credentials']['client_id'],
        client_credential=settings['client_credentials']['client_secret']
    )
    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    return result


client = GraphClient(settings['tenant'], acquire_token_msal)
teams = client.teams.get_all().execute_query()
for team in teams:
    print(team.id)
