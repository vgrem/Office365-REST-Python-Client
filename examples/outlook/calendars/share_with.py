"""
Create calendar permission

Demonstrates how to share my calendar with another user

https://learn.microsoft.com/en-us/graph/api/calendar-post-calendarpermissions?view=graph-rest-1.0
"""
from office365.graph_client import GraphClient
from office365.outlook.calendar.role_type import CalendarRoleType
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
my_cal = client.me.calendar
cal_perm = my_cal.calendar_permissions.add(
    "samanthab@adatum.onmicrosoft.com", CalendarRoleType.read
).execute_query()
print(cal_perm)
