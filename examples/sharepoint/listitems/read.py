"""
This common way of retrieving List Items from a List, only the default properties are getting returned

Official documentation:
https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/working-with-lists-and-list-items-with-rest#working-with-list-items-by-using-rest
"""

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

list_title = "Company Tasks"
ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
tasks_list = ctx.web.lists.get_by_title(list_title)
items = tasks_list.items.get().execute_query()
for item in items:
    print("{0}".format(item.properties.get("Title")))
