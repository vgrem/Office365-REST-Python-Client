"""
Demonstrates how to get taxonomy field value
"""

import sys

from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
custom_list = ctx.web.lists.get_by_title("Requests")
list_items = custom_list.items.get().execute_query()
if len(list_items) == 0:
    sys.exit("No list items were found.")

tax_field_value = list_items[0].get_property("Country")
tax_field_multi_value = list_items[0].get_property("Countries")
print(tax_field_value["TermGuid"])
print(tax_field_multi_value[0]["TermGuid"])
