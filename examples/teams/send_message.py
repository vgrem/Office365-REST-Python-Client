import sys

from office365.graph_client import GraphClient
from office365.outlook.mail.itemBody import ItemBody
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
my_teams = client.me.joined_teams.get().execute_query()
if len(my_teams) == 0:
    sys.exit("No teams found")

target_team = my_teams[1]

item_body = ItemBody("Hello world!")
message = target_team.primary_channel.messages.add(item_body).execute_query()
print(message.web_url)
