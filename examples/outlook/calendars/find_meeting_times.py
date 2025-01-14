"""
Find possible meeting times on the Outlook calendar

https://learn.microsoft.com/en-us/graph/findmeetingtimes-example
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient(tenant=test_tenant).with_username_and_password(
    test_client_id, test_username, test_password
)
result = client.me.find_meeting_times().execute_query()
for suggestion in result.value.meetingTimeSuggestions:
    print(suggestion)
