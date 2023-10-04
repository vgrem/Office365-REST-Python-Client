"""
Get free/busy schedule of Outlook calendar users and resources

https://learn.microsoft.com/en-us/graph/outlook-get-free-busy-schedule


The following example gets the availability information for user for the specified date, time, and time zone.
"""

import json
from datetime import datetime, timedelta

from office365.graph_client import GraphClient
from tests import test_user_principal_name
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
start_time = datetime.utcnow()
end_time = start_time + timedelta(days=1)
result = client.me.calendar.get_schedule(
    [test_user_principal_name], start_time, end_time
).execute_query()
print(json.dumps(result.value.to_json(), indent=4))
