"""
Get free/busy schedule of Outlook calendar users and resources

https://learn.microsoft.com/en-us/graph/outlook-get-free-busy-schedule


The following example gets the availability information for user for the specified date, time, and time zone.
"""

from datetime import datetime, timedelta

from office365.graph_client import GraphClient
from tests import (
    test_client_id,
    test_password,
    test_tenant,
    test_user_principal_name,
    test_username,
)

client = GraphClient.with_username_and_password(
    test_tenant, test_client_id, test_username, test_password
)
start_time = datetime.utcnow()
end_time = start_time + timedelta(days=1)
result = client.me.calendar.get_schedule(
    [test_user_principal_name], start_time, end_time
).execute_query()
for item in result.value:
    print(item.availabilityView)
