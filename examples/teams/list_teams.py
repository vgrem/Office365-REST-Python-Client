import adal

from settings import settings
from office365.graph_client import GraphClient


def acquire_token():
    authority_url = 'https://login.microsoftonline.com/{0}'.format(settings['tenant'])
    auth_ctx = adal.AuthenticationContext(authority_url)
    token = auth_ctx.acquire_token_with_username_password(
        'https://graph.microsoft.com',
        settings['user_credentials']['username'],
        settings['user_credentials']['password'],
        settings['client_credentials']['client_id'])
    return token


client = GraphClient(settings['tenant'], acquire_token)
teams = client.teams.get_all().execute_query()
for team in teams:
    print(team.id)
