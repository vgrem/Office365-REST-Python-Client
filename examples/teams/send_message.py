import msal

from office365.teams.itemBody import ItemBody
from settings import settings
from office365.graph_client import GraphClient


def acquire_token_by_username_password():
    """
    Acquire token via MSAL

    """
    authority_url = 'https://login.microsoftonline.com/{0}'.format(settings.get('tenant'))
    app = msal.PublicClientApplication(
        authority=authority_url,
        client_id=settings.get('client_credentials').get('client_id')
    )
    result = app.acquire_token_by_username_password(username=settings.get('user_credentials').get("username"),
                                                    password=settings.get('user_credentials').get("password"),
                                                    scopes=["https://graph.microsoft.com/.default"])
    return result


client = GraphClient(acquire_token_by_username_password)
teams_result = client.me.joinedTeams.get().execute_query()
if len(teams_result) > 0:
    target_team = teams_result[1]

    messages = target_team.primaryChannel.messages.get().execute_query()
    print(messages)

    #item_body = ItemBody("Hello world!")
    #message = target_team.primaryChannel.messages.add(item_body).execute_query()
    #print(message.web_url)
