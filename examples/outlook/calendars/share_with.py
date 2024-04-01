"""
Create calendar permission

Demonstrates how to share my calendar with another user

https://learn.microsoft.com/en-us/graph/api/calendar-post-calendarpermissions?view=graph-rest-1.0
"""
from office365.graph_client import GraphClient
from office365.outlook.calendar.role_type import CalendarRoleType
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient.with_username_and_password(
    test_tenant, test_client_id, test_username, test_password
)

cal_perm = client.me.calendar.calendar_permissions.add(
    "samanthab@adatum.onmicrosoft.com", CalendarRoleType.read
).execute_query()
print(cal_perm)
