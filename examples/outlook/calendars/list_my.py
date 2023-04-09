from examples import acquire_token_by_username_password
from office365.graph_client import GraphClient
from office365.outlook.calendar.calendar import Calendar

client = GraphClient(acquire_token_by_username_password)
calendars = client.me.calendars.top(10).get().execute_query()
for cal in calendars:  # type: Calendar
    print(cal.name)
