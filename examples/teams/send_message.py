from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
teams_result = client.me.joined_teams.get().execute_query()
if len(teams_result) > 0:
    target_team = teams_result[1]

    messages = target_team.primary_channel.messages.get().execute_query()
    print(messages)

    # item_body = ItemBody("Hello world!")
    # message = target_team.primaryChannel.messages.add(item_body).execute_query()
    # print(message.web_url)
