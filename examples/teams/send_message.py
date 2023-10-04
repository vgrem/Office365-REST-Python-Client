"""
Send a new message in the specified channel or a chat.
https://learn.microsoft.com/en-us/graph/api/chatmessage-post?view=graph-rest-1.0&tabs=http
"""
import sys

from office365.graph_client import GraphClient
from office365.outlook.mail.item_body import ItemBody
from office365.teams.team import Team
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
my_teams = client.me.joined_teams.get().execute_query()
if len(my_teams) == 0:
    sys.exit("No teams found")

target_team = my_teams[1]  # type: Team

message = target_team.primary_channel.messages.add(
    itemBody=ItemBody("Hello world!")
).execute_query()
print(message.web_url)
