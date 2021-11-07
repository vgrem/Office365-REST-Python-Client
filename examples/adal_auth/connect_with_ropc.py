from office365.graph_client import GraphClient
from tests import load_settings


def get_token_for_user():
    import adal
    settings = load_settings()
    authority_url = 'https://login.microsoftonline.com/{0}'.format(settings['default']['tenant'])
    auth_ctx = adal.AuthenticationContext(authority_url)
    token = auth_ctx.acquire_token_with_username_password(
        'https://graph.microsoft.com',
        settings['user_credentials']['username'],
        settings['user_credentials']['password'],
        settings['client_credentials']['client_id'])
    return token


client = GraphClient(get_token_for_user)
me = client.me.get().execute_query()
print(me.properties('displayName'))
