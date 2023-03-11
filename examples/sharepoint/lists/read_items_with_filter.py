import datetime

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.listitems.listitem import ListItem
from tests import test_client_credentials, test_team_site_url


ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
list_title = "Site Pages"
site_pages = ctx.web.lists.get_by_title(list_title)
from_datetime = datetime.datetime(2022, 1, 20, 0, 0)
filter_text = "Created gt datetime'{0}'".format(from_datetime.isoformat())
include_fields = ["Created", "EncodedAbsUrl"]
items = site_pages.items.filter(filter_text).select(include_fields).get().execute_query()
print("Loaded items count: {0}".format(len(items)))
for index, item in enumerate(items):  # type: int, ListItem
    print("{0}: {1}".format(index, item.properties['EncodedAbsUrl']))
