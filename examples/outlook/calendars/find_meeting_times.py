"""
Find possible meeting times on the Outlook calendar

https://learn.microsoft.com/en-us/graph/findmeetingtimes-example
"""

from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
result = client.me.find_meeting_times().execute_query()
for suggestion in result.value.meetingTimeSuggestions:
    print(suggestion)
