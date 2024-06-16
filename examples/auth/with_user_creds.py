"""
Username Password Authentication flow

https://github.com/AzureAD/microsoft-authentication-library-for-python/wiki/Username-Password-Authentication
"""
import msal

from office365.graph_client import GraphClient
from tests import test_client_id, test_tenant, test_user_credentials


def acquire_token():
    authority_url = "https://login.microsoftonline.com/{0}".format(test_tenant)
    app = msal.PublicClientApplication(
        authority=authority_url, client_id=test_client_id
    )

    result = app.acquire_token_by_username_password(
        username=test_user_credentials.userName,
        password=test_user_credentials.password,
        scopes=["https://graph.microsoft.com/.default"],
    )
    return result


client = GraphClient(acquire_token)
me = client.me.get().execute_query()
print(me.user_principal_name)
